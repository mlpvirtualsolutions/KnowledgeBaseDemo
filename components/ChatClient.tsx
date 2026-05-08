"use client";

import { useState, useRef, useEffect } from "react";
import ChatHero from "./ChatHero";
import UserBubble from "./UserBubble";
import AssistantMessage from "./AssistantMessage";
import ChatInput from "./ChatInput";

interface Message {
  role: "user" | "assistant";
  text: string;
  streaming?: boolean;
}

interface ChatClientProps {
  companyName: string;
}

export default function ChatClient({ companyName }: ChatClientProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend(text: string) {
    setMessages((prev) => [...prev, { role: "user", text }]);
    setIsStreaming(true);
    setMessages((prev) => [
      ...prev,
      { role: "assistant", text: "", streaming: true },
    ]);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      if (!res.ok || !res.body) {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            text: "Something went wrong. Please try again.",
            streaming: false,
          };
          return updated;
        });
        setIsStreaming(false);
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          updated[updated.length - 1] = { ...last, text: last.text + chunk };
          return updated;
        });
      }

      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          ...updated[updated.length - 1],
          streaming: false,
        };
        return updated;
      });
    } catch {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          text: "Something went wrong. Please try again.",
          streaming: false,
        };
        return updated;
      });
    }

    setIsStreaming(false);
  }

  return (
    <>
      <div className="pt-[60px] pb-[96px] min-h-screen">
        {messages.length === 0 ? (
          <ChatHero companyName={companyName} />
        ) : (
          <div className="max-w-[720px] mx-auto px-4 pt-8 flex flex-col gap-5">
            {messages.map((msg, i) =>
              msg.role === "user" ? (
                <UserBubble key={i} text={msg.text} />
              ) : (
                <AssistantMessage
                  key={i}
                  text={msg.text}
                  streaming={msg.streaming}
                />
              )
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <ChatInput onSend={handleSend} disabled={isStreaming} />
    </>
  );
}
