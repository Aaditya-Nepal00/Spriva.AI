"""
backend/agent/intake.py
-----------------------
Agent responsible for processing uploaded organization documents
(annual reports, past grant applications) to automatically build
and update the organization profile.
"""

from backend.agent.core import agent
from backend.agent.prompts import document_intake_prompt
from backend.mcp.drive import drive_mcp
import json
import re

class DocumentIntakeAgent:
    def __init__(self):
        self.agent = agent
        self.drive = drive_mcp
        self.supported_types = [
            "application/pdf",
            "text/plain", 
            "application/vnd.google-apps.document"
        ]

    async def process_uploaded_text(self, text: str, filename: str = "document") -> dict:
        """
        Takes raw text from a document and uses Gemini to extract 
        organization profile information.
        """
        try:
            prompt = document_intake_prompt(text)
            response = await self.agent.send_message(prompt)
            
            # Extract JSON object
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if not match:
                raise ValueError("No valid JSON found in Gemini response")
                
            extracted_data = json.loads(match.group())
            extracted_data["source_file"] = filename
            extracted_data["status"] = "success"
            
            return extracted_data
        except Exception as e:
            print(f"Error in document intake: {e}")
            return {
                "status": "error",
                "error_message": str(e),
                "source_file": filename
            }

    async def process_multiple_documents(self, documents: list) -> dict:
        """
        Processes multiple documents and merges the extracted information
        into a single coherent organization profile.
        """
        try:
            all_extracted = []
            for doc in documents:
                text = doc.get("text", "")
                filename = doc.get("filename", "unknown")
                result = await self.process_uploaded_text(text, filename)
                if result["status"] == "success":
                    all_extracted.append(result)
            
            if not all_extracted:
                return {"status": "error", "error_message": "No information could be extracted from documents."}
                
            # For simplicity in this demo, we'll ask Gemini to merge them
            merge_prompt = (
                f"Merge the following organization profile fragments into one single, "
                f"most accurate profile. Prioritize the most recent or detailed information.\n\n"
                f"Fragments:\n{json.dumps(all_extracted, indent=2)}\n\n"
                f"Return ONLY a JSON object with keys: org_name, mission, focus_areas, "
                f"location, budget_range, past_grants_won, key_programs, impact_metrics."
            )
            
            response = await self.agent.send_message(merge_prompt)
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if not match:
                # Fallback to first if merge fails
                return all_extracted[0]
                
            return json.loads(match.group())
            
        except Exception as e:
            print(f"Error in multiple document intake: {e}")
            return {"status": "error", "error_message": str(e)}

# Module-level singleton
intake_agent = DocumentIntakeAgent()
