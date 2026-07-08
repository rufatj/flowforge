// Living background: two slow-drifting cyan light fields over deep ink, plus a
// fine grain and a top vignette. Fixed behind all content, never interactive.
// This is the "theme that shifts" layer, kept dark so the dark media blend in.
export default function AuroraBackground() {
  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 -z-10 overflow-hidden bg-ink-950">
      <div
        className="animate-aurora absolute -top-1/3 left-1/4 h-[70vh] w-[70vh] rounded-full blur-3xl"
        style={{ background: "radial-gradient(circle, rgba(56,189,248,0.16), transparent 60%)" }}
      />
      <div
        className="animate-aurora absolute top-1/2 -right-1/4 h-[80vh] w-[80vh] rounded-full blur-3xl"
        style={{ background: "radial-gradient(circle, rgba(14,165,233,0.12), transparent 60%)", animationDelay: "-13s" }}
      />
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
        }}
      />
      <div
        className="absolute inset-x-0 top-0 h-64"
        style={{ background: "linear-gradient(to bottom, rgba(56,189,248,0.05), transparent)" }}
      />
    </div>
  );
}
