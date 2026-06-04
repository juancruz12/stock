import vertexai
from google.auth import default
from vertexai.preview import rag

PROJECT_ID = "project-76b5e515-21a1-4a89-82f"
LOCATION = "us-central1"

credentials, _ = default()
vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)

config_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
new_config = rag.RagEngineConfig(
    name=config_name,
    rag_managed_db_config=rag.RagManagedDbConfig(mode=rag.Serverless()),
)
result = rag.rag_data.update_rag_engine_config(rag_engine_config=new_config)
print("RAG Engine actualizado a Serverless:", result)