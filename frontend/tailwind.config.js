/** @type {import('tailwindcss').Config} */
// Dark, developer-grade. Near-black inks + one restrained cyan accent.
// No purple, no gradient washes. Reference feel: Linear, Vercel, Cursor.
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Deep near-black surfaces (not pure black).
        ink: {
          950: "#050508",
          900: "#08080c",
          850: "#0b0b11",
          800: "#101017",
        },
        // Single accent family: light blue / cyan. Used sparingly.
        accent: {
          DEFAULT: "#38bdf8",
          light: "#7dd3fc",
          bright: "#22d3ee",
          dim: "#0ea5e9",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
};
