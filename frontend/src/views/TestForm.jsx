// View 3 — Test form. Renders the HTML returned by POST /testform in an iframe
// so the user can trigger the webhook live. Placeholder for the skeleton.
export default function TestForm() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">Test form</h1>
      <p className="text-zinc-400">
        For workflows that start with a webhook, FlowForge generates a small HTML
        form. It will render here in an iframe so you can fire the workflow live.
      </p>
      <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-8 text-center text-sm text-zinc-500">
        Generate a webhook workflow first — the test form appears here.
      </div>
    </div>
  );
}
