# Banking Customer Support Chatbot — Project Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Original Python NLP Pipeline](#original-python-nlp-pipeline)
3. [Model Training](#model-training)
4. [Next.js Migration](#nextjs-migration)
5. [Architecture](#architecture)
6. [Design Patterns](#design-patterns)
7. [Database Schema](#database-schema)
8. [Deployment](#deployment)

---

## 1. Project Overview

This is an AI-powered banking customer support chatbot that classifies user intents, extracts named entities, analyzes sentiment, and generates contextual responses. The project has gone through two iterations:

1. **v1 — Python/FastAPI backend** with a vanilla HTML/CSS/JS frontend, designed for AWS Lambda + DynamoDB
2. **v2 — Next.js 14 + Supabase PostgreSQL** with a TypeScript NLP pipeline, deployed on Vercel

The chatbot handles banking-specific queries across 8 intent categories and provides escalation for negative sentiment.

---

## 2. Original Python NLP Pipeline

The original backend used three NLP components:

### 2.1 Intent Classification — DistilBERT (BERT)

- **Model**: `distilbert-base-uncased` fine-tuned on the **banking77** dataset
- **Library**: Hugging Face `transformers` (PyTorch backend)
- **Purpose**: Classify user messages into banking intent categories
- **Output**: Intent label + confidence score (0–1)

DistilBERT is a smaller, faster variant of BERT that retains ~97% of BERT's performance while being 60% faster. It uses a distillation process during pre-training to learn a smaller model that mimics the full BERT model's behavior.

**Why DistilBERT over full BERT?**
- 40% smaller (66M parameters vs 110M)
- 60% faster inference
- Near-identical accuracy for classification tasks
- Suitable for serverless deployment (AWS Lambda has cold start constraints)

### 2.2 Named Entity Recognition — spaCy

- **Library**: spaCy (`en_core_web_sm`)
- **Purpose**: Extract banking-relevant entities from user messages
- **Entity types detected**: MONEY, DATE, PERSON, ORG, GPE, CARDINAL, ORDINAL
- **Example**: "Transfer £500 to John on 15/01/2024" → `[MONEY: £500, PERSON: John, DATE: 15/01/2024]`

### 2.3 Sentiment Analysis — VADER

- **Library**: `vaderSentiment`
- **Purpose**: Score message polarity for escalation detection
- **Output**: `neg`, `neu`, `pos`, `compound` scores (compound range: -1 to +1)
- **Escalation threshold**: compound < -0.3 triggers human agent escalation

VADER (Valence Aware Dictionary and sEntiment Reasoner) is specifically tuned for social media and short text. It uses a lexicon of sentiment-bearing words with valence scores, combined with rules for handling:
- Punctuation (e.g., "great!!!" scores higher than "great")
- Capitalization (e.g., "GREAT" scores higher than "great")
- Degree modifiers (e.g., "very good" scores higher than "good")
- Negation (e.g., "not good" reverses polarity)
- Emoticons and slang

---

## 3. Model Training

### 3.1 Dataset — banking77

- **Source**: [mteb/banking77](https://huggingface.co/datasets/mteb/banking77) on Hugging Face
- **Domain**: Banking customer service queries
- **Size**: ~10,000 training samples
- **Labels**: 77 fine-grained banking intent categories
- **Examples**:

| Text | Intent |
|------|--------|
| "What is my current balance?" | `balance` |
| "I need to transfer money" | `transfer` |
| "My card has been stolen" | `card_lost_or_stolen` |
| "What are your loan rates?" | `interest_rate` |
| "I want to close my account" | `terminate_account` |

The 77 intents cover the full spectrum of banking operations: account management, card services, transactions, loans, payments, security, and general inquiries.

### 3.2 Training Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Base Model** | `distilbert-base-uncased` | Pre-trained on English text, uncased for robustness |
| **Epochs** | 5 | Sufficient for fine-tuning a pre-trained model |
| **Batch Size** | 32 (train) / 64 (eval) | Large batch for stable gradients on RTX 4060 Ti (16GB VRAM) |
| **Learning Rate** | 5e-5 | Standard for BERT fine-tuning (too high causes catastrophic forgetting) |
| **Warmup Steps** | 500 | Gradual LR increase prevents early training instability |
| **Weight Decay** | 0.01 | L2 regularisation to prevent overfitting |
| **Max Sequence Length** | 128 tokens | Banking queries are typically short (avg ~10 words) |
| **FP16** | Enabled (if CUDA available) | Mixed precision for 2x speedup on modern GPUs |
| **Early Stopping** | Patience of 3 eval steps | Prevents overfitting by monitoring validation F1 |
| **Random Seed** | 42 | Reproducibility |

### 3.3 Training Pipeline

```
1. Load banking77 dataset from Hugging Face Hub
          ↓
2. Create label mappings (77 intents ↔ numeric IDs)
          ↓
3. Split dataset: 80% train / 10% validation / 10% test
          ↓
4. Load pre-trained DistilBERT tokenizer
          ↓
5. Tokenize all splits (padding → 128, truncation enabled)
          ↓
6. Set PyTorch format (input_ids, attention_mask, label)
          ↓
7. Initialise DistilBERT with 77-class classification head
          ↓
8. Fine-tune with Hugging Face Trainer API
          ↓
9. Evaluate on held-out test set
          ↓
10. Save model weights, tokenizer, and label mappings
```

### 3.4 Evaluation Metrics

The training script computes four metrics on the test set:

| Metric | Description |
|--------|-------------|
| **Accuracy** | Overall proportion of correct predictions |
| **Precision** (weighted) | Of all predictions for a class, how many were correct |
| **Recall** (weighted) | Of all actual instances of a class, how many were found |
| **F1 Score** (weighted) | Harmonic mean of precision and recall (primary metric) |

The model selects the best checkpoint based on **weighted F1** on the validation set.

### 3.5 Hardware

- **GPU**: NVIDIA RTX 4060 Ti (16GB VRAM)
- **CUDA**: Enabled with FP16 mixed precision
- **Training time**: Approximately 10–15 minutes for 5 epochs

### 3.6 Saved Artifacts

After training, the following files are saved to `models/intent_model/`:

| File | Description |
|------|-------------|
| `config.json` | Model architecture configuration |
| `model.safetensors` | Fine-tuned model weights |
| `tokenizer.json` | Tokenizer vocabulary and config |
| `vocab.txt` | Token vocabulary file |
| `label_info.json` | Intent label ↔ ID mappings (77 labels) |

---

## 4. Next.js Migration

### 4.1 Motivation

The project was migrated from Python/FastAPI to Next.js/TypeScript for:
- **Simpler deployment**: Single codebase on Vercel (no separate Python backend)
- **No Python runtime dependency**: Everything runs in Node.js
- **Modern frontend**: React components with Tailwind CSS
- **Supabase integration**: PostgreSQL replaces DynamoDB (free tier, no AWS account needed)

### 4.2 NLP Pipeline Rewrites

| Python Component | TypeScript Replacement | Notes |
|-----------------|----------------------|-------|
| DistilBERT (transformers) | Keyword-based classifier | 8 intents with weighted scoring |
| spaCy NER | Regex-based entity extraction | Banking-specific patterns |
| VADER Sentiment | `sentiment` npm package | AFINN-based, similar approach |
| DialogueManager | TypeScript class | Same pipeline orchestration |
| Intent Handlers | TypeScript classes | Same Factory pattern |
| Sentiment Escalator | TypeScript class | Same Observer pattern |
| DynamoDB Client | Supabase client | Same DAO pattern |

### 4.3 Intent Classification (TypeScript)

The TypeScript classifier uses keyword matching with weighted scoring:

- Each intent has a list of associated keywords
- Longer multi-word keywords get higher weight (e.g., "move money" scores 2 vs "money" scoring 1)
- Confidence is normalised to 0–1 range

**Supported intents**: `balance`, `transaction`, `card`, `loan`, `complaint`, `greeting`, `goodbye`, `account`

### 4.4 Entity Extraction (TypeScript)

Regex patterns detect banking-specific entities:

| Entity Type | Pattern Examples |
|-------------|-----------------|
| MONEY | £1,250.75, $500, 1000 GBP |
| DATE | 25/12/2024, January 15, 2024 |
| ACCOUNT_NUMBER | 8-digit numbers |
| SORT_CODE | 12-34-56, 123456 |
| CARD_NUMBER | 16-digit with optional spaces |
| EMAIL | user@example.com |
| PHONE | +44 7700 900000 |
| REFERENCE | #SR-2024-001 |

---

## 5. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Vercel (Free Tier)                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Next.js 14 (App Router)                               │  │
│  │                                                        │  │
│  │  ┌─────────────┐    ┌──────────────────────────────┐  │  │
│  │  │  React UI    │    │  API Route (/api/chat)       │  │  │
│  │  │  - ChatWidget│───▶│  - DialogueManager           │  │  │
│  │  │  - Messages  │    │  - IntentClassifier          │  │  │
│  │  │  - Input     │    │  - EntityExtractor           │  │  │
│  │  │  - Escalation│    │  - SentimentAnalyzer         │  │  │
│  │  └─────────────┘    │  - IntentHandlers             │  │  │
│  │                      │  - SentimentEscalator         │  │  │
│  │                      └──────────┬───────────────────┘  │  │
│  └─────────────────────────────────┼──────────────────────┘  │
└────────────────────────────────────┼──────────────────────────┘
                                     │
                          ┌──────────▼──────────┐
                          │  Supabase (Free Tier)│
                          │  PostgreSQL Database  │
                          │  - conversations      │
                          │  - escalation_requests│
                          │  - user_profiles      │
                          └──────────────────────┘
```

### 5.1 Request Flow

```
User types message
       ↓
ChatWidget sends POST /api/chat
       ↓
API Route receives request
       ↓
DialogueManager.handle_message():
  1. classifyIntent()     → { intent, confidence }
  2. extractEntities()    → [{ text, label, start, end }]
  3. analyzeSentiment()   → { neg, neu, pos, compound }
  4. getHandler(intent)   → handler.handle(message, entities, context)
  5. needsEscalation()    → boolean (compound < -0.3)
       ↓
Save to Supabase (non-blocking)
       ↓
Return JSON response to frontend
       ↓
ChatWidget displays bot response + metadata
```

---

## 6. Design Patterns

| Pattern | Location | Purpose |
|---------|----------|---------|
| **Strategy** | `lib/nlp/intent-classifier.ts` | Allows swapping classification algorithms (keyword vs ML) without changing the DialogueManager |
| **Factory** | `lib/dialogue/handlers.ts` | Maps intent names to handler classes; returns the correct handler for each intent |
| **Observer** | `lib/dialogue/escalator.ts` | Notifies multiple listeners when sentiment escalation is triggered (logging, DB write, alerts) |
| **DAO (Data Access Object)** | `lib/db.ts` | Abstracts database operations; separates business logic from data persistence |
| **Singleton** | `app/api/chat/route.ts` | Reuses one DialogueManager instance across API requests |
| **Barrel Export** | `lib/nlp/index.ts`, `lib/dialogue/index.ts` | Clean module boundaries with single-entry-point imports |

---

## 7. Database Schema

### Supabase PostgreSQL Tables

#### `conversations`
Stores every chat turn for audit and analytics.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Auto-generated unique ID |
| `user_id` | TEXT | Session/user identifier |
| `timestamp` | TIMESTAMPTZ | When the message was sent |
| `user_message` | TEXT | User's input text |
| `bot_response` | TEXT | Bot's generated response |
| `intent` | TEXT | Classified intent |
| `confidence` | REAL | Intent confidence (0–1) |
| `sentiment_neg` | REAL | Negative sentiment score |
| `sentiment_neu` | REAL | Neutral sentiment score |
| `sentiment_pos` | REAL | Positive sentiment score |
| `sentiment_compound` | REAL | Compound sentiment (-1 to +1) |
| `escalated` | BOOLEAN | Whether escalation was triggered |

#### `escalation_requests`
Tracks cases where human intervention is needed.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Auto-generated unique ID |
| `user_id` | TEXT | User who triggered escalation |
| `timestamp` | TIMESTAMPTZ | When escalation occurred |
| `reason` | TEXT | Why escalation was triggered |
| `message` | TEXT | The triggering message |
| `sentiment_compound` | REAL | Sentiment score at escalation |
| `status` | TEXT | `pending`, `resolved`, etc. |

#### `user_profiles`
Stores user preferences and metadata.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | TEXT (PK) | Unique user identifier |
| `display_name` | TEXT | User's display name |
| `email` | TEXT | User's email |
| `preferences` | JSONB | Flexible key-value preferences |

Row Level Security (RLS) is enabled on all tables with permissive policies for demo use.

---

## 8. Deployment

### Stack

| Layer | Service | Cost |
|-------|---------|------|
| Frontend + API | Vercel (Hobby) | Free |
| Database | Supabase (Free) | Free |
| Domain | Namecheap / Cloudflare | ~$10/year (optional) |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous API key |

### Deployment Steps

1. Push code to GitHub
2. Import repository in Vercel
3. Add environment variables in Vercel Settings
4. Run SQL migration in Supabase SQL Editor (`supabase/migrations/001_create_tables.sql`)
5. Deploy — Vercel auto-builds on every push to `main`

---

## References

- [DistilBERT Paper](https://arxiv.org/abs/1910.01108) — Sanh et al., 2019
- [banking77 Dataset](https://huggingface.co/datasets/mteb/banking77) — Hugging Face
- [VADER Sentiment](https://github.com/cjhutto/vaderSentiment) — Hutto & Gilbert, 2014
- [spaCy NER](https://spacy.io/usage/linguistic-features#named-entities) — Explosion AI
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/) — Documentation
- [Next.js Documentation](https://nextjs.org/docs) — Vercel
- [Supabase Documentation](https://supabase.com/docs) — Supabase