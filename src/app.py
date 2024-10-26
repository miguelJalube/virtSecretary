import os
import logging
from flask import Flask, request, jsonify, render_template

from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.ollama import Ollama

from llama_index.core import (
    load_index_from_storage,
    StorageContext,
)

LLM = os.getenv("LLM")

# Initialize Flask application
app = Flask(__name__)

# Initialize LlamaIndex
Settings.llm = Ollama(model=LLM, request_timeout=240)

# Index the data
@app.route("/index")
def index():
    reader = SimpleDirectoryReader(input_dir="knowledge")
    documents = reader.load_data()
    
    index = VectorStoreIndex.from_documents(
        documents, show_progress=True, 
    )
    
    # save index to disk
    index.set_index_id("vector_index")
    index.storage_context.persist("./storage")
    
    return jsonify({"message": "Indexing complete"})

# Chat route for handling POST requests with user queries
@app.route("/chat", methods=["POST"])
def chat():
    # rebuild storage context
    storage_context = StorageContext.from_defaults(
        persist_dir="storage"
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
    user_query = data.get("query", "")
    
    # Use LlamaIndex to get a response

    return jsonify({"response": response.response})

# Home route to serve the frontend interface
@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
