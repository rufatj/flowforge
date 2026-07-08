// Inline Lucide-style icons, 24x24, currentColor. No emoji as UI icons.
const base = { viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round", strokeLinejoin: "round", "aria-hidden": true };

export const ArrowUp = ({ className = "h-5 w-5" }) => (
  <svg className={className} {...base}><path d="M12 19V5" /><path d="M5 12l7-7 7 7" /></svg>
);
export const Describe = ({ className = "h-5 w-5" }) => (
  <svg className={className} {...base}><path d="M12 20h9" /><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z" /></svg>
);
export const Generate = ({ className = "h-5 w-5" }) => (
  <svg className={className} {...base}><path d="M12 3v3m0 12v3m9-9h-3M6 12H3m14.5-6.5-2 2m-7 7-2 2m11 0-2-2m-7-7-2-2" /></svg>
);
export const Import = ({ className = "h-5 w-5" }) => (
  <svg className={className} {...base}><path d="M12 3v12" /><path d="m8 11 4 4 4-4" /><path d="M4 21h16" /></svg>
);
export const Github = ({ className = "h-4 w-4" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 .5C5.73.5.5 5.73.5 12a11.5 11.5 0 0 0 7.86 10.92c.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.37-3.88-1.37-.53-1.34-1.3-1.7-1.3-1.7-1.05-.72.08-.7.08-.7 1.17.08 1.78 1.2 1.78 1.2 1.04 1.78 2.73 1.27 3.4.97.1-.75.4-1.27.73-1.56-2.56-.29-5.26-1.28-5.26-5.7 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.18 1.18a11 11 0 0 1 5.8 0c2.2-1.5 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.84 1.19 3.1 0 4.43-2.7 5.4-5.28 5.69.41.36.78 1.07.78 2.16v3.2c0 .31.21.67.8.56A11.5 11.5 0 0 0 23.5 12C23.5 5.73 18.27.5 12 .5Z" /></svg>
);
export const Mail = ({ className = "h-4 w-4" }) => (
  <svg className={className} {...base}><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 7 9 6 9-6" /></svg>
);
export const ArrowRight = ({ className = "h-4 w-4" }) => (
  <svg className={className} {...base}><path d="M5 12h14" /><path d="m13 5 7 7-7 7" /></svg>
);
