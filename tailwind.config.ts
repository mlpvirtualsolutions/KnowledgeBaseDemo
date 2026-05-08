import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "logidex-bg":          "#edf1f8",
        "logidex-navy":        "#0f172a",
        "logidex-blue":        "#3b82f6",
        "logidex-blue-hover":  "#2563eb",
        "logidex-blue-light":  "#eff6ff",
        "logidex-blue-border": "#bfdbfe",
        "logidex-border":      "#e2e8f0",
        "logidex-muted":       "#64748b",
        "logidex-muted-light": "#94a3b8",
        "logidex-text":        "#374151",
        "logidex-text-dark":   "#1e293b",
      },
      fontFamily: {
        inter: ["Inter", "sans-serif"],
      },
      maxWidth: {
        chat: "760px",
      },
    },
  },
  plugins: [],
};

export default config;
