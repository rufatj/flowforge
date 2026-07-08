import Reveal from "../Reveal.jsx";
import Eyebrow from "./Eyebrow.jsx";
import { Github, Mail, ArrowRight } from "./icons.jsx";

const GITHUB_URL = "https://github.com/rufatj";
const EMAIL = "rufatjabra@gmail.com";

const CARDS = [
  { href: GITHUB_URL, external: true, icon: <Github className="h-5 w-5" />,
    label: "GitHub", value: "github.com/rufatj", note: "Source, issues, and releases." },
  { href: `mailto:${EMAIL}`, external: false, icon: <Mail className="h-5 w-5" />,
    label: "Email", value: EMAIL, note: "For questions, ideas, or a hello." },
];

// Closing invitation. Two large, glowing contact cards with real detail, so
// the page ends on a person rather than a form.
export default function Contact() {
  return (
    <section id="contact" className="scroll-mt-24 py-28">
      <div className="mx-auto max-w-3xl px-6">
        <Eyebrow label="Say hello" title="Let us build something quietly powerful" align="center" />

        <div className="mt-14 grid gap-5 sm:grid-cols-2">
          {CARDS.map((c, i) => (
            <Reveal key={c.label} delay={i * 110}>
              <a href={c.href} target={c.external ? "_blank" : undefined} rel={c.external ? "noreferrer" : undefined}
                className="group flex h-full flex-col rounded-2xl border border-white/[0.08] bg-white/[0.02] p-7 transition-all duration-300 hover:border-accent/30 hover:bg-white/[0.035] hover:shadow-[0_0_44px_-14px_rgba(56,189,248,0.4)]">
                <span className="flex h-11 w-11 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-accent">
                  {c.icon}
                </span>
                <span className="mt-5 text-sm text-zinc-500">{c.label}</span>
                <span className="mt-1 flex items-center gap-1.5 text-[15px] font-medium text-zinc-100">
                  {c.value}
                  <ArrowRight className="h-4 w-4 text-accent opacity-0 transition-all duration-300 group-hover:translate-x-0.5 group-hover:opacity-100" />
                </span>
                <span className="mt-2 text-sm text-zinc-500">{c.note}</span>
              </a>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
