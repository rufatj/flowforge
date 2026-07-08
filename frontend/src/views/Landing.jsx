import AuroraBackground from "../components/AuroraBackground.jsx";
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

export default function Landing() {
  return (
    <div className="relative min-h-screen overflow-x-hidden">
      <AuroraBackground />
      <Nav />
      <main>
        <Hero />
        <HowItWorks />
        <WhyDifferent />
        <Knows />
        <Timeline />
        <Story />
        <GetStarted />
        <Contact />
      </main>
      <Footer />
    </div>
  );
}
