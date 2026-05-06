"""
backend/mcp/drive.py
--------------------
Google Drive MCP integration for saving grant applications
and reading organization documents.
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from backend.config import settings
from datetime import datetime
import os
import json
import io

SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.readonly'
]

class DriveMCP:
    def __init__(self):
        """Initialize the DriveMCP instance with basic properties."""
        self.service = None
        self.credentials_file = "credentials.json"
        self.token_file = "drive_token.json"
        self.root_folder_name = "Spriva AI"
        self.root_folder_id = None

    def authenticate(self) -> bool:
        """
        Authenticate with the Google Drive API.
        Checks if drive_token.json exists, loads/refreshes credentials,
        and builds the drive service.
        Returns True on success, False on failure.
        """
        creds = None
        try:
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('drive', 'v3', credentials=creds)
            return True
        except Exception as e:
            print(f"Failed to authenticate with Google Drive API: {e}")
            return False

    def get_or_create_folder(self, folder_name: str, parent_id: str = None) -> str:
        """
        Search for an existing folder with the given name (and parent if specified).
        If not found, creates it.
        Returns the folder_id.
        """
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            response = self.service.files().list(
                q=query, spaces='drive', fields='files(id, name)'
            ).execute()
            files = response.get('files', [])
            
            if files:
                return files[0].get('id')
                
            # Create folder if it doesn't exist
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]
                
            folder = self.service.files().create(
                body=file_metadata, fields='id'
            ).execute()
            return folder.get('id')
        except Exception as e:
            print(f"Error in get_or_create_folder for '{folder_name}': {e}")
            return None

    def save_application(self, org_name: str, grant_title: str,
                         funder_name: str, application_content: dict) -> dict:
        """
        Creates the folder structure: Spriva AI/{org_name}/{grant_title} — {funder_name}/
        Converts application_content dict to formatted text and saves three files:
        - application_draft.txt
        - eligibility_score.txt
        - research_notes.txt
        """
        try:
            # 1. Create root folder
            if not self.root_folder_id:
                self.root_folder_id = self.get_or_create_folder(self.root_folder_name)
                
            # 2. Create org folder
            org_folder_id = self.get_or_create_folder(org_name, self.root_folder_id)
            
            # 3. Create grant folder
            grant_folder_name = f"{grant_title} — {funder_name}"
            grant_folder_id = self.get_or_create_folder(grant_folder_name, org_folder_id)
            
            # 4. Get the folder webViewLink
            folder = self.service.files().get(
                fileId=grant_folder_id, fields='webViewLink'
            ).execute()
            drive_link = folder.get('webViewLink')

            # 5. Format application_content dictionary to text
            draft_text = ""
            for section, content in application_content.items():
                title = str(section).replace('_', ' ').title()
                if isinstance(content, list):
                    content_str = "\n".join([f"- {item}" for item in content])
                else:
                    content_str = str(content)
                draft_text += f"{title}\n{'-'*30}\n{content_str}\n\n"

            # 6. Prepare files to create
            files_to_create = {
                'application_draft.txt': draft_text,
                'eligibility_score.txt': "Pending eligibility score.",
                'research_notes.txt': "Pending research notes."
            }
            
            created_files = []
            
            # 7. Upload each file using MediaInMemoryUpload
            for filename, text_content in files_to_create.items():
                media = MediaInMemoryUpload(
                    text_content.encode('utf-8'), 
                    mimetype='text/plain', 
                    resumable=False
                )
                
                # Check if file already exists to overwrite it, avoiding duplicates
                file_query = f"name='{filename}' and '{grant_folder_id}' in parents and trashed=false"
                file_res = self.service.files().list(q=file_query, spaces='drive', fields='files(id)').execute()
                
                if file_res.get('files'):
                    # Update existing file
                    file_id = file_res.get('files')[0].get('id')
                    updated_file = self.service.files().update(
                        fileId=file_id, media_body=media, fields='id, name'
                    ).execute()
                    created_files.append(updated_file.get('name'))
                else:
                    # Create new file
                    file_metadata = {
                        'name': filename,
                        'parents': [grant_folder_id]
                    }
                    new_file = self.service.files().create(
                        body=file_metadata, media_body=media, fields='id, name'
                    ).execute()
                    created_files.append(new_file.get('name'))
                
            return {
                "status": "saved", 
                "folder": grant_folder_name,
                "files_created": created_files,
                "folder_id": grant_folder_id,
                "drive_link": drive_link
            }
        except Exception as e:
            print(f"Error saving application: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }

    def read_org_documents(self, folder_name: str = "Org Documents") -> list:
        """
        Search Drive for PDF files in the specified folder (for Document Intake Agent).
        Returns a list of dicts with file metadata.
        """
        try:
            # Find the target folder by name
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            response = self.service.files().list(
                q=query, spaces='drive', fields='files(id, name)'
            ).execute()
            folders = response.get('files', [])
            
            if not folders:
                return []
                
            folder_id = folders[0].get('id')
            
            # Find all PDFs within that folder
            pdf_query = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
            pdf_response = self.service.files().list(
                q=pdf_query, spaces='drive', fields='files(id, name, createdTime, webViewLink)'
            ).execute()
            
            pdfs = pdf_response.get('files', [])
            
            # Return list of dicts
            return [
                {
                    "file_id": pdf.get('id'),
                    "name": pdf.get('name'),
                    "created_time": pdf.get('createdTime'),
                    "web_view_link": pdf.get('webViewLink')
                } for pdf in pdfs
            ]
        except Exception as e:
            print(f"Error reading org documents: {e}")
            return []

    def list_grant_folders(self, org_name: str) -> list:
        """
        Lists all grant research folders for a specific organization.
        Searches under Spriva AI/{org_name}/
        """
        try:
            # 1. Get root folder
            if not self.root_folder_id:
                root_query = f"name='{self.root_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                root_res = self.service.files().list(q=root_query, spaces='drive', fields='files(id)').execute()
                if not root_res.get('files'):
                    return []
                self.root_folder_id = root_res.get('files')[0].get('id')

            # 2. Get org folder
            org_query = f"name='{org_name}' and '{self.root_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            org_res = self.service.files().list(q=org_query, spaces='drive', fields='files(id)').execute()
            if not org_res.get('files'):
                return []
            org_folder_id = org_res.get('files')[0].get('id')
            
            # 3. List grant subfolders
            grant_query = f"'{org_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            grant_res = self.service.files().list(q=grant_query, spaces='drive', fields='files(id, name)').execute()
            
            return [
                {
                    "folder_id": f.get('id'), 
                    "name": f.get('name')
                } for f in grant_res.get('files', [])
            ]
        except Exception as e:
            print(f"Error listing grant folders: {e}")
            return []

    def save_research_notes(self, org_name: str, grant_title: str, notes: str) -> dict:
        """
        Saves eligibility reasoning and research notes as a text file 
        in the relevant grant folder.
        """
        try:
            # Setup hierarchy
            if not self.root_folder_id:
                self.root_folder_id = self.get_or_create_folder(self.root_folder_name)
            org_folder_id = self.get_or_create_folder(org_name, self.root_folder_id)
            
            # Since funder_name is not provided, search for any folder containing the grant_title
            # inside the org's folder.
            query = f"name contains '{grant_title}' and '{org_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            res = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
            
            if res.get('files'):
                grant_folder_id = res.get('files')[0].get('id')
            else:
                # Fallback: create a generic folder if it doesn't exist
                grant_folder_id = self.get_or_create_folder(f"{grant_title} — Research", org_folder_id)
                
            # Prepare file upload
            media = MediaInMemoryUpload(
                notes.encode('utf-8'), 
                mimetype='text/plain', 
                resumable=False
            )
            
            # Check if research_notes.txt already exists
            file_query = f"name='research_notes.txt' and '{grant_folder_id}' in parents and trashed=false"
            file_res = self.service.files().list(q=file_query, spaces='drive', fields='files(id)').execute()
            
            if file_res.get('files'):
                # Update existing
                file_id = file_res.get('files')[0].get('id')
                updated_file = self.service.files().update(
                    fileId=file_id, 
                    media_body=media, 
                    fields='id, name, webViewLink, createdTime'
                ).execute()
                return updated_file
            else:
                # Create new
                file_metadata = {
                    'name': 'research_notes.txt',
                    'parents': [grant_folder_id]
                }
                new_file = self.service.files().create(
                    body=file_metadata, 
                    media_body=media, 
                    fields='id, name, webViewLink, createdTime'
                ).execute()
                return new_file
                
        except Exception as e:
            print(f"Error saving research notes: {e}")
            return {}

# Instantiate the DriveMCP at the bottom of the module
drive_mcp = DriveMCP()
