import { Github, Discord } from "./icons.jsx";

const NAV_LINKS = [
  { href: "#how", label: "How it works" },
  { href: "#why", label: "Why FlowForge" },
  { href: "#journey", label: "Journey" },
  { href: "#contact", label: "Contact" },
];

// Brand block: eagle mark + wordmark + the open-source pill, all one link home.
function Brand() {
  return (
    <a href="#top" className="group flex items-center gap-3" aria-label="FlowForge, back to top">
      <img
        src="/assets/logo.png" alt="FlowForge eagle logo"
        className="h-9 w-9 select-none object-contain transition-transform duration-300 group-hover:scale-110"
      />
      <span className="flex flex-col leading-none">
        <span className="text-lg font-semibold tracking-tight text-zinc-50">
          Flow<span className="text-accent">Forge</span>
        </span>
        <span className="mt-1 hidden text-[10px] font-medium uppercase tracking-[0.22em] text-zinc-500 sm:block">
          Open source · Self hosted
        </span>
      </span>
    </a>
  );
}

// Sticky nav: always blurred in fullpage mode (window never scrolls).
export default function Nav() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-white/[0.06] bg-ink-950/70 backdrop-blur-xl transition-colors duration-500">
      <div className="mx-auto flex h-[4.5rem] max-w-6xl items-center justify-between px-6">
        <Brand />

        <nav className="hidden items-center gap-9 md:flex">
          {NAV_LINKS.map((l) => (
            <a key={l.href} href={l.href} className="group relative text-sm text-zinc-400 transition-colors duration-200 hover:text-zinc-100">
              {l.label}
              <span className="absolute -bottom-1.5 left-0 h-px w-0 bg-accent transition-all duration-300 group-hover:w-full" />
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <a href="https://discord.gg/QQYFBHttFV" target="_blank" rel="noreferrer" aria-label="Join the Discord"
            className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-white/12 text-zinc-300 transition-colors duration-300 hover:border-accent/50 hover:text-white">
            <Discord />
          </a>
          <a href="https://github.com/rufatj" target="_blank" rel="noreferrer"
            className="inline-flex items-center gap-2 rounded-full border border-white/12 px-4 py-1.5 text-sm text-zinc-200 transition-colors duration-300 hover:border-accent/50 hover:text-white">
            <Github /> Follow
          </a>
        </div>
      </div>
    </header>
  );
}
