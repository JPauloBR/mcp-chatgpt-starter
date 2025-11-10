import React, { useState, useEffect, useCallback } from "react";
import { createRoot } from "react-dom/client";
import { AnimatePresence } from "framer-motion";
import AddressForm from "./AddressForm";
import CoverageMap from "./CoverageMap";
import AvailabilityResults from "./AvailabilityResults";
import coverageData from "./coverage-data.json";
import { useOpenAiGlobal } from "../use-openai-global";
import { useMaxHeight } from "../use-max-height";
import { Maximize2 } from "lucide-react";

// Geocode mock addresses or use provided coordinates
function geocodeAddress(address) {
  const mockAddress = coverageData.mockAddresses.find(
    (a) => a.address.toLowerCase().includes(address.toLowerCase()) || 
           address.toLowerCase().includes(a.address.toLowerCase())
  );

  if (mockAddress) {
    return {
      coords: mockAddress.coords,
      fiber: mockAddress.fiber,
      internetAir: mockAddress.internetAir,
      availablePlans: mockAddress.plans,
    };
  }

  // Default fallback to SF downtown with both services
  return {
    coords: [-122.4194, 37.7749],
    fiber: true,
    internetAir: true,
    availablePlans: ["fiber-1gig", "fiber-2gig", "internet-air"],
  };
}

export default function App() {
  const displayMode = useOpenAiGlobal("displayMode");
  const maxHeight = useMaxHeight() ?? undefined;
  
  // Check if address was provided via widget state
  const [widgetState, setWidgetState] = useState({});
  const [currentView, setCurrentView] = useState("loading"); // "loading", "input", "map"
  const [addressData, setAddressData] = useState(null);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    // Check for pre-provided address from ChatGPT
    if (typeof window !== "undefined" && window.oai?.widget?.getState) {
      const state = window.oai.widget.getState();
      setWidgetState(state || {});
      
      // If address was provided, skip to map view
      if (state?.address) {
        const geocoded = geocodeAddress(state.address);
        setAddressData({
          address: state.address,
          ...geocoded,
        });
        setCurrentView("map");
        // Show results immediately when address is pre-provided
        setTimeout(() => setShowResults(true), 500);
      } else {
        setCurrentView("input");
      }
    } else {
      setCurrentView("input");
    }
  }, []);

  const handleAddressSubmit = (address) => {
    const geocoded = geocodeAddress(address);
    setAddressData({
      address,
      ...geocoded,
    });
    setCurrentView("map");
    // Show results after a brief delay to let map render
    setTimeout(() => setShowResults(true), 800);
  };

  const handleMapLoad = useCallback((map) => {
    // Fit bounds to show coverage areas and location
    if (addressData?.coords) {
      try {
        map.flyTo({
          center: addressData.coords,
          zoom: 13,
          duration: 1500,
        });
      } catch (error) {
        console.error("Error flying to location:", error);
      }
    }
    // Ensure map resizes to container
    setTimeout(() => {
      if (map) {
        try {
          map.resize();
        } catch (error) {
          console.error("Error resizing map:", error);
        }
      }
    }, 100);
  }, [addressData?.coords]);

  // Update widget state for ChatGPT
  useEffect(() => {
    if (
      typeof window !== "undefined" &&
      window.oai &&
      typeof window.oai.widget.setState === "function" &&
      addressData
    ) {
      window.oai.widget.setState({
        address: addressData.address,
        coords: addressData.coords,
        fiber: addressData.fiber,
        internetAir: addressData.internetAir,
        view: currentView,
      });
    }
  }, [addressData, currentView]);

  if (currentView === "loading") {
    return (
      <div className="flex items-center justify-center min-h-[480px] bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading coverage checker...</p>
        </div>
      </div>
    );
  }

  if (currentView === "input") {
    return <AddressForm onAddressSubmit={handleAddressSubmit} />;
  }

  // Safety check - ensure we have address data before showing map
  if (currentView === "map" && !addressData) {
    return (
      <div className="flex items-center justify-center min-h-[480px] bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading location data...</p>
        </div>
      </div>
    );
  }

  // Map view
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <div
        style={{
          maxHeight: displayMode === "fullscreen" ? undefined : maxHeight,
          height: displayMode === "fullscreen" ? "100vh" : 600,
        }}
        className={
          "relative antialiased w-full overflow-hidden " +
          (displayMode === "fullscreen"
            ? "rounded-none border-0 flex-1"
            : "border border-black/10 dark:border-white/10 rounded-2xl sm:rounded-3xl min-h-[600px]")
        }
      >
        {/* Fullscreen button */}
        {displayMode !== "fullscreen" && (
          <button
            aria-label="Enter fullscreen"
            className="absolute top-4 right-4 z-30 rounded-full bg-white text-black shadow-lg ring ring-black/5 p-2.5 pointer-events-auto"
            onClick={() => {
              if (window?.webplus?.requestDisplayMode) {
                window.webplus.requestDisplayMode({ mode: "fullscreen" });
              }
            }}
          >
            <Maximize2
              strokeWidth={1.5}
              className="h-4.5 w-4.5"
              aria-hidden="true"
            />
          </button>
        )}

        {/* Map */}
        <div className="absolute inset-0 w-full h-full z-0">
          <CoverageMap
            coords={addressData.coords}
            coverageZones={coverageData.coverageZones}
            onMapLoad={handleMapLoad}
          />
        </div>

        {/* Results Panel */}
        <AnimatePresence>
          {showResults && addressData && (
            <AvailabilityResults
              address={addressData.address}
              availability={{
                fiber: addressData.fiber,
                internetAir: addressData.internetAir,
                availablePlans: addressData.availablePlans,
              }}
              plans={coverageData.plans}
              onClose={() => setShowResults(false)}
            />
          )}
        </AnimatePresence>

        {/* Info bar (bottom) */}
        {displayMode === "fullscreen" && !showResults && (
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20">
            <button
              onClick={() => setShowResults(true)}
              className="bg-white hover:bg-gray-50 text-gray-900 font-medium px-6 py-3 rounded-full shadow-lg ring ring-black/5 transition-colors"
            >
              View available plans
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

createRoot(document.getElementById("att-fiber-coverage-checker-root")).render(<App />);
