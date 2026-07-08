import Reveal from "../Reveal.jsx";

// Luxury section header: a tracked uppercase eyebrow, a large title, and a
// short accent rule that draws attention without shouting.
export default function Eyebrow({ label, title, align = "left" }) {
  const alignment = align === "center" ? "items-center text-center" : "items-start text-left";
  return (
    <div className={`flex flex-col ${alignment}`}>
      <Reveal as="span" className="text-[11px] font-medium uppercase tracking-[0.28em] text-accent/80">
        {label}
      </Reveal>
      <Reveal as="h2" delay={80} className="mt-4 max-w-2xl text-3xl font-semibold tracking-tight text-zinc-50 sm:text-4xl">
        {title}
      </Reveal>
      <Reveal delay={140} className={`mt-5 h-px w-16 bg-gradient-to-r from-accent to-transparent ${align === "center" ? "mx-auto" : ""}`} />
    </div>
  );
}
