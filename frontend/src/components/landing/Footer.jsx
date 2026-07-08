import { Github, Mail } from "./icons.jsx";

const GITHUB_URL = "https://github.com/rufatj";
const EMAIL = "rufatjabra@gmail.com";
const LINKS = [
  { href: GITHUB_URL, label: "GitHub", external: true },
  { href: "#", label: "Model on Hugging Face", external: true },
  { href: "#", label: "Dataset", external: true },
  { href: "#", label: "License", external: true },
];

export default function Footer() {
  return (
    <footer className="border-t border-white/[0.06]">
      <div className="mx-auto max-w-6xl px-6 py-14">
        <div className="flex flex-col items-start justify-between gap-8 sm:flex-row sm:items-center">
          <div>
            <span className="text-[15px] font-semibold tracking-tight text-zinc-50">
              Flow<span className="text-accent">Forge</span>
            </span>
            <p className="mt-2 max-w-xs text-sm text-zinc-500">
              Your local n8n copilot. Fine tuned on AMD MI300X, served on hardware you own.
            </p>
          </div>
          <nav className="flex flex-wrap gap-x-6 gap-y-2">
            {LINKS.map((l) => (
              <a key={l.label} href={l.href} target={l.external ? "_blank" : undefined} rel={l.external ? "noreferrer" : undefined}
                className="text-sm text-zinc-400 transition-colors duration-200 hover:text-zinc-100">
                {l.label}
              </a>
            ))}
          </nav>
        </div>
        <div className="mt-10 flex flex-col items-start justify-between gap-4 border-t border-white/[0.05] pt-6 sm:flex-row sm:items-center">
          <p className="text-sm text-zinc-600">Open source under the MIT license.</p>
          <div className="flex items-center gap-4 text-zinc-500">
            <a href={GITHUB_URL} target="_blank" rel="noreferrer" aria-label="GitHub" className="transition-colors duration-200 hover:text-zinc-200"><Github className="h-4 w-4" /></a>
            <a href={`mailto:${EMAIL}`} aria-label="Email" className="transition-colors duration-200 hover:text-zinc-200"><Mail className="h-4 w-4" /></a>
          </div>
        </div>
      </div>
    </footer>
  );
}
