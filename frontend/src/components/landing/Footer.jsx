import { Github, Discord, XTwitter, HuggingFace, Mail } from "./icons.jsx";

const GITHUB_URL = "https://github.com/rufatj";
const HF_URL = "https://huggingface.co/rufatj";
const X_URL = "https://x.com/rufatjab";
const DISCORD_URL = "https://discord.gg/QQYFBHttFV";
const EMAIL = "rufatjabra@gmail.com";

const SOCIALS = [
  { href: GITHUB_URL, label: "GitHub", icon: Github },
  { href: DISCORD_URL, label: "Discord", icon: Discord },
  { href: HF_URL, label: "Hugging Face", icon: HuggingFace },
  { href: X_URL, label: "X", icon: XTwitter },
  { href: `mailto:${EMAIL}`, label: "Email", icon: Mail },
];

const COLUMNS = [
  { heading: "Product", links: [
    { label: "How it works", href: "#how" },
    { label: "Why FlowForge", href: "#why" },
    { label: "Journey", href: "#journey" },
    { label: "Contact", href: "#contact" },
  ] },
  { heading: "Resources", links: [
    { label: "Source code", href: GITHUB_URL, external: true },
    { label: "Model weights", href: HF_URL, external: true },
    { label: "Dataset", href: "#" },
    { label: "License (MIT)", href: "#" },
  ] },
  { heading: "Community", links: [
    { label: "Discord", href: DISCORD_URL, external: true },
    { label: "X / Twitter", href: X_URL, external: true },
    { label: "Hugging Face", href: HF_URL, external: true },
    { label: "Email us", href: `mailto:${EMAIL}` },
  ] },
];

// A proper closing footer: brand and mission up top, a real sitemap of
// columns beneath it, and a quiet legal line at the very bottom.
export default function Footer() {
  return (
    <footer className="border-t border-white/[0.06]">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="grid gap-12 md:grid-cols-[1.3fr_repeat(3,1fr)]">
          <div>
            <a href="#top" className="group inline-flex items-center gap-2.5" aria-label="FlowForge, back to top">
              <img
                src="/assets/logo.png"
                alt="FlowForge eagle logo"
                className="h-8 w-8 select-none object-contain transition-transform duration-300 group-hover:scale-110"
              />
              <span className="text-lg font-semibold tracking-tight text-zinc-50">
                Flow<span className="text-accent">Forge</span>
              </span>
            </a>
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-zinc-500">
              Your local n8n copilot. Open weights, open evaluation, and automations that run on
              hardware you own.
            </p>
            <div className="mt-6 flex items-center gap-3 text-zinc-500">
              {SOCIALS.map(({ href, label, icon: Icon }) => (
                <a
                  key={label}
                  href={href}
                  target={href.startsWith("mailto:") ? undefined : "_blank"}
                  rel={href.startsWith("mailto:") ? undefined : "noreferrer"}
                  aria-label={label}
                  className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-white/10 transition-colors duration-200 hover:border-accent/40 hover:text-zinc-100"
                >
                  <Icon className="h-4 w-4" />
                </a>
              ))}
            </div>
          </div>

          {COLUMNS.map((col) => (
            <div key={col.heading}>
              <h3 className="text-[11px] font-medium uppercase tracking-[0.22em] text-zinc-500">{col.heading}</h3>
              <ul className="mt-4 space-y-3">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <a
                      href={l.href}
                      target={l.external ? "_blank" : undefined}
                      rel={l.external ? "noreferrer" : undefined}
                      className="text-sm text-zinc-400 transition-colors duration-200 hover:text-zinc-100"
                    >
                      {l.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-14 flex flex-col items-start justify-between gap-3 border-t border-white/[0.05] pt-6 text-sm text-zinc-600 sm:flex-row sm:items-center">
          <p>&copy; {new Date().getFullYear()} FlowForge. Open source under the MIT license.</p>
          <p className="text-zinc-600">Built solo, shipped self hosted.</p>
        </div>
      </div>
    </footer>
  );
}
