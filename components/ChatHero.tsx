const HINTS = [
  "Ask about your handbook",
  "Ask about a process",
  "Ask for troubleshooting help",
];

interface ChatHeroProps {
  companyName: string;
}

export default function ChatHero({ companyName }: ChatHeroProps) {
  return (
    <div className="flex flex-col items-center text-center px-4 pt-[110px] pb-10">

      {/* Label */}
      <p className="text-[0.72rem] font-semibold tracking-[0.13em] uppercase text-logidex-muted mb-7">
        {companyName} ASSISTANT
      </p>

      {/* Heading */}
      <h1 className="text-[2.6rem] font-extrabold text-logidex-navy leading-[1.15] mb-4">
        What do you need to{" "}
        <span className="text-logidex-blue">know?</span>
      </h1>

      {/* Subtitle */}
      <p className="text-[0.95rem] text-logidex-muted mb-10 max-w-[480px] leading-relaxed">
        Answers pulled directly from your company knowledge base.
      </p>

      {/* Static hint chips */}
      <div className="flex flex-col gap-[10px] w-full max-w-[640px]">
        {HINTS.map((hint) => (
          <div
            key={hint}
            className="bg-white border border-logidex-border rounded-2xl px-6 py-[14px] text-[0.9rem] text-logidex-text cursor-default select-none shadow-[0_1px_4px_rgba(0,0,0,0.04)]"
          >
            {hint}
          </div>
        ))}
      </div>

      {/* Powered by */}
      <p className="text-[0.78rem] text-logidex-muted mt-10">
        Powered by{" "}
        <span className="text-logidex-blue font-semibold">Logidex</span>
      </p>
    </div>
  );
}
