import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer

# Load credentials from .env file
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Initialize the NLP model for GraphRAG embeddings
print("Loading SentenceTransformer model (this will download ~120MB the first time)...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

class AegisNetGraphBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()

    def _execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            # return list of dictionaries if there are records, otherwise empty list
            return [record.data() for record in result]

    def clear_database(self):
        print("Clearing existing database...")
        self._execute_query("MATCH (n) DETACH DELETE n")

    def setup_schema_and_indexes(self):
        print("Setting up graph schema and vector indexes...")
        
        # Constraints
        constraints = [
            "CREATE CONSTRAINT server_id IF NOT EXISTS FOR (s:Server) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT subnet_name IF NOT EXISTS FOR (s:Subnet) REQUIRE s.name IS UNIQUE",
            "CREATE CONSTRAINT cve_id IF NOT EXISTS FOR (c:CVE) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT malware_name IF NOT EXISTS FOR (m:MalwareFamily) REQUIRE m.name IS UNIQUE"
        ]
        
        for c in constraints:
            self._execute_query(c)

        # Vector Index for GraphRAG (Neo4j 5.x syntax)
        # We drop it first in case it exists from a previous run
        self._execute_query("DROP INDEX cve_embeddings IF EXISTS")
        self._execute_query("""
            CREATE VECTOR INDEX cve_embeddings IF NOT EXISTS
            FOR (c:CVE) ON (c.embedding)
            OPTIONS {indexConfig: {
              `vector.dimensions`: 384,
              `vector.similarity_function`: 'cosine'
            }}
        """)

    def build_mock_corporate_network(self):
        print("Building virtual corporate network...")
        
        # 1. Create Subnets
        self._execute_query("CREATE (:Subnet {name: 'DMZ', risk_level: 'High'})")
        self._execute_query("CREATE (:Subnet {name: 'Internal', risk_level: 'Low'})")
        self._execute_query("CREATE (:Subnet {name: 'Database', risk_level: 'Critical'})")
        
        # 2. Create Servers and assign to Subnets
        servers = [
            {"id": "Web-01", "os": "Linux", "subnet": "DMZ"},
            {"id": "Mail-01", "os": "Windows", "subnet": "DMZ"},
            {"id": "App-01", "os": "Linux", "subnet": "Internal"},
            {"id": "App-02", "os": "Windows", "subnet": "Internal"},
            {"id": "DB-Primary", "os": "Linux", "subnet": "Database"},
        ]
        
        for s in servers:
            self._execute_query("""
                MATCH (sub:Subnet {name: $subnet})
                CREATE (srv:Server {id: $id, os: $os})-[:BELONGS_TO]->(sub)
            """, parameters=s)

        # 3. Create Lateral Movement Paths (Network Connectivity)
        # DMZ can talk to Internal. Internal can talk to Database.
        self._execute_query("""
            MATCH (dmz:Server)-[:BELONGS_TO]->(:Subnet {name: 'DMZ'})
            MATCH (int:Server)-[:BELONGS_TO]->(:Subnet {name: 'Internal'})
            CREATE (dmz)-[:CAN_REACH]->(int)
        """)
        self._execute_query("""
            MATCH (int:Server)-[:BELONGS_TO]->(:Subnet {name: 'Internal'})
            MATCH (db:Server)-[:BELONGS_TO]->(:Subnet {name: 'Database'})
            CREATE (int)-[:CAN_REACH]->(db)
        """)

    def inject_vulnerabilities(self):
        print("Injecting Vulnerabilities and generating Vector Embeddings...")
        
        cves = [
            {
                "id": "CVE-2021-44228",
                "description": "Log4Shell vulnerability allowing remote code execution in Apache Log4j. High risk for lateral movement.",
                "affected_os": "Linux"
            },
            {
                "id": "CVE-2017-0144",
                "description": "EternalBlue SMBv1 vulnerability allowing remote code execution. Historically used by WannaCry and Allaple.",
                "affected_os": "Windows"
            }
        ]
        
        for cve in cves:
            # Generate the embedding vector mathematically
            embedding = embedding_model.encode(cve["description"]).tolist()
            
            # Create CVE node and link it to servers with the affected OS
            self._execute_query("""
                CREATE (c:CVE {id: $id, description: $desc, embedding: $emb})
                WITH c
                MATCH (s:Server {os: $os})
                CREATE (s)-[:HAS_VULNERABILITY]->(c)
            """, parameters={"id": cve["id"], "desc": cve["description"], "emb": embedding, "os": cve["affected_os"]})

    def inject_malware_families(self):
        print("Mapping Malware Families to vulnerabilities...")
        
        # Link the malware from Phase 2 to vulnerabilities it exploits
        self._execute_query("""
            CREATE (m:MalwareFamily {name: 'Allaple.L'})
            WITH m
            MATCH (c:CVE {id: 'CVE-2017-0144'})
            CREATE (m)-[:EXPLOITS]->(c)
        """)
        
        self._execute_query("""
            CREATE (m:MalwareFamily {name: 'Mirai'})
            WITH m
            MATCH (c:CVE {id: 'CVE-2021-44228'})
            CREATE (m)-[:EXPLOITS]->(c)
        """)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AegisNet Phase 3: Neo4j Graph Builder")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompt (DANGEROUS: wipes entire database)")
    args = parser.parse_args()
    
    if not NEO4J_URI or NEO4J_URI == "neo4j+s://<YOUR_AURA_ID>.databases.neo4j.io":
        print("ERROR: Please set your Neo4j Aura credentials in the .env file.")
        exit(1)
    
    print(f"Connecting to Neo4j database at {NEO4J_URI}...")
    
    if not args.force:
        print("\n⚠️  WARNING: This will PERMANENTLY DELETE all existing data in your Neo4j database.")
        print(f"   Target: {NEO4J_URI}")
        confirm = input("   Type 'yes' to proceed: ").strip().lower()
        if confirm != "yes":
            print("Aborted. No changes were made.")
            exit(0)
    
    try:
        builder = AegisNetGraphBuilder(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
        builder.clear_database()
        builder.setup_schema_and_indexes()
        builder.build_mock_corporate_network()
        builder.inject_vulnerabilities()
        builder.inject_malware_families()
        builder.close()
        print("\nSUCCESS: Phase 3 Graph Database Successfully Built!")
        print("You can now open the Neo4j Aura console to explore the network graph visually.")
    except Exception as e:
        print(f"\nERROR: Could not connect or execute queries. Details: {e}")

