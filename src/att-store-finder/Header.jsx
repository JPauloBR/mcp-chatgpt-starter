import React from "react";
import { Search, ShoppingCart, Menu } from "lucide-react";

export default function Header() {
  return (
    <header className="bg-white border-b border-black/10 sticky top-0 z-50">
      {/* Top bar */}
      <div className="bg-white border-b border-black/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-8 text-xs">
            <div className="flex items-center gap-4">
              <button className="hover:underline">Personal</button>
              <button className="text-black/50 hover:text-black hover:underline">
                Business
              </button>
            </div>
            <div className="flex items-center gap-4">
              <button className="hover:underline">Find a store</button>
              <button className="hover:underline">Ver en español</button>
            </div>
          </div>
        </div>
      </div>

      {/* Main navigation */}
      <div className="bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo and menu */}
            <div className="flex items-center gap-6">
              <button className="lg:hidden p-2 hover:bg-black/5 rounded-lg">
                <Menu className="h-6 w-6" />
              </button>
              
              {/* AT&T Logo */}
              <div className="flex items-center gap-2">
                <div className="flex items-center justify-center w-10 h-10 bg-att-blue rounded-full">
                  <svg
                    viewBox="0 0 24 24"
                    className="w-6 h-6 text-white"
                    fill="currentColor"
                  >
                    <circle cx="12" cy="12" r="10" />
                    <path
                      d="M12 6v12M6 12h12"
                      stroke="white"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                </div>
                <span className="text-2xl font-bold text-att-blue">AT&T</span>
              </div>

              {/* Desktop navigation */}
              <nav className="hidden lg:flex items-center gap-6 ml-4">
                <button className="text-sm font-medium hover:text-att-blue transition">
                  Deals
                </button>
                <button className="text-sm font-medium hover:text-att-blue transition">
                  Wireless
                </button>
                <button className="text-sm font-medium hover:text-att-blue transition">
                  Internet
                </button>
                <button className="text-sm font-medium hover:text-att-blue transition">
                  Accessories
                </button>
                <button className="text-sm font-medium hover:text-att-blue transition">
                  Prepaid
                </button>
              </nav>
            </div>

            {/* Search and actions */}
            <div className="flex items-center gap-4">
              {/* Search bar */}
              <div className="hidden md:flex items-center bg-gray-50 rounded-full px-4 py-2 w-64 border border-black/10 focus-within:border-att-blue focus-within:ring-2 focus-within:ring-att-blue/20">
                <Search className="h-4 w-4 text-black/40 mr-2" />
                <input
                  type="text"
                  placeholder="I'm looking for..."
                  className="bg-transparent border-none outline-none text-sm w-full placeholder:text-black/40"
                />
              </div>

              {/* Mobile search icon */}
              <button className="md:hidden p-2 hover:bg-black/5 rounded-lg">
                <Search className="h-5 w-5" />
              </button>

              {/* Cart */}
              <button className="p-2 hover:bg-black/5 rounded-lg relative">
                <ShoppingCart className="h-5 w-5" />
              </button>

              {/* Support */}
              <button className="hidden sm:block text-sm font-medium hover:text-att-blue transition">
                Support
              </button>

              {/* Account */}
              <button className="hidden sm:block text-sm font-medium hover:text-att-blue transition">
                Account
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
