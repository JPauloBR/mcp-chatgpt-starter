import React from "react";
import { Facebook, Instagram, Linkedin, Twitter } from "lucide-react";

export default function Footer() {
  const footerSections = [
    {
      title: "Shop",
      links: [
        "Cell phones",
        "Fiber internet",
        "Home internet",
        "Tablets",
        "Smartwatches",
        "Wireless accessories",
        "Prepaid phones",
      ],
    },
    {
      title: "Trending",
      links: [
        "iPhone 17 Pro Max",
        "iPhone 17 Pro",
        "iPhone Air",
        "Samsung Galaxy S25 Ultra",
        "Samsung Galaxy Z Fold7",
        "Samsung Galaxy Z Flip7",
      ],
    },
    {
      title: "Top phone & data plans",
      links: [
        "Unlimited phone plans",
        "International plans",
        "Add a line",
        "Upgrade",
        "Tablet data plans",
        "Mobile hotspot plans",
        "Next Up Anytime",
      ],
    },
    {
      title: "Switch to AT&T",
      links: [
        "Switch to AT&T",
        "How to switch phone carriers",
        "Internet speed test",
        "Bring your own device",
        "Cell phone trade-in",
      ],
    },
    {
      title: "Resources",
      links: [
        "Bundle internet and wireless",
        "What is Internet Air?",
        "How to use your phone internationally",
        "What is fiber internet?",
        "What is eSIM?",
        "Return or exchange your wireless device",
      ],
    },
    {
      title: "AT&T",
      links: [
        "Find a store",
        "Newsroom",
        "Investor Relations",
        "Corporate Responsibility",
        "Careers",
        "Help & info",
        "AT&T Guarantee",
      ],
    },
  ];

  return (
    <footer className="bg-[#00468B] text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Footer grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 mb-12">
          {footerSections.map((section, idx) => (
            <div key={idx}>
              <h3 className="font-semibold text-sm mb-4">{section.title}</h3>
              <ul className="space-y-2">
                {section.links.map((link, linkIdx) => (
                  <li key={linkIdx}>
                    <button className="text-xs text-white/80 hover:text-white hover:underline text-left">
                      {link}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Social media */}
        <div className="border-t border-white/20 pt-8 mb-8">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium">Follow AT&T</span>
              <div className="flex gap-3">
                <button
                  className="p-2 hover:bg-white/10 rounded-full transition"
                  aria-label="Twitter"
                >
                  <Twitter className="h-5 w-5" />
                </button>
                <button
                  className="p-2 hover:bg-white/10 rounded-full transition"
                  aria-label="Facebook"
                >
                  <Facebook className="h-5 w-5" />
                </button>
                <button
                  className="p-2 hover:bg-white/10 rounded-full transition"
                  aria-label="Instagram"
                >
                  <Instagram className="h-5 w-5" />
                </button>
                <button
                  className="p-2 hover:bg-white/10 rounded-full transition"
                  aria-label="LinkedIn"
                >
                  <Linkedin className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom links */}
        <div className="border-t border-white/20 pt-8">
          <div className="flex flex-wrap gap-4 text-xs text-white/80 mb-4">
            <button className="hover:text-white hover:underline">
              Terms of Use
            </button>
            <span>|</span>
            <button className="hover:text-white hover:underline">
              Privacy Policy
            </button>
            <span>|</span>
            <button className="hover:text-white hover:underline">
              Accessibility
            </button>
            <span>|</span>
            <button className="hover:text-white hover:underline">
              Legal
            </button>
            <span>|</span>
            <button className="hover:text-white hover:underline">
              Your Privacy Choices
            </button>
          </div>
          <p className="text-xs text-white/60">
            © 2025 AT&T Intellectual Property. All rights reserved. AT&T, the
            Globe logo, and other marks are trademarks and service marks of
            AT&T Intellectual Property and/or AT&T affiliated companies.
          </p>
        </div>
      </div>
    </footer>
  );
}
