import AuroraBackground from "../components/AuroraBackground.jsx";
import FullpageContainer from "../components/FullpageContainer.jsx";
import Nav from "../components/landing/Nav.jsx";
import Hero from "../components/landing/Hero.jsx";
import HowItWorks from "../components/landing/HowItWorks.jsx";
import WhyDifferent from "../components/landing/WhyDifferent.jsx";
import Knows from "../components/landing/Knows.jsx";
import Timeline from "../components/landing/Timeline.jsx";
import Story from "../components/landing/Story.jsx";
import GetStarted from "../components/landing/GetStarted.jsx";
import Contact from "../components/landing/Contact.jsx";
import Footer from "../components/landing/Footer.jsx";

// Slide wrapper: fills 100vh, centers content both axes
function Slide({ children, id, overflow = "hidden" }) {
  return (
    <div
      id={id}
      className={`relative flex h-screen w-full flex-col overflow-${overflow}`}
    >
      {children}
    </div>
  );
}

// Centering shell: stretches full width so mx-auto inside works correctly
function Center({ children, flex = true }) {
  return (
    <div className={`flex h-full w-full items-center justify-center ${flex ? "" : "flex-col"}`}>
      {children}
    </div>
  );
}

const SECTIONS = [
  // 0 — Hero
  <Slide key="hero" id="slide-hero">
    <Hero />
  </Slide>,

  // 1 — How it works
  <Slide key="how" id="slide-how" overflow="auto">
    <Center>
      <div className="w-full">
        <HowItWorks />
      </div>
    </Center>
  </Slide>,

  // 2 — Why different (full-bleed bg image, internally centered)
  <Slide key="why" id="slide-why">
    <WhyDifferent />
  </Slide>,

  // 3 — Knows / integrations
  <Slide key="knows" id="slide-knows" overflow="auto">
    <Center>
      <div className="w-full">
        <Knows />
      </div>
    </Center>
  </Slide>,

  // 4 — Journey / timeline
  <Slide key="journey" id="slide-journey" overflow="auto">
    <Center>
      <div className="w-full">
        <Timeline />
      </div>
    </Center>
  </Slide>,

  // 5 — Story / about
  <Slide key="story" id="slide-story" overflow="auto">
    <Center>
      <div className="w-full">
        <Story />
      </div>
    </Center>
  </Slide>,

  // 6 — Get started
  <Slide key="start" id="slide-start">
    <Center>
      <GetStarted />
    </Center>
  </Slide>,

  // 7 — Contact + Footer
  <Slide key="contact" id="slide-contact" overflow="auto">
    <div className="flex h-full w-full flex-col justify-between">
      <div className="flex flex-1 w-full items-center justify-center">
        <div className="w-full">
          <Contact />
        </div>
      </div>
      <Footer />
    </div>
  </Slide>,
];

export default function Landing() {
  return (
    <div className="relative overflow-hidden">
      <AuroraBackground />
      <Nav />
      <FullpageContainer sections={SECTIONS} duration={900} showDots />
    </div>
  );
}
