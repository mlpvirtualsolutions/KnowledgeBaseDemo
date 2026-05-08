"use client";

const NAV_LINKS = [
  { label: "Chat",      active: true  },
  { label: "Dashboard", active: false },
  { label: "Handbook",  active: false },
  { label: "Team",      active: false },
];

interface NavbarProps {
  userEmail?: string;
}

export default function Navbar({ userEmail = "" }: NavbarProps) {
  return (
    <nav className="fixed top-0 left-0 right-0 h-[60px] bg-logidex-navy flex items-center px-7 z-[9999] gap-8">

      {/* Brand */}
      <div className="text-[1.05rem] font-extrabold tracking-[0.04em] text-white flex-shrink-0">
        LOGI<span className="text-logidex-blue">DEX</span>
      </div>

      {/* Nav links */}
      <div className="flex gap-1 flex-1">
        {NAV_LINKS.map(({ label, active }) => (
          <span
            key={label}
            className={`text-[0.85rem] font-medium px-[14px] py-[6px] rounded-lg cursor-default transition-colors duration-150 ${
              active ? "bg-white/10 text-white" : "text-[#94a3b8]"
            }`}
          >
            {label}
          </span>
        ))}
      </div>

      {/* Right: email pill + sign-out */}
      <div className="flex items-center gap-[10px]">
        {userEmail && (
          <span className="bg-white/[.08] border border-white/[.12] text-[#cbd5e1] text-[0.8rem] font-medium px-[14px] py-[5px] rounded-full flex-shrink-0">
            {userEmail}
          </span>
        )}
        <a
          href="/login"
          className="text-[#64748b] text-[0.78rem] font-medium no-underline px-[11px] py-1 rounded-[6px] border border-white/[.15] whitespace-nowrap transition-colors duration-150 hover:text-white hover:border-white/[.35]"
        >
          Sign out
        </a>
      </div>
    </nav>
  );
}
