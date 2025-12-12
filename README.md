# 🚀 DynaRAG - Dynamic Retrieval-Augmented Generation for Any Document

**DynaRAG** is a fully dynamic RAG engine designed to transform any document—PDFs, text files, Word docs, slides, or entire folders—into a real-time, queryable knowledge base.

**No preprocessing. No manual pipelines.**  
Just give it content and start asking questions.

DynaRAG automatically:
- **Ingests and parses documents** from any source
- **Cleans and chunks content intelligently** for optimal retrieval
- **Embeds using state-of-the-art vector models** for semantic understanding
- **Retrieves relevant context on demand** with precision
- **Generates grounded, citation-backed answers** you can trust

Whether you're building an internal assistant, a research companion, or a knowledge automation tool, DynaRAG gives you instant RAG without the heavy lifting.

## Why DynaRAG?

The name combines:
- **Dyna** — from *Dynamic* — representing instant ingestion and adaptive indexing
- **RAG** — *Retrieval-Augmented Generation*

Together, they form a system that is **flexible, scalable, and purpose-built for live, dynamic document understanding**.

## 🚀 Features

- **Intelligent Document Retrieval**: Uses semantic search to find the most relevant information
- **Context-Aware Answers**: Generates accurate answers augmented with retrieved context
- **Multiple Document Support**: Index documents from multiple directories
- **RESTful API**: Easy-to-use API endpoints for integration
- **Web Interface**: Clean, responsive UI for asking questions
- **Docker Support**: Containerized deployment for easy setup
- **Persistent Storage**: ChromaDB vector database with persistent storage
- **Configurable**: Flexible configuration for chunk size, overlap, and retrieval parameters

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Data Collection](#data-collection)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** (for local development)
- **Docker** and **Docker Compose** (recommended for deployment)
- **Hugging Face API Key** (free account at [huggingface.co](https://huggingface.co))

## 📥 Installation

### Option 1: Docker (Recommended) 🐳

**Quick Start:**

1. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

2. **Set up environment variables:**
1. **Create a `.env` file** in the project root:
   ```env
   HF_API_KEY=your_huggingface_api_key_here
   ```
   
   Get your Hugging Face API key from: https://huggingface.co/settings/tokens

2. **Build and start the container**:
   ```bash
   docker-compose up -d --build
   ```

3. **Access the application**:
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

![Docker Setup](./images/docker-setup.png)

### Option 2: Local Development

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file**:
   ```env
   HF_API_KEY=your_huggingface_api_key_here
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## ⚙️ Configuration

The system is configured through `config.json`:

```json
{
    "document_paths": [],
    "collection_name": "rag_collection",
    "n_results": 5,
    "use_augmentation": true,
    "chunk_size": 1000,
    "chunk_overlap": 100,
    "tokens_per_chunk": 256
}
```

**Note**: By default, `document_paths` is empty. You'll add your data sources through the web interface (see Usage section below).

### Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `document_paths` | List of directories containing documents to index | `["./docs"]` |
| `collection_name` | Name of the ChromaDB collection | `"rag_collection"` |
| `n_results` | Number of relevant chunks to retrieve | `5` |
| `use_augmentation` | Enable context-augmented generation | `true` |
| `chunk_size` | Size of text chunks (characters) | `1000` |
| `chunk_overlap` | Overlap between chunks (characters) | `100` |
| `tokens_per_chunk` | Max tokens per chunk for embeddings | `256` |

## 🎮 Running the Application

### Using Docker

```bash
# Start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Using Python Directly

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Run the application
python main.py

# Or use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

![Application Running](./images/app-running.png)

## 💡 Usage

### Quick Start: Premier League Knowledge Base Demo

This guide demonstrates DynaRAG's dynamic capabilities by showing the **before and after** of loading data. You'll see how DynaRAG starts with no knowledge, loads the Premier League dataset, and instantly becomes a Premier League expert.

---

#### Step 1: Launch the Application

After starting the application (Docker or Python), open your browser to http://localhost:8000

![DynaRAG Home - Empty](./images/dynarag-home-empty.png)

The application starts with an **empty knowledge base** (no documents loaded).

---

#### Step 2: Test the Empty Knowledge Base

Let's verify DynaRAG has no Premier League knowledge yet.

**Ask**: "Who won the Premier League in 1992-93?"

![Question Before Data](./images/question-before-data.png)

DynaRAG will return either:
- **No results found**, or
- A generic response indicating it doesn't have relevant information

![No Results](./images/no-results.png)

This proves the system is working correctly - it won't make up answers without data!

---

#### Step 3: Load the Premier League Dataset

Now let's give DynaRAG some knowledge. Click the **⚙️ Settings** tab.

![Settings Tab Empty](./images/settings-tab-empty.png)

You'll see:
- **Document Paths**: Currently empty
- **Add Document Path** button

**Add the Premier League data:**

1. Type the path: `./premier_league_data/wikipedia`
2. Click **Add Path**

![Adding Document Path](./images/adding-document-path.png)

The path is now added to the list.

---

#### Step 4: Reindex the Documents

Scroll down in the Settings tab and click **🔄 Reindex Documents**

![Reindex Button](./images/reindex-button.png)

DynaRAG will:
- Scan the folder (80+ Wikipedia articles)
- Parse and chunk the text
- Generate embeddings
- Store in the vector database

![Reindexing Progress](./images/reindexing-progress.png)

You'll see a success message when complete:
- **"Successfully reindexed X documents"**

---

#### Step 5: Test Again with Data Loaded

Return to the **💬 Question** tab and ask the same question:

**Ask**: "Who won the Premier League in 1992-93?"

![Question After Data](./images/question-after-data.png)

Now DynaRAG returns:
- **✅ Detailed Answer**: "Manchester United won the inaugural Premier League season in 1992-93..."
- **📚 Source Context**: Relevant passages from the Wikipedia articles
- **🔢 Multiple Chunks**: Shows which documents the information came from

![Answer with Results](./images/answer-with-results.png)

**The RAG is working!** 🎉

---

#### Step 6: Try More Complex Questions

Now that the knowledge base is loaded, explore the full dataset:

**Question**: "Tell me about Leicester City's miracle season in 2015-16"

![Complex Question](./images/complex-question.png)

DynaRAG retrieves multiple relevant passages and synthesizes a comprehensive answer about Leicester's historic Premier League victory.

---

#### Step 7: View Statistics

Scroll down on any tab to see **System Statistics**:

![System Statistics](./images/system-statistics.png)

- **Total Documents**: Number of indexed documents
- **Collection Name**: Your vector database name
- **Chunk Size**: Text processing configuration

This confirms your data is loaded and ready!

### More Example Questions

Try these to explore the Premier League knowledge base:

#### 🏆 **Championships & Winners**
- "Who won the Premier League in 1992-93?"
- "Which team has won the most Premier League titles?"
- "Tell me about Manchester United's dominance in the 1990s"

#### ⚽ **Players & Records**
- "Who has scored the most Premier League goals?"
- "Tell me about Alan Shearer's career"
- "Who is Cristiano Ronaldo and what did he achieve in the Premier League?"

#### 📊 **Memorable Moments**
- "What is Arsenal's Invincibles season?"
- "What happened in the 2015-16 season with Leicester City?"
- "Tell me about the 2011-12 season finale"

#### 👨‍💼 **Managers & Tactics**
- "Who is Sir Alex Ferguson?"
- "Tell me about José Mourinho's time at Chelsea"
- "What did Arsène Wenger achieve at Arsenal?"

#### 📈 **Recent History**
- "Who won the Premier League in 2023-24?"
- "What has Manchester City achieved recently?"
- "Tell me about Liverpool under Jürgen Klopp"

![Example Questions](./images/example-questions.png)

### API Usage

You can also interact with DynaRAG programmatically:

```python
import requests

# Ask a question
response = requests.post(
    "http://localhost:8000/api/question",
    json={
        "question": "Who won the Premier League in 2023-24?",
        "n_results": 5,
        "use_augmentation": True
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Found {result['num_chunks']} relevant chunks")
```

```bash
# Using curl
curl -X POST "http://localhost:8000/api/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Who is the all-time Premier League top scorer?",
    "n_results": 5
  }'
```

## 📚 API Documentation

### Endpoints

#### `POST /api/question`
Ask a question and get an answer with relevant context.

**Request Body**:
```json
{
  "question": "Your question here",
  "n_results": 5,
  "use_augmentation": true
}
```

**Response**:
```json
{
  "answer": "Generated answer based on context",
  "relevant_chunks": ["chunk1", "chunk2", "..."],
  "num_chunks": 5
}
```

#### `GET /api/settings`
Get current configuration settings.

#### `POST /api/settings`
Update configuration settings.

**Request Body**:
```json
{
  "document_paths": ["./docs", "./new_folder"],
  "n_results": 10,
  "chunk_size": 1500
}
```

#### `POST /api/document-path/add`
Add a new document path to index.

**Request Body**:
```json
{
  "path": "./new_documents"
}
```

#### `POST /api/document-path/remove`
Remove a document path from indexing.

#### `POST /api/reindex`
Reindex all documents from configured paths.

#### `GET /api/stats`
Get collection statistics (document count, etc.).

### Interactive API Documentation

FastAPI provides interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

![API Documentation](./images/api-docs.png)

## 📊 Data Collection

### Collecting Premier League Data

BizMind includes a Jupyter notebook for collecting Premier League data from Wikipedia:

1. **Open the notebook**:
   ```bash
   jupyter notebook collect_premier_league_data.ipynb
   ```

2. **Run all cells** to download:
   - 80+ Wikipedia articles
   - Complete season history (1992-2025)
   - Club information
   - Player biographies
   - Manager profiles
   - Historical events

3. **Data location**: Articles are saved in `premier_league_data/wikipedia/`

4. **Automatic indexing**: The data is automatically indexed when the application starts

![Data Collection](./images/data-collection.png)

### Adding Your Own Documents

1. **Create a folder** for your documents:
   ```bash
   mkdir my_documents
   ```

2. **Add text files** (`.txt`, `.md`, etc.) to the folder

3. **Update `config.json`**:
   ```json
   {
     "document_paths": [
       "./docs",
       "./premier_league_data/wikipedia",
       "./my_documents"
     ]
   }
   ```

4. **Reindex** using the API or restart the application

## 📁 Project Structure

```
BizMind/
├── main.py                          # FastAPI application entry point
├── requirements.txt                 # Python dependencies
├── config.json                      # Configuration file
├── docker-compose.yml               # Docker Compose configuration
├── Dockerfile                       # Docker image definition
├── .env                            # Environment variables (HF_API_KEY)
├── README.md                       # This file
│
├── rag_mind/                       # RAG model package
│   ├── __init__.py
│   ├── config.py                   # Configuration manager
│   ├── rag_model.py                # Core RAG model implementation
│   └── utils.py                    # Utility functions
│
├── static/                         # Web interface
│   ├── index.html                  # Main HTML page
│   ├── styles.css                  # Styling
│   └── app.js                      # Frontend JavaScript
│
├── docs/                           # Sample documents
│   └── *.txt                       # Text documents
│
├── premier_league_data/            # Premier League data
│   ├── wikipedia/                  # Wikipedia articles
│   │   └── *.txt
│   └── metadata/                   # Article metadata
│       ├── articles_index.json
│       └── articles_index.csv
│
├── chroma_persistent_storage/      # ChromaDB vector database
│   └── [database files]
│
└── collect_premier_league_data.ipynb  # Data collection notebook
```

## 🔍 How It Works

1. **Document Processing**: Text documents are loaded and split into chunks
2. **Embedding Generation**: Each chunk is converted to a vector embedding using Hugging Face models
3. **Vector Storage**: Embeddings are stored in ChromaDB for fast retrieval
4. **Question Processing**: User questions are embedded using the same model
5. **Similarity Search**: Most relevant chunks are retrieved based on cosine similarity
6. **Answer Generation**: Retrieved context is used to generate accurate answers
7. **Response**: Answer and source chunks are returned to the user

![RAG Pipeline](./images/rag-pipeline.png)

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.9+
- **Vector Database**: ChromaDB with persistent storage
- **Embeddings**: Sentence Transformers (BAAI/bge-small-en-v1.5)
- **LLM**: Mistral-7B-Instruct-v0.2 via Hugging Face Inference API
- **Text Processing**: LangChain text splitters
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Containerization**: Docker, Docker Compose

## 🐛 Troubleshooting

### Docker Issues

**Container won't start**:
```bash
# Check logs
docker-compose logs -f

# Rebuild container
docker-compose down
docker-compose up -d --build
```

**Port already in use**:
- Change the port in `docker-compose.yml`: `"8080:8000"`

### API Key Issues

**"HF_API_KEY not found"**:
1. Ensure `.env` file exists in project root
2. Check the API key is correct: `HF_API_KEY=hf_xxxxxxxxxxxxx`
3. Restart the application

### ChromaDB Issues

**Database errors**:
```bash
# Clear the database and reindex
rm -rf chroma_persistent_storage/*
# Restart application
```

### No Results Found

**Questions return empty results**:
1. Check that documents are indexed: `GET /api/stats`
2. Verify document paths in `config.json`
3. Try reindexing: `POST /api/reindex`
4. Increase `n_results` in configuration

## 🛠️ Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Format code
black .

# Lint code
flake8 .
```

### Adding New Features

1. Modify the code in `rag_mind/` or `main.py`
2. Update configuration if needed
3. Rebuild Docker container: `docker-compose up -d --build`
4. Test the changes

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📧 Support

For questions or issues:
- Check the [Troubleshooting](#troubleshooting) section
- Review the API documentation at `/docs`
- Open an issue on the project repository

## 🎯 Roadmap

Future enhancements:
- [ ] Multi-language support
- [ ] PDF document support
- [ ] Advanced query filtering
- [ ] User authentication
- [ ] Query history and analytics
- [ ] Fine-tuned models for domain-specific tasks
- [ ] Real-time document updates
- [ ] Export/import configuration

---

**Built with ❤️ using FastAPI, ChromaDB, and Hugging Face**

![Footer](./images/footer.png)
