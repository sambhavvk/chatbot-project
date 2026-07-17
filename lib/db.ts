/**
 * Database Operations - DAO Pattern (Supabase PostgreSQL).
 * Replaces the Python DynamoDBClient.
 * Handles conversation logging, escalation requests, and user profiles.
 */

import { supabase } from "./supabase";

// ─── Conversation Operations ───────────────────────────────────────

export interface ConversationRecord {
  id?: string;
  user_id: string;
  timestamp: string;
  user_message: string;
  bot_response: string;
  intent: string;
  confidence: number;
  sentiment_neg: number;
  sentiment_neu: number;
  sentiment_pos: number;
  sentiment_compound: number;
  escalated: boolean;
}

export async function saveMessage(
  userId: string,
  message: string,
  response: string,
  intent: string,
  confidence: number,
  sentiment: { neg: number; neu: number; pos: number; compound: number },
  escalated: boolean = false
): Promise<void> {
  const record: Omit<ConversationRecord, "id"> = {
    user_id: userId,
    timestamp: new Date().toISOString(),
    user_message: message,
    bot_response: response,
    intent,
    confidence,
    sentiment_neg: sentiment.neg,
    sentiment_neu: sentiment.neu,
    sentiment_pos: sentiment.pos,
    sentiment_compound: sentiment.compound,
    escalated,
  };

  const { error } = await supabase.from("conversations").insert(record);

  if (error) {
    console.error("Failed to save conversation:", error.message);
    throw new Error(`Database error: ${error.message}`);
  }
}

export async function getRecentConversation(
  userId: string,
  limit: number = 10
): Promise<ConversationRecord[]> {
  const { data, error } = await supabase
    .from("conversations")
    .select("*")
    .eq("user_id", userId)
    .order("timestamp", { ascending: false })
    .limit(limit);

  if (error) {
    console.error("Failed to fetch conversations:", error.message);
    return [];
  }

  return data || [];
}

// ─── Escalation Operations ─────────────────────────────────────────

export interface EscalationRecord {
  id?: string;
  user_id: string;
  timestamp: string;
  reason: string;
  message?: string;
  sentiment_compound?: number;
  status: string;
}

export async function createEscalationRequest(
  userId: string,
  reason: string,
  sentiment?: { compound: number },
  message?: string
): Promise<string> {
  const record: Omit<EscalationRecord, "id"> = {
    user_id: userId,
    timestamp: new Date().toISOString(),
    reason,
    message,
    sentiment_compound: sentiment?.compound,
    status: "pending",
  };

  const { data, error } = await supabase
    .from("escalation_requests")
    .insert(record)
    .select("id")
    .single();

  if (error) {
    console.error("Failed to create escalation:", error.message);
    throw new Error(`Database error: ${error.message}`);
  }

  return data.id;
}

// ─── User Profile Operations ───────────────────────────────────────

export interface UserProfile {
  user_id: string;
  display_name?: string;
  email?: string;
  preferences?: Record<string, unknown>;
}

export async function saveUserProfile(
  userId: string,
  profile: Partial<UserProfile>
): Promise<void> {
  const { error } = await supabase.from("user_profiles").upsert(
    {
      user_id: userId,
      ...profile,
      updated_at: new Date().toISOString(),
    },
    { onConflict: "user_id" }
  );

  if (error) {
    console.error("Failed to save user profile:", error.message);
    throw new Error(`Database error: ${error.message}`);
  }
}

export async function getUserProfile(
  userId: string
): Promise<UserProfile | null> {
  const { data, error } = await supabase
    .from("user_profiles")
    .select("*")
    .eq("user_id", userId)
    .single();

  if (error) {
    if (error.code === "PGRST116") return null; // Not found
    console.error("Failed to fetch user profile:", error.message);
    return null;
  }

  return data;
}