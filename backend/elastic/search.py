from elasticsearch import Elasticsearch, helpers
from backend.config import settings
from datetime import datetime, timedelta
import json
import uuid

# Create Elasticsearch client at module level
client = Elasticsearch(
    settings.ELASTIC_ENDPOINT,
    api_key=settings.ELASTIC_API_KEY
)

INDEX_NAME = "spriva-grants"

# Define the grants index mapping
GRANTS_MAPPING = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "title": {
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "funder": {
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "funder_type": {"type": "keyword"},
            "amount_min": {"type": "integer"},
            "amount_max": {"type": "integer"},
            "amount_text": {"type": "text"},
            "deadline": {"type": "date", "format": "yyyy-MM-dd||yyyy/MM/dd||basic_date"},
            "focus_areas": {"type": "keyword"},
            "location_requirement": {"type": "keyword"},
            "description": {"type": "text"},
            "application_url": {"type": "keyword"},
            "requirements": {"type": "text"},
            "indexed_at": {"type": "date"}
        }
    }
}

class ElasticGrantSearch:
    def __init__(self):
        self.client = client
        self.index = INDEX_NAME

    def setup_index(self) -> bool:
        """
        Check if index exists, create it with GRANTS_MAPPING if not.
        Returns True on success, False on failure.
        """
        try:
            if not self.client.indices.exists(index=self.index):
                self.client.indices.create(index=self.index, body=GRANTS_MAPPING)
                print(f"Elastic index created: {self.index}")
            else:
                print("Elastic index already exists")
            return True
        except Exception as e:
            print(f"Error setting up Elastic index: {e}")
            return False

    def index_grant(self, grant: dict) -> bool:
        """
        Index a single grant document.
        Adds indexed_at timestamp and uses the grant id as the document id.
        """
        try:
            doc_id = grant.get("id")
            if not doc_id:
                doc_id = str(uuid.uuid4())
                grant["id"] = doc_id
                
            grant["indexed_at"] = datetime.now().isoformat()
            
            self.client.index(index=self.index, id=doc_id, document=grant)
            return True
        except Exception as e:
            print(f"Error indexing grant: {e}")
            return False

    def index_grants_batch(self, grants: list) -> dict:
        """
        Index a list of grants using bulk indexing.
        """
        try:
            actions = []
            for grant in grants:
                doc_id = grant.get("id")
                if not doc_id:
                    doc_id = str(uuid.uuid4())
                    grant["id"] = doc_id
                    
                grant["indexed_at"] = datetime.now().isoformat()
                
                actions.append({
                    "_index": self.index,
                    "_id": doc_id,
                    "_source": grant
                })
            
            success, failed = helpers.bulk(self.client, actions, stats_only=True)
            return {"indexed": success, "failed": failed, "status": "ok"}
        except Exception as e:
            print(f"Error in batch indexing: {e}")
            return {"indexed": 0, "failed": len(grants), "status": "error"}

    def search_grants(self, org_profile: dict) -> list:
        """
        Main search method. Builds a multi-match query using org_profile fields.
        Excludes past deadlines and returns the top 10 results.
        """
        try:
            mission = org_profile.get("mission", "")
            focus_areas = org_profile.get("focus_areas", "")
            location = org_profile.get("location", "")
            
            # Prepare focus_areas as a list of terms
            if isinstance(focus_areas, str):
                focus_areas_list = [f.strip() for f in focus_areas.split(',')] if focus_areas else []
            else:
                focus_areas_list = focus_areas or []

            now_str = datetime.now().strftime("%Y-%m-%d")

            query = {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": mission,
                                "fields": ["description", "requirements"],
                                "boost": 2
                            }
                        },
                        {
                            "match": {
                                "location_requirement": {
                                    "query": location,
                                    "boost": 1.5
                                }
                            }
                        }
                    ],
                    "minimum_should_match": 1,
                    "filter": [
                        {
                            "range": {
                                "deadline": {
                                    "gte": now_str
                                }
                            }
                        }
                    ]
                }
            }
            
            # Add terms query for focus_areas if we have any
            if focus_areas_list:
                query["bool"]["should"].append({
                    "terms": {
                        "focus_areas": focus_areas_list,
                        "boost": 3
                    }
                })

            response = self.client.search(
                index=self.index,
                query=query,
                size=10
            )

            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                source["elastic_score"] = hit["_score"]
                results.append(source)
                
            return results
        except Exception as e:
            print(f"Error in search_grants: {e}")
            return []

    def semantic_search(self, query_text: str, size: int = 6) -> list:
        """Simple full-text search across all grant fields."""
        try:
            query = {
                "multi_match": {
                    "query": query_text,
                    "fields": ["title", "description", "funder", "focus_areas", "requirements"]
                }
            }
            response = self.client.search(
                index=self.index,
                query=query,
                size=size
            )
            
            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                source["elastic_score"] = hit["_score"]
                results.append(source)
                
            return results
        except Exception as e:
            print(f"Error in semantic_search: {e}")
            return []

    def get_all_grants(self) -> list:
        """Returns all indexed grants."""
        try:
            query = {
                "match_all": {}
            }
            response = self.client.search(
                index=self.index,
                query=query,
                size=100
            )
            
            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                results.append(source)
                
            return results
        except Exception as e:
            print(f"Error in get_all_grants: {e}")
            return []

    def delete_index(self) -> bool:
        """Deletes the index (for testing/reset)."""
        try:
            if self.client.indices.exists(index=self.index):
                self.client.indices.delete(index=self.index)
            return True
        except Exception as e:
            print(f"Error deleting index: {e}")
            return False


