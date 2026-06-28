import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#0b0c10",
          light: "#16181d",
          lighter: "#1f2228",
        },
        gold: {
          DEFAULT: "#caa53d",
          bright: "#f1c84a",
          dim: "#8a722c",
        },
        parchment: "#e9e4d3",
      },
      fontFamily: {
        sans: ["var(--font-body)", "ui-sans-serif", "system-ui"],
        display: ["var(--font-display)", "serif"],
      },
      boxShadow: {
        card: "0 4px 20px rgba(0,0,0,0.5)",
        glow: "0 0 12px rgba(202,165,61,0.5)",
      },
    },
  },
  plugins: [],
};

export default config;
