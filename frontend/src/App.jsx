import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Landing from "./views/Landing.jsx";
import Generate from "./views/Generate.jsx";
import Result from "./views/Result.jsx";
import TestForm from "./views/TestForm.jsx";
import Proof from "./views/Proof.jsx";
import About from "./views/About.jsx";

export default function App() {
  return (
    <Routes>
      {/* Landing is the full-bleed marketing page: its own nav, no Layout chrome. */}
      <Route path="/" element={<Landing />} />

      {/* App routes keep the existing skeleton Layout (top nav + footer). */}
      <Route path="/generate" element={<Layout><Generate /></Layout>} />
      <Route path="/result" element={<Layout><Result /></Layout>} />
      <Route path="/testform" element={<Layout><TestForm /></Layout>} />
      <Route path="/proof" element={<Layout><Proof /></Layout>} />
      <Route path="/about" element={<Layout><About /></Layout>} />
    </Routes>
  );
}
