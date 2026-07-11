# 🤖 Customer Support Chatbot

An AI-powered customer support chatbot built with **OOP design patterns**, **NLP**, **NoSQL (DynamoDB)**, and **AWS serverless architecture**. Fine-tunes DistilBERT on banking77 for intent classification, with sentiment escalation, entity extraction, and a full CI/CD pipeline.



## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **CUDA 11.8+** (for GPU training on RTX 4060 Ti)
- **Docker & Docker Compose** (for localstack and containerized deployment)
- **Git**

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