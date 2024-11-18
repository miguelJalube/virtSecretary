import os
import sys
import logging
from flask import Flask, request, jsonify, render_template, stream_with_context, Response

from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.memory import ChatMemoryBuffer

import logging

from llama_index.core import (
    load_index_from_storage,
    StorageContext,
)

# Set up logging
logger = logging.getLogger(__name__)

LLM = os.environ.get("LLM", "llama3.2:1b")
LLM_SERVER = os.environ.get("LLM_SERVER", "http://ollama:11434")
PORT = os.environ.get("PORT", 8071)
EMBED_MODEL = os.environ.get("EMBED_MODEL", "intfloat/multilingual-e5-large")

# Initialize Flask application
app = Flask(__name__)


# Index the data
@app.route("/index")
def index():
    # print content of current dir
    logging.warning("List dir : ")
    logging.warning(os.listdir())
    
    
    reader = SimpleDirectoryReader(input_dir="src/knowledge")
    documents = reader.load_data()
    
    index = VectorStoreIndex.from_documents(
        documents, show_progress=True, 
    )
    
    # save index to disk
    index.set_index_id("vector_index")
    index.storage_context.persist("src/storage")
    
    return jsonify({"message": "Indexing complete"})

# Chat route for handling POST requests with user queries
@app.route("/chat", methods=["POST"])
def chat():
    # rebuild storage context
    storage_context = StorageContext.from_defaults(
        persist_dir="src/storage"
    )
    
    try:
        # load index
        index = load_index_from_storage(
            storage_context,
            index_id="vector_index"
        )
    except Exception as e:
        message = f"Error loading index: {str(e)}"
        logging.error(message)
    
    data = request.get_json()
    
    memory = ChatMemoryBuffer.from_defaults(token_limit=1500)
    
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        memory = memory
    )
    logger.warning("Data : " + str(data["query"]))
    
    streaming_response = chat_engine.stream_chat(data["query"])
    
    # Use LlamaIndex to stream a response
    return Response(stream_with_context(streaming_response.response_gen), content_type="application/json")

# Home route to serve the frontend interface
@app.route("/")
def home():
    logging.info("Rendering home page")
    return render_template("index.html")

if __name__ == "__main__":
    
    # Get system prompt from prompts/system_prompt
    with open("src/prompts/system_prompt", "r") as f:
        system_prompt = f.read()
    
    # Initialize LlamaIndex
    Settings.llm = Ollama(base_url=LLM_SERVER, model=LLM, request_timeout=240, system_prompt=system_prompt)
    
    # Embedding model
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=EMBED_MODEL,
        trust_remote_code=True,
        cache_folder="cache"
    )
    
    app.run(debug=True, host="0.0.0.0", port=PORT)
