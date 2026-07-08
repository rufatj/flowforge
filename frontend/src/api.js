// Single place that knows the backend base URL.
// Configured at build time via VITE_BACKEND_URL (see docker-compose.yml).
export const BACKEND_URL =
  import.meta.env.VITE_BACKEND_URL || "http://localhost:8080";

async function request(path, options = {}) {
  const res = await fetch(`${BACKEND_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res;
}

export const api = {
  health: () => request("/health").then((r) => r.json()),
  generate: (description) =>
    request("/generate", {
      method: "POST",
      body: JSON.stringify({ description }),
    }).then((r) => r.json()),
  importWorkflow: (workflow) =>
    request("/import", {
      method: "POST",
      body: JSON.stringify({ workflow }),
    }).then((r) => r.json()),
  testform: (workflow) =>
    request("/testform", {
      method: "POST",
      body: JSON.stringify({ workflow }),
    }).then((r) => r.text()),
  results: () => request("/results").then((r) => r.json()),
};
