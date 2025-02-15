import os
import sys
import logging
from flask import (
    Flask, 
    redirect, 
    request, 
    jsonify, 
    render_template, 
    stream_with_context, 
    Response
)
from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
)
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.memory import ChatMemoryBuffer
from sqlalchemy import make_url

import logging

# Activate INFO level logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Set up logging
logger = logging.getLogger(__name__)

LLM =                   os.environ.get("LLM", "llama3.2:3b")
LLM_SERVER =            os.environ.get("LLM_SERVER", "host.docker.internal")
LLM_PORT =              os.environ.get("LLM_PORT", "11434")
PORT =                  os.environ.get("PORT", 8071)
LLAMA_CLOUD_API_KEY =   os.environ.get("LLAMA_CLOUD_API_KEY", "llama_cloud_api_key")
EMBED_MODEL =           os.environ.get("EMBED_MODEL", "intfloat/multilingual-e5-large")
PG_USER =               os.environ.get("PG_USER", "postgres")
PG_PASSWORD =           os.environ.get("PG_PASSWORD", "password")
PG_HOST =               os.environ.get("PG_HOST", "katia_pgvector")
PG_PORT =               os.environ.get("PG_PORT", 5432)
PG_DB =                 os.environ.get("PG_DB", "katia_db")

# Initialize Flask application
app = Flask(__name__)

chat_engine = None
vector_store = None
memory = None

# Index the data
@app.route("/index")
def index():
    # bring in deps
    from llama_parse import LlamaParse
    
    # print content of current dir
    logger.info("List dir : ")
    logger.info(os.listdir())
    
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
    
    logger.info("vector_store load")
    global vector_store
    logger.info("vector_store loaded : " + str(vector_store))

    logger.info("storage_context load")
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    index_base = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, show_progress=True, 
    )
    
    return jsonify({"message": "Indexing complete"})

# Chat route for handling POST requests with user queries
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    
    logger.info("Data : " + str(data["query"]))
    
    memory = ChatMemoryBuffer.from_defaults(llm=Settings.llm, token_limit=1500)
    
    # load index_base
    index_base = VectorStoreIndex.from_vector_store(
        vector_store=vector_store
    )

    chat_engine = index_base.as_chat_engine(
        chat_mode="context",
        memory = memory
    )
    
    streaming_response = chat_engine.stream_chat(data["query"])
    
    # Use LlamaIndex to stream a response
    return Response(stream_with_context(streaming_response.response_gen), content_type="application/json")

# Home route to serve the frontend interface
@app.route("/")
def home():
    logger.info("Rendering home page")    
    return render_template("index.html")

if __name__ == "__main__":    
    # Get system prompt from prompts/system_prompt
    with open("src/prompts/system_prompt.txt", "r") as f:
        system_prompt = f.read()    
    
    # Initialize LlamaIndex
    Settings.llm = Ollama(
        base_url=f"http://{LLM_SERVER}:{LLM_PORT}",
        model=LLM, 
        request_timeout=240, 
        system_prompt=system_prompt
    )
    
    # Embedding model
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=EMBED_MODEL,
        trust_remote_code=True,
        cache_folder="cache"
    )
    
    connection_string = "postgresql://postgres:password@"+str(PG_HOST)+":"+str(PG_PORT)
    db_name = str(PG_DB)
    
    url = make_url(connection_string)
    vector_store = PGVectorStore.from_params(
        database=db_name,
        host=url.host,
        password=url.password,
        port=url.port,
        user=url.username,
        table_name="vector_store",
        embed_dim=1024,  # openai embedding dimension
        hnsw_kwargs={
            "hnsw_m": 16,
            "hnsw_ef_construction": 64,
            "hnsw_ef_search": 40,
            "hnsw_dist_method": "vector_cosine_ops"
        },
    )

    app.run(debug=True, host="0.0.0.0", port=PORT)
