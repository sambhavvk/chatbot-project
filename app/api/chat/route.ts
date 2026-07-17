/**
 * Chat API Route - Next.js Route Handler
 * Replaces the Python AWS Lambda handler.
 * Processes chat messages through the NLP pipeline and persists to Supabase.
 */

import { NextRequest, NextResponse } from "next/server";
import { DialogueManager } from "@/lib/dialogue";
import { saveMessage, createEscalationRequest } from "@/lib/db";

// Singleton DialogueManager (persists across requests in the same process)
let manager: DialogueManager | null = null;

function getManager(): DialogueManager {
  if (!manager) {
    manager = new DialogueManager();
  }
  return manager;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const userId = body.user_id || "anonymous";
    const message = body.message;

    if (!message || typeof message !== "string" || message.trim() === "") {
      return NextResponse.json(
        { error: "message field is required" },
        { status: 400 }
      );
    }

    // Process through the NLP pipeline
    const dm = getManager();
    const result = dm.handle_message(userId, message);

    // Persist to Supabase (non-blocking - don't fail the response if DB fails)
    try {
      await saveMessage(
        userId,
        message,
        result.response,
        result.intent,
        result.confidence,
        result.sentiment,
        result.escalated
      );

      if (result.escalated) {
        await createEscalationRequest(
          userId,
          `Negative sentiment detected: compound=${result.sentiment.compound}`,
          result.sentiment,
          message
        );
      }
    } catch (dbError) {
      console.error("Failed to persist to Supabase:", dbError);
      // Continue - don't fail the chat response due to DB issues
    }

    return NextResponse.json({
      response: result.response,
      intent: result.intent,
      confidence: result.confidence,
      entities: result.entities,
      sentiment: result.sentiment,
      escalated: result.escalated,
      timestamp: result.timestamp,
    });
  } catch (error) {
    console.error("Error processing chat request:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

// Handle CORS preflight
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}