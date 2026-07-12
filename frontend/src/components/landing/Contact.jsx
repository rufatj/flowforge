import Reveal from "../Reveal.jsx";
import Eyebrow from "./Eyebrow.jsx";
import { useTilt } from "../../hooks/useTilt.js";
import { Github, Discord, XTwitter, HuggingFace, Mail, ArrowRight } from "./icons.jsx";

const GITHUB_URL = "https://github.com/rufatj";
const HF_URL = "https://huggingface.co/rufatj";
const X_URL = "https://x.com/rufatjab";
const DISCORD_URL = "https://discord.gg/QQYFBHttFV";
const EMAIL = "rufatjabra@gmail.com";

const CARDS = [
  { href: GITHUB_URL, external: true, icon: <Github className="h-5 w-5" />,
    label: "GitHub", value: "github.com/rufatj", note: "Source, issues, and releases." },
  { href: HF_URL, external: true, icon: <HuggingFace className="h-5 w-5" />,
    label: "Hugging Face", value: "huggingface.co/rufatj", note: "Model weights and datasets." },
  { href: DISCORD_URL, external: true, icon: <Discord className="h-5 w-5" />,
    label: "Discord", value: "Join the community", note: "Ask questions, share workflows." },
  { href: X_URL, external: true, icon: <XTwitter className="h-5 w-5" />,
    label: "X", value: "x.com/rufatjab", note: "Progress notes and releases." },
  { href: `mailto:${EMAIL}`, external: false, icon: <Mail className="h-5 w-5" />,
    label: "Email", value: EMAIL, note: "For questions, ideas, or a hello." },
];

// Each card carries a gentle 3D weight under the cursor, as if it were a
// real object on the page rather than a flat link.
function Card({ card, index }) {
  const tiltRef = useTilt({ max: 7, scale: 1.02 });
  return (
    <Reveal delay={index * 90} className="w-full sm:w-[260px]">
      <a
        ref={tiltRef}
        href={card.href}
        target={card.external ? "_blank" : undefined}
        rel={card.external ? "noreferrer" : undefined}
        className="tilt group flex h-full flex-col rounded-2xl border border-white/[0.08] bg-white/[0.02] p-7 transition-colors duration-300 hover:border-accent/30 hover:bg-white/[0.035] hover:shadow-[0_0_44px_-14px_rgba(56,189,248,0.4)]"
      >
        <span className="flex h-11 w-11 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-accent">
          {card.icon}
        </span>
        <span className="mt-5 text-sm text-zinc-500">{card.label}</span>
        <span className="mt-1 flex items-center gap-1.5 text-[15px] font-medium text-zinc-100">
          {card.value}
          <ArrowRight className="h-4 w-4 text-accent opacity-0 transition-all duration-300 group-hover:translate-x-0.5 group-hover:opacity-100" />
        </span>
        <span className="mt-2 text-sm text-zinc-500">{card.note}</span>
      </a>
    </Reveal>
  );
}

// Closing invitation. Five glowing, weighted contact cards with real detail,
// so the page ends on a person and a community rather than a form.
export default function Contact() {
  return (
    <section id="contact" className="scroll-mt-24 py-28">
      <div className="mx-auto max-w-4xl px-6">
        <Eyebrow label="Say hello" title="Let us build something quietly powerful" align="center" />

        <div className="mt-14 flex flex-wrap justify-center gap-5">
          {CARDS.map((c, i) => <Card key={c.label} card={c} index={i} />)}
        </div>
      </div>
    </section>
  );
}
