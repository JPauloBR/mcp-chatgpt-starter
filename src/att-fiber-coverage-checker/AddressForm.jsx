import React, { useState } from "react";
import { Search } from "lucide-react";

export default function AddressForm({ onAddressSubmit }) {
  const [address, setAddress] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (address.trim()) {
      setIsLoading(true);
      // Simulate geocoding delay
      setTimeout(() => {
        onAddressSubmit(address.trim());
        setIsLoading(false);
      }, 500);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[480px] bg-gradient-to-br from-blue-50 to-white p-8">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Enter your address to get started
          </h1>
          <p className="text-lg text-gray-600">
            Check if AT&T Fiber or Internet Air is available at your location
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
              Address
            </label>
            <div className="relative">
              <input
                id="address"
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="12345 Main st Apt A Winter Park, FL 32792"
                className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-base"
                disabled={isLoading}
              />
              <Search className="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="businessAddress"
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="businessAddress" className="text-sm text-gray-700">
              This is a business address
            </label>
          </div>

          <button
            type="submit"
            disabled={!address.trim() || isLoading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-full transition-colors duration-200"
          >
            {isLoading ? "Checking availability..." : "Check availability"}
          </button>

          <p className="text-sm text-gray-600 text-center mt-4">
            Are you a home business?{" "}
            <a href="#" className="text-blue-600 hover:underline">
              Learn more about home business offers
            </a>
          </p>
        </form>

        <div className="mt-12 p-6 bg-blue-50 rounded-lg border border-blue-100">
          <h3 className="font-semibold text-gray-900 mb-2">What you'll see:</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li className="flex items-start">
              <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mr-2 mt-1.5"></span>
              <span><strong>Blue areas</strong> show AT&T Fiber coverage with speeds up to 5 Gig</span>
            </li>
            <li className="flex items-start">
              <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2 mt-1.5"></span>
              <span><strong>Green areas</strong> show AT&T Internet Air (5G wireless) coverage</span>
            </li>
            <li className="flex items-start">
              <span className="inline-block w-2 h-2 bg-purple-500 rounded-full mr-2 mt-1.5"></span>
              <span>Your home location and available plans</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
