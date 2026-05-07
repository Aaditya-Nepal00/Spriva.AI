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
            "funder_website": {"type": "keyword"},
            "funder_email": {"type": "keyword"},
            "funder_phone": {"type": "keyword"},
            "funder_twitter": {"type": "keyword"},
            "funder_linkedin": {"type": "keyword"},
            "program_officer": {"type": "text"},
            "application_portal": {"type": "keyword"},
            "funder_description": {"type": "text"},
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
            "application_url": "https://www.usaid.gov/work-usaid/get-grant-or-contract/opportunities-for-funding",
            "requirements": "Must be a registered NGO. Minimum 3 years of operations.",
            "funder_website": "https://www.usaid.gov",
            "funder_email": "open@usaid.gov",
            "funder_phone": "+1-202-712-4810",
            "funder_twitter": "@USAID",
            "funder_linkedin": "https://www.linkedin.com/company/usaid",
            "program_officer": "Administrator Samantha Power",
            "application_portal": "https://www.grants.gov",
            "funder_description": "USAID is the world's premier international development agency and a catalytic actor driving development results."
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
            "application_url": "https://www.gatesfoundation.org/How-We-Work/General-Information/Grant-Opportunities",
            "requirements": "Demonstrated community engagement and measurable climate impact.",
            "funder_website": "https://www.gatesfoundation.org",
            "funder_email": "info@gatesfoundation.org",
            "funder_phone": "+1-206-709-3100",
            "funder_twitter": "@gatesfoundation",
            "funder_linkedin": "https://www.linkedin.com/company/gates-foundation",
            "program_officer": "Mark Suzman (CEO)",
            "application_portal": "https://www.gatesfoundation.org/How-We-Work/General-Information/Grant-Opportunities",
            "funder_description": "The Bill & Melinda Gates Foundation works to help all people lead healthy, productive lives."
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
            "application_url": "https://www.unwomen.org/en/about-us/partnerships/trust-funds",
            "requirements": "Organization must be at least 50% women-led.",
            "funder_website": "https://www.unwomen.org",
            "funder_email": "unwomen.contact@unwomen.org",
            "funder_phone": "+1-646-781-4400",
            "funder_twitter": "@UN_Women",
            "funder_linkedin": "https://www.linkedin.com/company/un-women",
            "program_officer": "Sima Bahous (Executive Director)",
            "application_portal": "https://www.unwomen.org/en/about-us/partnerships/trust-funds",
            "funder_description": "UN Women is the United Nations entity dedicated to gender equality and the empowerment of women."
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
            "application_url": "https://www.worldbank.org/en/about/partners/grants",
            "requirements": "Partnership with local government required.",
            "funder_website": "https://www.worldbank.org",
            "funder_email": "philanthropy@worldbank.org",
            "funder_phone": "+1-202-473-1000",
            "funder_twitter": "@WorldBank",
            "funder_linkedin": "https://www.linkedin.com/company/the-world-bank",
            "program_officer": "Ajay Banga (President)",
            "application_portal": "https://www.worldbank.org/en/about/partners/grants",
            "funder_description": "The World Bank provides loans and grants to the governments of low- and middle-income countries for capital projects."
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
            "application_url": "https://www.fordfoundation.org/work/our-grants/",
            "requirements": "Clear track record of advocacy.",
            "funder_website": "https://www.fordfoundation.org",
            "funder_email": "office-of-communications@fordfoundation.org",
            "funder_phone": "+1-212-573-5000",
            "funder_twitter": "@FordFoundation",
            "funder_linkedin": "https://www.linkedin.com/company/ford-foundation",
            "program_officer": "Darren Walker (President)",
            "application_portal": "https://www.fordfoundation.org/work/our-grants/",
            "funder_description": "The Ford Foundation is a private foundation with the mission of advancing human welfare and social justice."
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
            "application_url": "https://www.opensocietyfoundations.org/grants",
            "requirements": "Proposal must include a public education component.",
            "funder_website": "https://www.opensocietyfoundations.org",
            "funder_email": "media@opensocietyfoundations.org",
            "funder_phone": "+1-212-548-0600",
            "funder_twitter": "@OpenSociety",
            "funder_linkedin": "https://www.linkedin.com/company/open-society-foundations",
            "program_officer": "Mark Malloch-Brown (President)",
            "application_portal": "https://www.opensocietyfoundations.org/grants",
            "funder_description": "OSF is the world's largest private funder of independent groups working for justice, democratic governance, and human rights."
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
            "application_url": "https://wellcome.org/grant-funding/schemes",
            "requirements": "Must involve community-based health workers.",
            "funder_website": "https://wellcome.org",
            "funder_email": "fundingsupport@wellcome.org",
            "funder_phone": "+44-20-7611-8888",
            "funder_twitter": "@wellcometrust",
            "funder_linkedin": "https://www.linkedin.com/company/wellcome-trust",
            "program_officer": "John-Arne Røttingen (CEO)",
            "application_portal": "https://wellcome.org/grant-funding/schemes",
            "funder_description": "Wellcome is a global charitable foundation that supports science to solve the urgent health challenges facing everyone."
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
            "application_url": "https://skoll.org/about/skoll-award/",
            "requirements": "Demonstrated proof of concept and scalable model.",
            "funder_website": "https://skoll.org",
            "funder_email": "info@skoll.org",
            "funder_phone": "+1-650-331-1031",
            "funder_twitter": "@SkollFoundation",
            "funder_linkedin": "https://www.linkedin.com/company/skoll-foundation",
            "program_officer": "Don Gips (CEO)",
            "application_portal": "https://skoll.org/about/skoll-award/",
            "funder_description": "The Skoll Foundation invests in social entrepreneurs and innovators who help solve the world's most pressing problems."
        }
    ]
    return grants

elastic_search = ElasticGrantSearch()
