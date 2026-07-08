import { useEffect, useState } from "react";
import { Github } from "./icons.jsx";

const NAV_LINKS = [
  { href: "#how", label: "How it works" },
  { href: "#why", label: "Why FlowForge" },
  { href: "#journey", label: "Journey" },
  { href: "#contact", label: "Contact" },
];

// Sticky nav that gains a hairline and blur once the page scrolls, so the hero
// reads edge to edge at rest. Underline grows from the left on hover.
export default function Nav() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header className={`fixed inset-x-0 top-0 z-50 transition-colors duration-500 ${scrolled ? "border-b border-white/[0.06] bg-ink-950/70 backdrop-blur-xl" : "border-b border-transparent"}`}>
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <a href="#top" className="text-[15px] font-semibold tracking-tight text-zinc-50">
          Flow<span className="text-accent">Forge</span>
        </a>
        <nav className="hidden items-center gap-9 md:flex">
          {NAV_LINKS.map((l) => (
            <a key={l.href} href={l.href} className="group relative text-sm text-zinc-400 transition-colors duration-200 hover:text-zinc-100">
              {l.label}
              <span className="absolute -bottom-1.5 left-0 h-px w-0 bg-accent transition-all duration-300 group-hover:w-full" />
            </a>
          ))}
        </nav>
        <a href="#contact" className="inline-flex items-center gap-2 rounded-full border border-white/12 px-4 py-1.5 text-sm text-zinc-200 transition-colors duration-300 hover:border-accent/50 hover:text-white">
          <Github /> Follow
        </a>
      </div>
    </header>
  );
}
