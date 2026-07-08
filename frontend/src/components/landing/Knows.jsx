import Reveal from "../Reveal.jsx";
import Eyebrow from "./Eyebrow.jsx";

const TAGS = [
  "Webhook", "HTTP Request", "IF", "Switch", "Loop Over Items", "Google Sheets",
  "Telegram", "Slack", "Gmail", "AI Agent", "LangChain Tools", "Memory Buffer",
];

// Full-bleed showcase: the integration image spans the whole viewport width and
// its top and bottom fade into the page, so it reads as part of the canvas
// rather than a boxed screenshot. Copy and node tags sit over the fade.
export default function Knows() {
  return (
    <section id="knows" className="scroll-mt-24 py-28">
      <div className="mx-auto max-w-6xl px-6">
        <Eyebrow label="Depth" title="Built on real workflows" align="center" />
      </div>

      <div className="relative mt-4 w-full overflow-hidden">
        <Reveal className="w-screen ml-[calc(50%-50vw)] mr-[calc(50%-50vw)]">
          <img
            src="/assets/integration-ways.png"
            alt="A central engine wired to Gmail, Google Drive, Slack, Teams, Zoom and WhatsApp"
            className="h-[46vh] min-h-[320px] w-full select-none object-cover sm:h-[62vh]"
            style={{ WebkitMaskImage: "linear-gradient(to bottom, transparent, #000 22%, #000 78%, transparent)",
              maskImage: "linear-gradient(to bottom, transparent, #000 22%, #000 78%, transparent)" }}
          />
        </Reveal>
      </div>

      <div className="mx-auto -mt-6 max-w-3xl px-6">
        <Reveal as="p" className="text-center text-[15px] leading-relaxed text-zinc-400">
          The model learned from thousands of community workflows spanning webhooks, HTTP requests,
          conditional and switch logic, loops over items, Google Sheets, Telegram, Slack, Gmail, and
          the modern AI Agent node with its tools and memory. It understands the exact JSON shape n8n
          expects.
        </Reveal>
        <Reveal delay={100} className="mt-8 flex flex-wrap justify-center gap-2">
          {TAGS.map((tag) => (
            <span key={tag} className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 font-mono text-[13px] text-zinc-400 transition-colors duration-200 hover:border-accent/30 hover:text-zinc-200">
              {tag}
            </span>
          ))}
        </Reveal>
      </div>
    </section>
  );
}
