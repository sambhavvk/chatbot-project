# Banking Customer Support Chatbot

AI-powered banking customer support chatbot built with **Next.js 14**, **Supabase PostgreSQL**, and **TypeScript NLP pipeline**.

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Next.js Frontend (React + Tailwind CSS)        │
│  ┌───────────────────────────────────────────┐  │
│  │  ChatWidget → MessageBubble → ChatInput   │  │
│  └───────────────────────────────────────────┘  │
│                      │ POST /api/chat            │
│  ┌───────────────────────────────────────────┐  │
│  │  API Route (Next.js Route Handler)         │  │
│  │  ┌─────────────────────────────────────┐  │  │
│  │  │  DialogueManager (TypeScript)        │  │  │
│  │  │  ├─ IntentClassifier (keyword NLP)   │  │  │
│  │  │  ├─ EntityExtractor (regex NER)      │  │  │
│  │  │  ├─ SentimentAnalyzer (sentiment pkg)│  │  │
│  │  │  ├─ IntentHandlers (Factory Pattern) │  │  │
│  │  │  └─ SentimentEscalator (Observer)    │  │  │
│  │  └─────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────┘  │
│                      │                           │
│  ┌───────────────────────────────────────────┐  │
│  │  Supabase PostgreSQL                       │  │
│  │  ├─ conversations                          │  │
│  │  ├─ escalation_requests                    │  │
│  │  └─ user_profiles                          │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Features

- **Intent Classification**: Keyword-based NLP with 8 banking intents (balance, transaction, card, loan, complaint, greeting, goodbye, account)
- **Named Entity Recognition**: Regex-based extraction for money, dates, account numbers, sort codes, card numbers, emails, phone numbers
- **Sentiment Analysis**: AFINN-based sentiment scoring with escalation detection
- **Dialogue Management**: Full pipeline orchestration with Factory (handlers) and Observer (escalation) patterns
- **Persistent Storage**: Supabase PostgreSQL replacing DynamoDB
- **Modern UI**: Responsive chat widget with Tailwind CSS, typing indicators, escalation banners

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Set Up Supabase

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. Go to **SQL Editor** and run the migration from `supabase/migrations/001_create_tables.sql`
4. Go to **Project Settings → API** and copy your:
   - **Project URL** (`NEXT_PUBLIC_SUPABASE_URL`)
   - **Anon public key** (`NEXT_PUBLIC_SUPABASE_ANON_KEY`)

### 3. Configure Environment

```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your Supabase credentials:

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

### 4. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Deployment

### Deploy to Vercel (Free)

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com) and import your repository
3. Add environment variables (`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`)
4. Deploy!

### Supabase Database Setup

Run the SQL migration in your Supabase SQL Editor:
- `supabase/migrations/001_create_tables.sql`

This creates the `conversations`, `escalation_requests`, and `user_profiles` tables with Row Level Security policies.

## Project Structure

```
├── app/                    # Next.js App Router
│   ├── api/chat/route.ts   # Chat API endpoint
│   ├── globals.css         # Global styles (Tailwind)
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Home page
├── components/             # React components
│   ├── chat-widget.tsx     # Main chat widget
│   ├── chat-input.tsx      # Message input
│   ├── message-bubble.tsx  # Message display
│   └── escalation-banner.tsx
├── lib/                    # Business logic
│   ├── nlp/                # NLP pipeline
│   │   ├── intent-classifier.ts
│   │   ├── sentiment-analyzer.ts
│   │   ├── entity-extractor.ts
│   │   └── index.ts
│   ├── dialogue/           # Dialogue management
│   │   ├── manager.ts
│   │   ├── handlers.ts
│   │   ├── escalator.ts
│   │   └── index.ts
│   ├── supabase.ts         # Supabase client
│   └── db.ts               # Database operations (DAO)
├── supabase/               # Supabase configuration
│   └── migrations/         # SQL migrations
├── src/                    # Original Python backend (reference)
└── frontend/               # Original vanilla frontend (reference)
```

## Design Patterns

| Pattern | Location | Purpose |
|---------|----------|---------|
| Strategy | `lib/nlp/intent-classifier.ts` | Swappable classification strategies |
| Factory | `lib/dialogue/handlers.ts` | Intent handler creation |
| Observer | `lib/dialogue/escalator.ts` | Sentiment escalation events |
| DAO | `lib/db.ts` | Database abstraction layer |
| Singleton | `app/api/chat/route.ts` | DialogueManager instance |

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Database**: Supabase PostgreSQL
- **NLP**: Custom TypeScript (sentiment package for AFINN analysis)
- **Deployment**: Vercel + Supabase (free tier)