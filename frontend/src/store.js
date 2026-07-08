// Tiny session store: carries the generated workflow between views
// (Generate -> Result) and survives a page refresh. No state library needed.

const KEY = "flowforge.lastGeneration";

export function saveGeneration(result) {
  sessionStorage.setItem(KEY, JSON.stringify(result));
}

export function loadGeneration() {
  try {
    const raw = sessionStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}
