# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import uuid
import requests
import urllib.parse

import google.auth

from google.adk.tools import FunctionTool
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import (
    VertexAiRagRetrieval,
)
from openinference.instrumentation import using_session
from vertexai.preview import rag

from rag.tracing import instrument_adk_with_arize

from .prompts import return_instructions_root

load_dotenv()

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-west1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

_ = instrument_adk_with_arize()

# Initialize tools list
tools = []
# Instanciamos el cliente RAG de forma interna
rag_corpus = os.environ.get("RAG_CORPUS")

if rag_corpus:
    # 1. Instanciamos el cliente agregando 'name' y 'description' que son requeridos por su constructor
    rag_retrieval_client = VertexAiRagRetrieval(
        name="retrieve_rag_documentation",
        description="Use this tool to retrieve documentation, measures, technical specifications and reference materials.",
        rag_resources=[rag.RagResource(rag_corpus=rag_corpus)],
        similarity_top_k=10,
        vector_distance_threshold=0.6,
    )
    
    # 2. Creamos la función envoltorio estándar de Python
    # Agregamos **kwargs o tool_context para recolectar el estado del framework
    async def retrieve_rag_documentation(query: str, tool_context=None, **kwargs) -> dict:
        """
        Use this tool to retrieve documentation, measures, technical specifications and 
        reference materials for the question from the RAG corpus.
        
        Args:
            query: The search term or question to look up in the catalog.
        """
        # Formateamos los argumentos exactos tal cual los espera VertexAiRagRetrieval
        # Nota: intentamos mandarle tanto 'query' como 'text' dentro del mapa interno
        args_for_rag = {"query": query, "text": query}
        
        if hasattr(rag_retrieval_client, "run_async"):
            return await rag_retrieval_client.run_async(
                args=args_for_rag, 
                tool_context=tool_context
            )
        
        return rag_retrieval_client.run(
            args=args_for_rag, 
            tool_context=tool_context
        )

    tools.append(retrieve_rag_documentation)

def get_stock_availability(product_name: str) -> dict:
    """Consulta el stock real y disponibilidad en el inventario.

    Args:
        product_name: El nombre o descripcion del producto a buscar.
    """
    api_url = os.environ.get("STOCK_API_URL", "https://stock-api-114519320182.us-central1.run.app").rstrip("/")
    
    try:
        encoded_name = urllib.parse.quote(product_name)
        url = f"{api_url}/stockByName/{encoded_name}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            return {"resultado": f"No se encontro informacion de stock para {product_name}."}
        
        # Estructura plana (Evita listas complejas u objetos anidados si da problemas)
        detalles = ""
        for item in data:
            nombre = item.get("stock_name") or item.get("name") or product_name
            cantidad = item.get("stock") or item.get("quantity") or "no especificada"
            detalles += f"Producto: {nombre}, Cantidad disponible: {cantidad}. "
            
        return {"resultado": detalles}

    except Exception as e:
        return {"error": f"Error al consultar inventario: {str(e)}"}

tools.append(FunctionTool(get_stock_availability))

root_agent = Agent(
    model="gemini-2.5-flash",
    name="ask_rag_agent",
    instruction=return_instructions_root(),
    tools=tools,
)

app = App(
    root_agent=root_agent,
    name="rag_agent",
)