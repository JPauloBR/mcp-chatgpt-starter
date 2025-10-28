import React from "react";
import { createRoot } from "react-dom/client";
import productsData from "./products.json";
import { ShoppingCart, Star } from "lucide-react";

function App() {
  const places = productsData?.products || [];

  return (
    <div className="antialiased w-full text-black px-4 pb-2 border border-black/10 rounded-2xl sm:rounded-3xl overflow-hidden bg-white">
      <div className="max-w-full">
        <div className="flex flex-row items-center gap-4 sm:gap-4 border-b border-black/5 py-4">
          <div
            className="sm:w-18 w-16 aspect-square rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center text-white font-bold text-2xl"
          >
            AT&T
          </div>
          <div>
            <div className="text-base sm:text-xl font-medium">
              Top Devices
            </div>
            <div className="text-sm text-black/60">
              Best smartphones and tablets available now
            </div>
          </div>
          <div className="flex-auto hidden sm:flex justify-end pr-2">
            <button
              type="button"
              className="cursor-pointer inline-flex items-center rounded-lg bg-blue-600 text-white px-4 py-2 sm:text-md text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              View All
            </button>
          </div>
        </div>
        <div className="min-w-full text-sm flex flex-col">
          {places.slice(0, 8).map((place, i) => (
            <div
              key={place.id}
              className="px-3 -mx-2 rounded-2xl hover:bg-black/5 cursor-pointer transition-colors"
            >
              <div
                style={{
                  borderBottom:
                    i === places.slice(0, 8).length - 1 ? "none" : "1px solid rgba(0, 0, 0, 0.05)",
                }}
                className="flex w-full items-center hover:border-black/0! gap-2"
              >
                <div className="py-3 pr-3 min-w-0 w-full sm:w-auto sm:flex-1">
                  <div className="flex items-center gap-3">
                    <img
                      src={place.thumbnail}
                      alt={place.name}
                      className="h-12 w-12 sm:h-14 sm:w-14 rounded-lg object-contain bg-gray-50 p-1 ring ring-black/5"
                    />
                    <div className="w-4 text-center sm:block hidden text-sm font-medium text-black/40">
                      {i + 1}
                    </div>
                    <div className="min-w-0 sm:pl-1 flex flex-col items-start h-full flex-1">
                      {place.brand && (
                        <div className="text-xs font-medium text-blue-600">
                          {place.brand}
                        </div>
                      )}
                      <div className="font-semibold text-sm sm:text-base truncate max-w-[40ch]">
                        {place.name}
                      </div>
                      <div className="mt-0.5 flex items-center gap-3 text-black/60 text-xs">
                        <div className="flex items-center gap-1">
                          <Star
                            strokeWidth={1.5}
                            className="h-3 w-3 fill-yellow-400 text-yellow-400"
                          />
                          <span>
                            {place.rating?.toFixed
                              ? place.rating.toFixed(1)
                              : place.rating}
                          </span>
                        </div>
                        <div className="whitespace-nowrap sm:hidden">
                          {place.color}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="hidden sm:flex flex-col items-end py-2 px-3 text-sm whitespace-nowrap">
                  <div className="font-bold text-black">{place.price}</div>
                  {place.fullPrice && (
                    <div className="text-xs text-black/40 line-through">
                      {place.fullPrice}
                    </div>
                  )}
                </div>
                <div className="py-2 whitespace-nowrap flex justify-end pl-2">
                  <button className="p-2 rounded-lg hover:bg-blue-50 transition-colors">
                    <ShoppingCart strokeWidth={1.5} className="h-5 w-5 text-blue-600" />
                  </button>
                </div>
              </div>
            </div>
          ))}
          {places.length === 0 && (
            <div className="py-6 text-center text-black/60">
              No devices found.
            </div>
          )}
        </div>
        <div className="sm:hidden px-0 pt-2 pb-2">
          <button
            type="button"
            className="w-full cursor-pointer inline-flex items-center justify-center rounded-lg bg-blue-600 text-white px-4 py-2.5 font-medium hover:bg-blue-700 transition-colors"
          >
            View All
          </button>
        </div>
      </div>
    </div>
  );
}

createRoot(document.getElementById("att-products-list-root")).render(<App />);
