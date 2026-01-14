import React from "react";
import { Star } from "lucide-react";
import {
  iphone_17_pro_max,
  samsung_s25_ultra,
  iphone_15_pro_max,
  google_pixel_9a,
  samsung_fold_6,
  iphone_15,
  ipad_pro_13,
  iphone_14,
} from "./images.generated.js";

// Map image paths to base64 data URLs
const imageMap = {
  "./images/iphone-17-pro-max.png": iphone_17_pro_max,
  "./images/samsung-s25-ultra.png": samsung_s25_ultra,
  "./images/iphone-15-pro-max.png": iphone_15_pro_max,
  "./images/google-pixel-9a.png": google_pixel_9a,
  "./images/samsung-fold-6.png": samsung_fold_6,
  "./images/iphone-15.png": iphone_15,
  "./images/ipad-pro-13.png": ipad_pro_13,
  "./images/iphone-14.png": iphone_14,
};

const resolveImage = (path) => imageMap[path] || path;

export default function PlaceCard({ place }) {
  if (!place) return null;
  return (
    <div className="min-w-[240px] select-none max-w-[240px] w-[70vw] sm:w-[240px] self-stretch flex flex-col bg-white rounded-2xl border border-black/10 overflow-hidden shadow-sm hover:shadow-md transition-shadow">
      <div className="w-full bg-gray-50 p-4">
        <img
          src={resolveImage(place.thumbnail)}
          alt={place.name}
          className="w-full aspect-square object-contain"
        />
      </div>
      <div className="p-4 flex flex-col flex-1">
        {place.brand && (
          <div className="text-xs font-medium text-blue-600 mb-1">
            {place.brand}
          </div>
        )}
        <div className="text-base font-semibold truncate line-clamp-1">{place.name}</div>
        {place.color && (
          <div className="text-xs mt-1 text-black/60">
            {place.color}
          </div>
        )}
        {place.rating && (
          <div className="text-xs mt-2 text-black/60 flex items-center gap-1">
            <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" aria-hidden="true" />
            {place.rating?.toFixed ? place.rating.toFixed(1) : place.rating}
          </div>
        )}
        {place.description ? (
          <div className="text-xs mt-2 text-black/70 line-clamp-2 flex-auto">
            {place.description}
          </div>
        ) : null}
        {place.price && (
          <div className="mt-3 pt-3 border-t border-black/10">
            <div className="flex items-baseline gap-2">
              <span className="text-lg font-bold text-black">
                {place.price}
              </span>
              {place.fullPrice && (
                <span className="text-xs text-black/40 line-through">
                  {place.fullPrice}
                </span>
              )}
            </div>
            <p className="text-xs text-black/60 mt-0.5">
              with eligible trade-in
            </p>
          </div>
        )}
        <div className="mt-4">
          <button
            type="button"
            className="w-full cursor-pointer inline-flex items-center justify-center rounded-lg bg-blue-600 text-white px-4 py-2.5 text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            View details
          </button>
        </div>
      </div>
    </div>
  );
}
