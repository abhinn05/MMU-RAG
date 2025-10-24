🧠 MMU-RAG  
**Retrieval-Augmented Generation (RAG) system with FastAPI and Docker**

---

## 📖 Overview  
MMU-RAG is an intelligent API server designed to answer questions using **Retrieval-Augmented Generation (RAG)**.  
It combines **information retrieval** and **large language models (LLMs)** to provide accurate, context-aware answers from your local knowledge base or document corpus.  
Supports both **local development** and **Dockerized deployment**.

---

## ✨ Features  
- Retrieval-based context extraction  
- Generative model for intelligent responses  
- Configurable via `config.yaml`  
- REST API endpoint for question answering  
- Modular code structure for flexible extensions  
- Easy Docker deployment  

---

## 🗂️ Project Structure  

```text
MMU-RAG/
│
├── app.py                  # Main FastAPI server
├── config.yaml             # Configuration file
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker build file
├── local_test.py           # Local test script
├── t2t_val.jsonl           # Sample dataset / validation data
└── src/                    # Source code for retrieval & generation modules
````

---

## 🧩 Prerequisites

* Python 3.9+
* pip package manager
* Docker & Docker Compose (for container deployment)
* Git

Clone the repository:

```bash
git clone https://github.com/abhinn05/MMU-RAG.git
cd MMU-RAG
```

---

## 🧪 Running Locally (Without Docker)

### 1️⃣ Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure

Edit `config.yaml` to set:

```yaml
retriever:
  source_path: ./data/documents
  top_k: 5

generator:
  model_name: "gpt-3.5-turbo"
  max_tokens: 512

server:
  host: "0.0.0.0"
  port: 5010
```

### 4️⃣ Run the Server

```bash
python app.py
```

Server will start at: `http://localhost:5010`

### 5️⃣ Test the API

```bash
curl -X POST http://localhost:5010/run \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Retrieval Augmented Generation?"}'
```

Expected JSON response:

```json
{
  "answer": "Retrieval Augmented Generation is a method that combines information retrieval with generative models to produce context-aware answers."
}
```

---

## 🐳 Running with Docker

### 1️⃣ Build the Docker Image

```bash
docker build -t mmu-rag:latest .
```

### 2️⃣ Run the Container

```bash
docker run -d \
  -p 5010:5010 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/data:/app/data \
  --name mmu-rag-container \
  mmu-rag:latest
```

### 3️⃣ Verify the Server

```bash
curl -X POST http://localhost:5010/run \
  -H "Content-Type: application/json" \
  -d '{"question": "How to deploy with Docker?"}'
```

### 4️⃣ Stop and Remove the Container

```bash
docker stop mmu-rag-container
docker rm mmu-rag-container
```

---

## ⚙️ API Endpoint

### POST `/run`

**Request:**

```json
{
  "question": "Your query here"
}
```

**Response:**

```json
{
  "answer": "Generated answer based on retrieved context"
}
```

---

## 🧑‍💻 Contributing

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature-name
```

3. Make your changes
4. Commit and push

```bash
git commit -m "Added new feature"
git push origin feature-name
```

5. Open a Pull Request

---

## 🪪 License

This project is licensed under **MIT License**.

---

## 💡 Future Enhancements

* Add vector database support (FAISS / Chroma)
* Integrate a model selection UI
* Add streaming response support
* Deploy to cloud (AWS / GCP / Azure)

---

## 🧭 Author

**Abhinn Goyal**
[GitHub](https://github.com/abhinn05) • [LinkedIn](https://www.linkedin.com/in/abhinn-goyal/)
