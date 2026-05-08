"use client";

import ReactMarkdown from "react-markdown";

interface AssistantMessageProps {
  text: string;
  streaming?: boolean;
}

export default function AssistantMessage({ text, streaming = false }: AssistantMessageProps) {
  return (
    <div className="flex justify-start">
      <div className="max-w-[80%] bg-white border border-logidex-border rounded-[18px] rounded-tl-[4px] px-5 py-4 shadow-[0_1px_6px_rgba(0,0,0,0.05)]">
        <div className="assistant-body">
          <ReactMarkdown>{text}</ReactMarkdown>
          {streaming && (
            <span className="inline-block w-[2px] h-[1.1em] bg-logidex-blue ml-[1px] align-middle animate-pulse" />
          )}
        </div>
      </div>
    </div>
  );
}
