import { Link } from "react-router-dom";
import Reveal from "../Reveal.jsx";
import { Github, ArrowRight } from "./icons.jsx";

const GITHUB_URL = "https://github.com/rufatj";

// A quiet, centered climax. The primary action glows softly; the secondary
// stays understated. Both are large touch targets.
export default function GetStarted() {
  return (
    <section id="start" className="scroll-mt-24 py-28">
      <div className="mx-auto max-w-2xl px-6 text-center">
        <Reveal as="h2" className="text-3xl font-semibold tracking-tight text-zinc-50 sm:text-4xl">
          Try it now, or host it yourself
        </Reveal>
        <Reveal delay={100} className="mx-auto mt-5 h-px w-16 bg-gradient-to-r from-transparent via-accent to-transparent" />

        <Reveal delay={140} className="mt-10 flex flex-col justify-center gap-3 sm:flex-row">
          <Link to="/generate"
            className="group inline-flex items-center justify-center gap-2 rounded-full bg-accent px-6 py-3 text-sm font-medium text-ink-950 shadow-[0_0_28px_-6px_rgba(56,189,248,0.7)] transition-all duration-300 hover:bg-accent-light hover:shadow-[0_0_36px_-4px_rgba(56,189,248,0.9)]">
            Try the demo
            <ArrowRight className="h-4 w-4 transition-transform duration-300 group-hover:translate-x-0.5" />
          </Link>
          <a href={GITHUB_URL} target="_blank" rel="noreferrer"
            className="inline-flex items-center justify-center gap-2 rounded-full border border-white/15 px-6 py-3 text-sm font-medium text-zinc-200 transition-colors duration-300 hover:border-accent/40 hover:bg-white/[0.03]">
            <Github /> Clone on GitHub
          </a>
        </Reveal>

        <Reveal as="p" delay={200} className="mt-8 text-sm text-zinc-500">
          MIT licensed. Run it on your own n8n instance. Fine tune it on your own workflows.
        </Reveal>
      </div>
    </section>
  );
}
