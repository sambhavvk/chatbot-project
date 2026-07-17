"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { MessageBubble } from "./message-bubble";
import { ChatInput } from "./chat-input";
import { EscalationBanner } from "./escalation-banner";

interface Message {
  id: string;
  type: "user" | "bot";
  text: string;
  meta?: {
    intent: string;
    confidence: number;
  };
}

// Generate a persistent user ID for this session
const USER_ID =
  "web-user-" + Math.random().toString(36).substring(2, 8);

export function ChatWidget() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      type: "bot",
      text:
        "Hello! Welcome to our virtual assistant. I can help with balance inquiries, " +
        "transactions, card services, loans, and more. How can I assist you today?",
      meta: { intent: "greeting", confidence: 1 },
    },
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showEscalation, setShowEscalation] = useState(false);
  const [statusText, setStatusText] = useState("● Online");

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = useCallback(
    async (text: string) => {
      if (isProcessing) return;

      // Add user message
      const userMsg: Message = {
        id: Date.now().toString(),
        type: "user",
        text,
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsProcessing(true);
      setStatusText("● Typing...");

      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: USER_ID, message: text }),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        // Add bot response
        const botMsg: Message = {
          id: (Date.now() + 1).toString(),
          type: "bot",
          text: data.response,
          meta: {
            intent: data.intent,
            confidence: data.confidence,
          },
        };
        setMessages((prev) => [...prev, botMsg]);

        // Handle escalation
        if (data.escalated) {
          setShowEscalation(true);
        }
      } catch (error) {
        console.error("Chat error:", error);
        const errorMsg: Message = {
          id: (Date.now() + 1).toString(),
          type: "bot",
          text: "Sorry, I encountered an error. Please try again later.",
        };
        setMessages((prev) => [...prev, errorMsg]);
      } finally {
        setIsProcessing(false);
        setStatusText("● Online");
      }
    },
    [isProcessing]
  );

  const handleDismissEscalation = useCallback(() => {
    setShowEscalation(false);
  }, []);

  return (
    <div className="w-full max-w-[480px] h-[90vh] max-h-[700px] bg-white rounded-2xl shadow-2xl shadow-primary/20 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-light to-accent px-5 py-4 flex items-center gap-3">
        <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center text-xl">
          🤖
        </div>
        <div className="flex-1">
          <h1 className="text-white font-semibold text-base">
            Virtual Assistant
          </h1>
          <p className="text-white/70 text-xs">{statusText}</p>
        </div>
      </div>

      {/* Escalation Banner */}
      <EscalationBanner
        show={showEscalation}
        onDismiss={handleDismissEscalation}
      />

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50">
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            type={msg.type}
            text={msg.text}
            meta={msg.meta}
          />
        ))}

        {/* Typing Indicator */}
        {isProcessing && (
          <div className="flex gap-3 animate-fade-in">
            <div className="flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center text-lg shadow-md bg-gradient-to-br from-gray-700 to-gray-800">
              🤖
            </div>
            <div className="bg-white rounded-2xl rounded-tl-md px-4 py-3 border border-gray-100 shadow-sm">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-typing-bounce" />
                <span
                  className="w-2 h-2 bg-gray-400 rounded-full animate-typing-bounce"
                  style={{ animationDelay: "0.2s" }}
                />
                <span
                  className="w-2 h-2 bg-gray-400 rounded-full animate-typing-bounce"
                  style={{ animationDelay: "0.4s" }}
                />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <ChatInput onSendMessage={handleSendMessage} disabled={isProcessing} />
    </div>
  );
}