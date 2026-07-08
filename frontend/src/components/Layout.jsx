import { NavLink, Link } from "react-router-dom";
import AuroraBackground from "./AuroraBackground.jsx";

// App-shell chrome for the tool pages. Same living canvas as the landing:
// near-black ink surfaces, drifting aurora, hairline borders, one cyan accent.

const links = [
  { to: "/generate", label: "Generate" },
  { to: "/result", label: "Result" },
  { to: "/proof", label: "Proof" },
  { to: "/about", label: "About" },
];

export default function Layout({ children }) {
  return (
    <div className="relative min-h-screen flex flex-col">
      <AuroraBackground />
      <header className="border-b border-white/[0.06] bg-ink-950/70 backdrop-blur-md">
        <div className="max-w-5xl w-full mx-auto px-6 h-16 flex items-center gap-8">
          <Link to="/" className="font-semibold tracking-tight text-zinc-50">
            Flow<span className="text-accent">Forge</span>
          </Link>
          <nav className="flex gap-1 text-sm">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md transition-colors duration-200 ${
                    isActive
                      ? "bg-white/[0.06] text-zinc-100"
                      : "text-zinc-400 hover:text-zinc-100"
                  }`
                }
              >
                {l.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-12">{children}</main>
      <footer className="border-t border-white/[0.06] text-xs text-zinc-600">
        <div className="max-w-5xl mx-auto px-6 py-4">
          FlowForge, the open self hosted alternative to n8n's AI copilot · MIT
        </div>
      </footer>
    </div>
  );
}
