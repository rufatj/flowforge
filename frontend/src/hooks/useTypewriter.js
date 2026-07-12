import { useEffect, useRef, useState } from "react";

// Cycles through example prompts inside the hero input: types each one
// character by character (~2.5s), holds it, erases quickly, moves on.
// Pauses whenever `active` is false (user focused or typed something).
const TYPE_MS = 34;      // per character while typing
const ERASE_MS = 9;      // per character while erasing
const HOLD_MS = 4200;    // how long a finished example stays readable

export function useTypewriter(prompts, active = true) {
  const [text, setText] = useState("");
  const state = useRef({ index: 0, pos: 0, phase: "typing" });

  useEffect(() => {
    if (!active || prompts.length === 0) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setText(prompts[0]);
      return;
    }

    let timer;
    const tick = () => {
      const s = state.current;
      const prompt = prompts[s.index % prompts.length];

      if (s.phase === "typing") {
        s.pos += 1;
        setText(prompt.slice(0, s.pos));
        if (s.pos >= prompt.length) {
          s.phase = "holding";
          timer = setTimeout(tick, HOLD_MS);
        } else {
          timer = setTimeout(tick, TYPE_MS);
        }
      } else if (s.phase === "holding") {
        s.phase = "erasing";
        timer = setTimeout(tick, ERASE_MS);
      } else {
        s.pos -= 2;
        if (s.pos <= 0) {
          s.pos = 0;
          setText("");
          s.index += 1;
          s.phase = "typing";
          timer = setTimeout(tick, 500);
        } else {
          setText(prompt.slice(0, s.pos));
          timer = setTimeout(tick, ERASE_MS);
        }
      }
    };

    timer = setTimeout(tick, 600);
    return () => clearTimeout(timer);
  }, [prompts, active]);

  return text;
}
