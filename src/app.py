import os
import sys
import logging
from flask import Flask, redirect, request, jsonify, render_template, stream_with_context, Response

from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
    load_index_from_storage,
    StorageContext,
)
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.memory import ChatMemoryBuffer


import logging

# Set up logging
logger = logging.getLogger(__name__)

LLM =                   os.environ.get("LLM", "llama3.2:3b")
LLM_SERVER =            os.environ.get("LLM_SERVER", "host.docker.internal")
LLM_PORT =              os.environ.get("LLM_PORT", "11434")
PORT =                  os.environ.get("PORT", 8071)
LLAMA_CLOUD_API_KEY =   os.environ.get("LLAMA_CLOUD_API_KEY", "llama_cloud_api_key")
EMBED_MODEL =           os.environ.get("EMBED_MODEL", "intfloat/multilingual-e5-large")

# Initialize Flask application
app = Flask(__name__)

chat_engine = None

# Index the data
@app.route("/index")
def index():
    # bring in deps
    from llama_parse import LlamaParse
    
    # print content of current dir
    logging.warning("List dir : ")
    logging.warning(os.listdir())
    
    # set up parser
    parser = LlamaParse(
        result_type="markdown",
        api_key=LLAMA_CLOUD_API_KEY,
        
    )

    # use SimpleDirectoryReader to parse our file
    file_extractor = {".pdf": parser}

    documents = SimpleDirectoryReader(
        input_dir="src/knowledge", 
        recursive=True, 
        #file_extractor=file_extractor
    ).load_data()
    
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
    data = request.get_json()
    
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
    with open("src/prompts/system_prompt.txt", "r") as f:
        system_prompt = f.read()
    
    logger.warning("LLM Server : " + LLM_SERVER)
    
    url = f"http://{LLM_SERVER}:{LLM_PORT}"
    
    # Initialize LlamaIndex
    Settings.llm = Ollama(base_url=url, model=LLM, request_timeout=240, system_prompt=system_prompt)
    
    # Embedding model
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=EMBED_MODEL,
        trust_remote_code=True,
        cache_folder="cache"
    )
    
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
    
    memory = ChatMemoryBuffer.from_defaults(llm=Settings.llm, token_limit=1500)
    
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        memory = memory
    )
    
    app.run(debug=True, host="0.0.0.0", port=PORT)
