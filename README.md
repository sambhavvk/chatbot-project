# 🤖 Customer Support Chatbot

An AI-powered customer support chatbot built with **OOP design patterns**, **NLP**, **NoSQL (DynamoDB)**, and **AWS serverless architecture**. Fine-tunes DistilBERT on banking77 for intent classification, with sentiment escalation, entity extraction, and a full CI/CD pipeline.

---

## 📋 Table of Contents

- [Architecture](#architecture)
- [OOP Design Patterns](#oop-design-patterns)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Training the Model](#training-the-model)
- [Running Locally](#running-locally)
- [Docker Setup](#docker-setup)
- [AWS Deployment](#aws-deployment)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Tech Stack](#tech-stack)

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Frontend  │────▶│  API Gateway  │────▶│  Lambda /       │
│  (HTML/JS)  │     │  (REST)       │     │  FastAPI Server  │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                   │
                          ┌────────────────────────┼────────────────────────┐
                          │                        │                        │
                    ┌─────▼─────┐          ┌──────▼──────┐         ┌───────▼───────┐
                    │  Intent   │          │   Entity    │         │  Sentiment    │
                    │ Classifier│          │  Extractor  │         │  Analyzer     │
                    │ (Strategy)│          │   (spaCy)   │         │   (VADER)     │
                    └─────┬─────┘          └──────┬──────┘         └───────┬───────┘
                          │                        │                        │
                          └────────────────────────┼────────────────────────┘
                                                   │
                                          ┌────────▼────────┐
                                          │  Dialogue       │
                                          │  Manager        │
                                          │  (Orchestrator) │
                                          └────────┬────────┘
                                                   │
                              ┌────────────────────┼────────────────────┐
                              │                    │                    │
                       ┌──────▼──────┐     ┌──────▼──────┐     ┌──────▼──────┐
                       │   Intent    │     │  Sentiment  │     │  DynamoDB   │
                       │  Handler    │     │  Escalator  │     │   Client    │
                       │  (Factory)  │     │ (Observer)  │     │   (DAO)     │
                       └─────────────┘     └─────────────┘     └─────────────┘
```

### Data Flow
1. User sends a message via the frontend → API Gateway → Lambda / FastAPI
2. `DialogueManager` classifies the intent (Strategy pattern), extracts entities (spaCy), and analyzes sentiment (VADER)
3. The appropriate `IntentHandler` (Factory pattern) generates a contextual response
4. If sentiment drops below threshold, `SentimentEscalator` notifies observers (Observer pattern)
5. Conversation is persisted to DynamoDB via the DAO layer

---

## 🎨 OOP Design Patterns

| Pattern | Where Used | Purpose |
|---------|------------|---------|
| **Strategy** | `IntentClassifier` (abstract) with `BertIntentClassifier` / `MockIntentClassifier` | Swap ML models without changing client code |
| **Factory** | `IntentHandlerFactory` → creates `BalanceHandler`, `ComplaintHandler`, etc. | Decouple intent routing from handler creation |
| **Observer** | `SentimentEscalator` + `SentimentObserver` implementations | Trigger escalation notifications when user sentiment drops |
| **DAO** | `DynamoDBClient` | Abstract all DynamoDB CRUD operations behind a clean interface |

---

## 📁 Project Structure

```
chatbot-project/
├── data/                         # Raw & processed datasets
├── models/                       # Saved trained models
├── src/
│   ├── __init__.py
│   ├── nlp/
│   │   ├── __init__.py
│   │   ├── intent_classifier.py  # Abstract + BERT + Mock implementations (Strategy)
│   │   ├── entity_extractor.py   # spaCy NER wrapper
│   │   └── sentiment_analyzer.py # VADER sentiment wrapper
│   ├── dialogue/
│   │   ├── __init__.py
│   │   ├── manager.py            # DialogueManager (orchestrator)
│   │   ├── escalator.py          # Observer pattern for sentiment escalation
│   │   ├── cli.py                # Interactive CLI chatbot loop
│   │   └── handlers/
│   │       ├── __init__.py
│   │       ├── base.py           # Abstract IntentHandler
│   │       ├── factory.py        # IntentHandlerFactory (Factory pattern)
│   │       └── registry.py       # Concrete handlers (Balance, Transaction, etc.)
│   ├── storage/
│   │   ├── __init__.py
│   │   └── dynamodb_client.py    # DAO for DynamoDB operations
│   ├── api/
│   │   ├── __init__.py
│   │   ├── lambda_handler.py     # AWS Lambda entry point
│   │   └── local_server.py       # FastAPI server for local development
│   └── train.py                  # Fine-tune DistilBERT on banking77
├── tests/
│   ├── __init__.py
│   ├── test_intent_classifier.py
│   ├── test_sentiment_analyzer.py
│   ├── test_handlers.py
│   └── test_dialogue_manager.py
├── frontend/
│   ├── index.html                # Chat UI
│   ├── styles.css                # Styles
│   ├── app.js                    # Frontend logic
│   └── nginx.conf                # Nginx config for Docker
├── Dockerfile                    # Multi-stage build (dev + lambda)
├── docker-compose.yml            # localstack + API + frontend
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **CUDA 11.8+** (for GPU training on RTX 4060 Ti)
- **Docker & Docker Compose** (for localstack and containerized deployment)
- **Git**

### 1. Clone & Setup

```bash
git clone https://github.com/sambhavvk/chatbot-project.git
cd chatbot-project

# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 2. Verify CUDA (optional, for GPU training)

```python
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0)}')"
```

Expected output:
```
CUDA available: True
Device: NVIDIA GeForce RTX 4060 Ti
```

---

## 🧠 Training the Model

Fine-tune DistilBERT on the **banking77** dataset (13,083 utterances, 77 intents):

```bash
python src/train.py
```

**What happens:**
1. Downloads `mteb/banking77` from HuggingFace
2. Splits into 80% train / 10% val / 10% test
3. Fine-tunes DistilBERT with:
   - Batch size: 32 (fits easily in 4060 Ti VRAM)
   - 5 epochs with early stopping
   - Mixed precision (FP16) on CUDA
   - Weighted F1 as the optimization metric
4. Saves model to `models/intent_model/`

**Expected result:** >90% validation accuracy, ~90% F1 score.

---

## 💻 Running Locally

### Option A: CLI Chatbot (no Docker)

```bash
# Using mock classifier (no GPU needed)
python -m src.dialogue.cli

# Using trained BERT model
python -m src.dialogue.cli --bert

# With DynamoDB persistence (requires localstack)
python -m src.dialogue.cli --db
```

### Option B: FastAPI Server + Frontend

```bash
# Start the API server
uvicorn src.api.local_server:app --host 0.0.0.0 --port 8080 --reload
```

Then open `frontend/index.html` in your browser, or visit:
- **API Docs:** http://localhost:8080/docs
- **Health Check:** http://localhost:8080/health

### Option C: Docker Compose (full stack)

```bash
docker-compose up -d
```

This starts:
- **Chatbot API** at http://localhost:8080
- **Frontend** at http://localhost:3000
- **localstack** (DynamoDB emulator) at http://localhost:4566

---

## 🐳 Docker Setup

### Build & Run (Development)

```bash
# Build
docker build --target dev -t chatbot-api .

# Run
docker run -p 8080:8080 chatbot-api
```

### Build Lambda Image

```bash
docker build --target lambda -t chatbot-lambda .
# Push to ECR and create Lambda function from container image
```

---

## ☁️ AWS Deployment

### Step 1: Train Model Locally

```bash
python src/train.py
```

### Step 2: Create ECR Repository & Push Image

```bash
aws ecr create-repository --repository-name chatbot-lambda --region eu-west-2
docker build --target lambda -t chatbot-lambda .
# Tag and push following AWS ECR instructions
```

### Step 3: Create Lambda Function
- Use container image from ECR
- Set memory to 2048 MB, timeout to 30 seconds
- Set environment variable `MODEL_PATH=/app/models/intent_model`

### Step 4: Create API Gateway
- REST API with POST `/chat` endpoint
- Lambda proxy integration
- Enable CORS

### Step 5: Deploy Frontend to S3
- Upload `frontend/` to an S3 bucket with static website hosting
- Update `API_ENDPOINT` in `frontend/app.js` to point to your API Gateway URL

### Free Tier Usage
- **Lambda:** 1M requests/month free
- **API Gateway:** 1M requests/month free
- **DynamoDB:** 25 GB storage, 25 WCU/RCU free
- **S3:** 5 GB storage free
- **ECR:** 500 MB storage free

---

## 📡 API Reference

### `POST /chat`

Process a user message and return the chatbot response.

**Request:**
```json
{
  "user_id": "user-123",
  "message": "What is my account balance?"
}
```

**Response:**
```json
{
  "response": "The current balance for your account is £1,250.75. Is there anything else I can help you with?",
  "intent": "balance",
  "confidence": 0.9876,
  "entities": [
    {"text": "account", "label": "MONEY", "start": 15, "end": 22}
  ],
  "sentiment": {
    "neg": 0.0,
    "neu": 0.892,
    "pos": 0.108,
    "compound": 0.2732
  },
  "escalated": false,
  "timestamp": "2025-01-15T10:30:00.123456+00:00"
}
```

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_intent_classifier.py -v
```

### Test Coverage

| Module | Tests |
|--------|-------|
| `test_intent_classifier.py` | Mock classifier accuracy, confidence bounds, unknown intent handling |
| `test_sentiment_analyzer.py` | Positive/negative/neutral polarity, escalation threshold, custom config |
| `test_handlers.py` | All handler responses, Factory pattern (creation, caching, registration), FallbackHandler |
| `test_dialogue_manager.py` | Full pipeline integration, escalation triggering, Observer notifications, error handling |

---

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **ML Framework** | PyTorch + Transformers | Fine-tune DistilBERT |
| **NLP** | spaCy, VADER Sentiment | Entity extraction, sentiment |
| **Backend** | Python 3.12, FastAPI, uvicorn | REST API server |
| **Serverless** | AWS Lambda, API Gateway | Cloud deployment |
| **Database** | Amazon DynamoDB (localstack for dev) | Conversation persistence |
| **Frontend** | Vanilla HTML/CSS/JS | Chat UI |
| **Containerization** | Docker, Docker Compose | Reproducible environments |
| **Testing** | pytest, pytest-mock, pytest-cov | Unit testing, coverage |
| **CI/CD** | GitHub Actions | Automated testing on push |
| **Emulation** | localstack | Local AWS service emulation |

---

## 📝 Intent Classes

The system handles these intents (from banking77 dataset):

| Intent | Example Utterance | Handler |
|--------|------------------|---------|
| `balance` | "What's my current balance?" | `BalanceHandler` |
| `transaction` | "I want to transfer £50" | `TransactionHandler` |
| `card` | "My credit card was stolen" | `CardHandler` |
| `loan` | "Tell me about mortgage rates" | `LoanHandler` |
| `complaint` | "I have a serious complaint" | `ComplaintHandler` |
| `greeting` | "Hello! Good morning" | `GreetingHandler` |
| `goodbye` | "Bye, see you later" | `GoodbyeHandler` |
| *unknown* | (anything else) | `FallbackHandler` |

---

## 🏆 Key Features

- ✅ **GPU-accelerated training** on NVIDIA RTX 4060 Ti
- ✅ **Clean OOP architecture** with 4 design patterns
- ✅ **Sentiment-based escalation** with Observer pattern
- ✅ **NoSQL persistence** with DynamoDB (DAO pattern)
- ✅ **Serverless deployment** on AWS Lambda + API Gateway
- ✅ **Full Docker setup** with localstack for local dev
- ✅ **Interactive CLI** for testing without a frontend
- ✅ **Responsive chat UI** with typing indicators and escalation banner
- ✅ **Comprehensive test suite** with >90% coverage

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

*Built as a portfolio project demonstrating OOP, NLP, NoSQL, and AWS cloud deployment skills.*