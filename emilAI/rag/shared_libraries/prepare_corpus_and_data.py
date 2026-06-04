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
import tempfile

import requests
import vertexai
from dotenv import load_dotenv, set_key
from google.api_core.exceptions import ResourceExhausted
from google.auth import default
from vertexai.preview import rag

# --- Please fill in your configurations ---
# Load environment variables from .env file
# Try finding .env in the current working directory first (e.g. scaffolded project)
cwd_env = os.path.join(os.getcwd(), ".env")
if os.path.exists(cwd_env):
    ENV_FILE_PATH = cwd_env
else:
    ENV_FILE_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    )
load_dotenv(ENV_FILE_PATH)

# Retrieve the PROJECT_ID from the environmental variables.
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise ValueError(
        "GOOGLE_CLOUD_PROJECT environment variable not set. Please set it in your .env file."
    )
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
if not LOCATION:
    raise ValueError(
        "GOOGLE_CLOUD_LOCATION environment variable not set. Please set it in your .env file."
    )
CORPUS_DISPLAY_NAME = "papeleria_corpus"
CORPUS_DESCRIPTION = "Informacion de la papeleria: tipo/tamaños de caja de pizza, tipo/tamaño de papel"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PDF_FILENAME = "Guia_Cajas_Pizza_y_Empanadas_ACTUALIZADA.pdf"
LOCAL_PDF_PATH = os.path.join(PROJECT_ROOT, PDF_FILENAME)




# --- Start of the script ---
def initialize_vertex_ai():
    credentials, _ = default()
    vertexai.init(
        project=PROJECT_ID, location=LOCATION, credentials=credentials
    )


def create_or_get_corpus():
    """Creates a new corpus or retrieves an existing one."""
    embedding_model_config = rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-004"
    )
    existing_corpora = rag.list_corpora()
    corpus = None
    for existing_corpus in existing_corpora:
        if existing_corpus.display_name == CORPUS_DISPLAY_NAME:
            corpus = existing_corpus
            print(
                f"Found existing corpus with display name '{CORPUS_DISPLAY_NAME}'"
            )
            break
    if corpus is None:
        corpus = rag.create_corpus(
            display_name=CORPUS_DISPLAY_NAME,
            description=CORPUS_DESCRIPTION,
            embedding_model_config=embedding_model_config
        
        )
        print(f"Created new corpus with display name '{CORPUS_DISPLAY_NAME}'")
    return corpus


def download_pdf_from_url(url, output_path):
    """Downloads a PDF file from the specified URL."""
    print(f"Downloading PDF from {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for HTTP errors

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"PDF downloaded successfully to {output_path}")
    return output_path


def upload_pdf_to_corpus(corpus_name, pdf_path, display_name, description):
    """Uploads a PDF file to the specified corpus."""
    print(f"Uploading {display_name} to corpus...")
    try:
        rag_file = rag.upload_file(
            corpus_name=corpus_name,
            path=pdf_path,
            display_name=display_name,
            description=description,
        )
        print(f"Successfully uploaded {display_name} to corpus")
        return rag_file
    except ResourceExhausted as e:
        print(f"Error uploading file {display_name}: {e}")
        print(
            "\nThis error suggests that you have exceeded the API quota for the embedding model."
        )
        print("This is common for new Google Cloud projects.")
        print(
            "Please see the 'Troubleshooting' section in the README.md for instructions on how to request a quota increase."
        )
        return None
    except Exception as e:
        print(f"Error uploading file {display_name}: {e}")
        return None


def update_env_file(corpus_name, env_file_path):
    """Updates the .env file with the corpus name."""
    try:
        set_key(env_file_path, "RAG_CORPUS", corpus_name)
        print(f"Updated RAG_CORPUS in {env_file_path} to {corpus_name}")
    except Exception as e:
        print(f"Error updating .env file: {e}")


def list_corpus_files(corpus_name):
    """Lists files in the specified corpus."""
    files = list(rag.list_files(corpus_name=corpus_name))
    print(f"Total files in corpus: {len(files)}")
    for file in files:
        print(f"File: {file.display_name} - {file.name}")


def main():
      initialize_vertex_ai()
      corpus = create_or_get_corpus()

      # Update the .env file with the corpus name
      update_env_file(corpus.name, ENV_FILE_PATH)

      # Verificar que el PDF local exista antes de subirlo
      if not os.path.exists(LOCAL_PDF_PATH):
          raise FileNotFoundError(
              f"No encontre el PDF en: {LOCAL_PDF_PATH}. "
              f"Verifica que el archivo este en la raiz de ~/emil-ai y que el nombre coincida."
          )

      # Subir el PDF local de la papeleria al corpus
      upload_pdf_to_corpus(
          corpus_name=corpus.name,
          pdf_path=LOCAL_PDF_PATH,
          display_name=PDF_FILENAME,
          description="Informacion de la papeleria",
      )

      # List all files in the corpus
      list_corpus_files(corpus_name=corpus.name)


if __name__ == "__main__":
    main()
