import { useReveal } from "../hooks/useReveal.js";

// Wraps children in a scroll-reveal container. `delay` staggers siblings
// (ms). `as` picks the element tag. Keep stagger small; per the motion
// guidance only a couple of elements should draw attention per view.
export default function Reveal({ children, as: Tag = "div", delay = 0, className = "", ...rest }) {
  const { ref, visible } = useReveal();
  return (
    <Tag
      ref={ref}
      className={`reveal ${visible ? "is-visible" : ""} ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
      {...rest}
    >
      {children}
    </Tag>
  );
}
