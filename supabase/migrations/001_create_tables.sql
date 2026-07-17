-- Supabase PostgreSQL Schema for Banking Chatbot
-- Replaces DynamoDB tables: Conversations, EscalationRequests, UserProfiles

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Conversations table (replaces DynamoDB Conversations table)
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    intent TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 0.0,
    sentiment_neg REAL NOT NULL DEFAULT 0.0,
    sentiment_neu REAL NOT NULL DEFAULT 0.0,
    sentiment_pos REAL NOT NULL DEFAULT 0.0,
    sentiment_compound REAL NOT NULL DEFAULT 0.0,
    escalated BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for fast user conversation lookups
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp DESC);

-- Escalation requests table (replaces DynamoDB EscalationRequests table)
CREATE TABLE IF NOT EXISTS escalation_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reason TEXT NOT NULL,
    message TEXT,
    sentiment_compound REAL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for escalation lookups
CREATE INDEX IF NOT EXISTS idx_escalations_user_id ON escalation_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_escalations_status ON escalation_requests(status);

-- User profiles table (replaces DynamoDB UserProfiles table)
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id TEXT PRIMARY KEY,
    display_name TEXT,
    email TEXT,
    preferences JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable Row Level Security (RLS) for Supabase
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE escalation_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Allow anonymous access for demo purposes
-- In production, you'd restrict these to authenticated users
CREATE POLICY "Allow anonymous read conversations" ON conversations
    FOR SELECT USING (true);

CREATE POLICY "Allow anonymous insert conversations" ON conversations
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anonymous read escalations" ON escalation_requests
    FOR SELECT USING (true);

CREATE POLICY "Allow anonymous insert escalations" ON escalation_requests
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anonymous read profiles" ON user_profiles
    FOR SELECT USING (true);

CREATE POLICY "Allow anonymous insert profiles" ON user_profiles
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anonymous update profiles" ON user_profiles
    FOR UPDATE USING (true);