def seed_sample_grants() -> list:
    """Creates 8 realistic sample grants and returns them as a list."""
    now = datetime.now()
    
    grants = [
        {
            "id": "g-usaid-001",
            "title": "Global Health & Education Innovation Fund",
            "funder": "USAID",
            "funder_type": "Government",
            "amount_min": 100000,
            "amount_max": 500000,
            "amount_text": "Up to $500,000",
            "deadline": (now + timedelta(days=60)).strftime("%Y-%m-%d"),
            "focus_areas": ["health", "education"],
            "location_requirement": "Global South",
            "description": "Funding innovative projects that improve access to both basic healthcare and primary education in underserved communities.",
            "application_url": "https://example.com/usaid-grants",
            "requirements": "Must be a registered NGO. Minimum 3 years of operations."
        },
        {
            "id": "g-gates-002",
            "title": "Rural Climate Resilience Initiative",
            "funder": "Gates Foundation",
            "funder_type": "Foundation",
            "amount_min": 50000,
            "amount_max": 250000,
            "amount_text": "$50,000 - $250,000",
            "deadline": (now + timedelta(days=90)).strftime("%Y-%m-%d"),
            "focus_areas": ["climate", "rural development"],
            "location_requirement": "Sub-Saharan Africa, South Asia",
            "description": "Supports local organizations building climate resilience in rural agriculture.",
            "application_url": "https://example.com/gates-climate",
            "requirements": "Demonstrated community engagement and measurable climate impact."
        },
        {
            "id": "g-unwomen-003",
            "title": "Women in Tech Leadership Grants",
            "funder": "UN Women",
            "funder_type": "UN Agency",
            "amount_min": 10000,
            "amount_max": 50000,
            "amount_text": "Up to $50,000",
            "deadline": (now + timedelta(days=120)).strftime("%Y-%m-%d"),
            "focus_areas": ["women empowerment", "technology"],
            "location_requirement": "Global",
            "description": "Providing seed funding for women-led tech startups and digital literacy programs for girls.",
            "application_url": "https://example.com/unwomen-tech",
            "requirements": "Organization must be at least 50% women-led."
        },
        {
            "id": "g-worldbank-004",
            "title": "Digital Infrastructure for Rural Areas",
            "funder": "World Bank",
            "funder_type": "International",
            "amount_min": 200000,
            "amount_max": 500000,
            "amount_text": "Up to $500,000",
            "deadline": (now + timedelta(days=180)).strftime("%Y-%m-%d"),
            "focus_areas": ["technology", "rural development"],
            "location_requirement": "Developing Nations",
            "description": "Grants to improve broadband connectivity and digital infrastructure in remote areas.",
            "application_url": "https://example.com/worldbank-digital",
            "requirements": "Partnership with local government required."
        },
        {
            "id": "g-ford-005",
            "title": "Civic Rights and Engagement Program",
            "funder": "Ford Foundation",
            "funder_type": "Foundation",
            "amount_min": 50000,
            "amount_max": 150000,
            "amount_text": "$50,000 - $150,000",
            "deadline": (now + timedelta(days=75)).strftime("%Y-%m-%d"),
            "focus_areas": ["human rights"],
            "location_requirement": "Global",
            "description": "Supporting grassroots movements that protect voting rights and civic space.",
            "application_url": "https://example.com/ford-civic",
            "requirements": "Clear track record of advocacy."
        },
        {
            "id": "g-opensociety-006",
            "title": "Justice and Human Rights Fellowship",
            "funder": "Open Society Foundations",
            "funder_type": "Foundation",
            "amount_min": 25000,
            "amount_max": 100000,
            "amount_text": "Up to $100,000",
            "deadline": (now + timedelta(days=150)).strftime("%Y-%m-%d"),
            "focus_areas": ["human rights", "education"],
            "location_requirement": "Eastern Europe, Latin America",
            "description": "Fellowships and project grants for human rights defenders and legal educators.",
            "application_url": "https://example.com/opensociety-justice",
            "requirements": "Proposal must include a public education component."
        },
        {
            "id": "g-wellcome-007",
            "title": "Mental Health Innovations in Low-Resource Settings",
            "funder": "Wellcome Trust",
            "funder_type": "Foundation",
            "amount_min": 100000,
            "amount_max": 300000,
            "amount_text": "$100,000 - $300,000",
            "deadline": (now + timedelta(days=100)).strftime("%Y-%m-%d"),
            "focus_areas": ["health"],
            "location_requirement": "LMICs (Low and Middle Income Countries)",
            "description": "Funding research and implementation of scalable mental health interventions.",
            "application_url": "https://example.com/wellcome-mentalhealth",
            "requirements": "Must involve community-based health workers."
        },
        {
            "id": "g-skoll-008",
            "title": "Social Entrepreneurship for Climate & Women",
            "funder": "Skoll Foundation",
            "funder_type": "Foundation",
            "amount_min": 150000,
            "amount_max": 400000,
            "amount_text": "Up to $400,000",
            "deadline": (now + timedelta(days=160)).strftime("%Y-%m-%d"),
            "focus_areas": ["climate", "women empowerment"],
            "location_requirement": "Global",
            "description": "Awards for social entrepreneurs creating intersectional solutions for climate change and gender equity.",
            "application_url": "https://example.com/skoll-award",
            "requirements": "Demonstrated proof of concept and scalable model."
        }
    ]
    return grants

elastic_search = ElasticGrantSearch()
