---

## Document Indexing Chatbot with Progress Bar

This application allows users to upload documents for indexing, which is used in a Retrieval-Augmented Generation (RAG) system powered by LlamaIndex and Ollama’s models. The progress of document indexing is displayed on a webpage using a progress bar.

### Features
- Upload documents for indexing.
- Real-time progress bar showing indexing completion.
- Simple frontend for document upload and backend API for handling indexing.

---

### Project Structure

```
chatbot_project/
├── Dockerfile                   # Dockerfile for building the container
├── docker-compose.yml           # Optional: Docker Compose file
├── .env                         # Environment file (for secret configurations)
├── requirements.txt             # Dependencies for the project
├── README.md                    # Project documentation
├── src/
│   ├── app.py                   # Flask application code
│   ├── templates/
│   │   └── index.html           # HTML template for the /index page
│   └── static/
│       └── style.css            # CSS styling for the progress bar and layout
```

---

### Prerequisites

Make sure you have the following installed:
- **Docker** (for containerization)
- **Docker Compose** (optional, for managing multi-container applications)
- **Python 3.9+** (if running locally without Docker)

Make sure you have the following API keys:
- **Llama cloud API key**

Make sure you have access to LLM model and server. You can setup your own ollama server.
---

### Setup and Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/miguelJalube/virtSecretary.git
   cd virtSecretary
   ```

2. **Environment Variables**:
   Create a `.env` file at the root level of the project. Include any required configurations for API keys.

   Example `.env`:
   ```plaintext
   # .env file
   LLM=[llm model]
   LLM_SERVER =[llm server]
   LLAMA_CLOUD_API_KEY=[llama cloud api key]
   EMBED_MODEL = "intfloat/multilingual-e5-large"
   PORT = 8071
   ```

3. **Install Dependencies** (if running locally without Docker):
   ```bash
   pip install -r requirements.txt
   ```

---

### Running the Application with Docker

2. **Run the Docker Container**:
   Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. **Access the Application**:
   Open your browser and go to `http://localhost:8071/index` to access the document indexing interface.
   Then `http://localhost:8071/chat` to access the chatbot interface.

---

### Usage

1. **Index Documents**:
   - Navigate to the `/index` page.
   - Upload your documents using the file input.
   - Click the "Start Indexing" button. The progress bar will display the indexing progress in real-time.

2. **Check Indexing Status**:
   - Once indexing is complete, the progress bar will reach 100%, and a message will display indicating that indexing is complete.

3. **Chat**:
   - You can now use the indexed documents in the chatbot at `/chat` or other application that requires indexed data.

---

### Notes

- **Data Processing**: The progress bar updates as each document is indexed on the server.
- **Error Handling**: Any issues during file upload or indexing will be displayed as a status message.

---

### Example Commands

**To rebuild the container and restart the application**:
```bash
docker-compose up --build
```

**To stop the application**:
```bash
docker-compose down
```

---

### License

This project is free for non-comercial use. See `LICENSE` for details.

---

### Contributing

Feel free to submit issues or pull requests if you would like to contribute to the project.