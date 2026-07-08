import Reveal from "../components/Reveal.jsx";

// About: luxury voice, no dashes in prose, product first.
export default function About() {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <Reveal as="h1" className="text-3xl font-semibold tracking-tight text-zinc-50">
        About FlowForge
      </Reveal>
      <Reveal as="p" delay={80} className="text-[15px] leading-relaxed text-zinc-300">
        FlowForge is your local n8n copilot. It turns a plain language description of an automation
        into a valid, importable n8n workflow using a Gemma model fine tuned with LoRA on an AMD
        MI300X and served with vLLM. The backend routes between a Fireworks endpoint for development
        and your own AMD endpoint for the live demo, so your prompts and workflows never leave your
        infrastructure.
      </Reveal>
      <Reveal as="p" delay={140} className="text-sm leading-relaxed text-zinc-500">
        Backend, FastAPI. Frontend, React with Vite and Tailwind. Evaluation, a three gate live
        import harness. Training, Unsloth LoRA on ROCm.
      </Reveal>
    </div>
  );
}
