import { ChatWidget } from "@/components/chat-widget";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-primary-light to-accent flex items-center justify-center p-4">
      <ChatWidget />
    </main>
  );
}