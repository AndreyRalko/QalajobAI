import Navbar from "@/app/components/layout/Navbar";
import Hero from "@/app/components/home/Hero";
import HowItWorks from "@/app/components/home/HowItWorks";
import AISection from "@/app/components/home/AISection";
import CTA from "@/app/components/home/CTA";
import Footer from "@/app/components/layout/Footer";

export default function Home() {
  return (
    <main className="min-h-screen bg-[#030712] text-white overflow-hidden">
      <Navbar />
      <Hero />
      <HowItWorks />
      <AISection />
      <CTA />
      <Footer />
    </main>
  );
}
