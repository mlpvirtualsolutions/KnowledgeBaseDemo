"use client";

import { useState, useRef } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function handleSubmit() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  function handleInput(e: React.FormEvent<HTMLTextAreaElement>) {
    const t = e.currentTarget;
    t.style.height = "auto";
    t.style.height = `${t.scrollHeight}px`;
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-logidex-bg pb-7 pt-3">
      <div className="max-w-[660px] mx-auto px-4">
        <div className="flex items-center gap-3 bg-white border border-logidex-border rounded-full pl-6 pr-[10px] py-[10px] shadow-[0_2px_12px_rgba(0,0,0,0.07)]">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            onInput={handleInput}
            placeholder="Ask anything about your operations..."
            disabled={disabled}
            rows={1}
            className="flex-1 resize-none bg-transparent outline-none text-[0.9rem] text-logidex-text-dark placeholder:text-logidex-muted-light leading-relaxed max-h-[140px] overflow-y-auto"
          />
          <button
            onClick={handleSubmit}
            disabled={disabled || !value.trim()}
            className="flex-shrink-0 w-9 h-9 bg-logidex-blue hover:bg-logidex-blue-hover disabled:opacity-40 rounded-full flex items-center justify-center transition-colors duration-150 cursor-pointer disabled:cursor-default"
          >
            <svg
              width="15"
              height="15"
              viewBox="0 0 24 24"
              fill="none"
              stroke="white"
              strokeWidth="2.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="12" y1="19" x2="12" y2="5" />
              <polyline points="5 12 12 5 19 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
