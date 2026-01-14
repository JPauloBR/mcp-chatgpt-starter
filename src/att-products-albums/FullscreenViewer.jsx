import React from "react";
import { useMaxHeight } from "../use-max-height";
import { X } from "lucide-react";
import FilmStrip from "./FilmStrip";
import { resolveImage } from "./imageResolver.js";

export default function FullscreenViewer({ album, onClose }) {
  const maxHeight = useMaxHeight() ?? undefined;
  const [index, setIndex] = React.useState(0);

  React.useEffect(() => {
    setIndex(0);
  }, [album?.id]);

  const photo = album?.photos?.[index];

  return (
    <div
      className="relative w-full bg-white overflow-y-auto"
      style={{
        maxHeight,
        height: maxHeight || "600px",
        minHeight: "500px",
      }}
    >
      {/* Close button */}
      {onClose && (
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-20 rounded-full bg-white text-black shadow-lg ring ring-black/5 p-2.5 hover:bg-gray-50"
          aria-label="Close viewer"
        >
          <X strokeWidth={1.5} className="h-4.5 w-4.5" aria-hidden="true" />
        </button>
      )}
      
      <div className="flex flex-col lg:flex-row min-h-full">
        {/* Film strip - left side on desktop */}
        <div className="hidden lg:block w-40 border-r border-black/10 pointer-events-auto flex-shrink-0">
          <FilmStrip album={album} selectedIndex={index} onSelect={setIndex} />
        </div>
        
        {/* Main content area */}
        <div className="flex-1 flex flex-col lg:flex-row">
          {/* Product image */}
          <div className="flex-1 flex items-center justify-center p-8 lg:p-12 bg-gray-50">
            {photo ? (
              <img
                src={resolveImage(photo.url)}
                alt={photo.title || album.title}
                className="max-w-full max-h-[400px] lg:max-h-[500px] object-contain"
              />
            ) : (
              <div className="text-black/40">No photo available</div>
            )}
          </div>
          
          {/* Product details - right side */}
          <div className="w-full lg:w-96 p-6 lg:p-8 border-t lg:border-t-0 lg:border-l border-black/10 bg-white">
            {photo?.brand && (
              <div className="text-sm font-medium text-blue-600 mb-2">
                {photo.brand}
              </div>
            )}
            
            <h1 className="text-2xl lg:text-3xl font-semibold text-black mb-4">
              {photo?.title || album?.title}
            </h1>
            
            {photo?.color && (
              <div className="mb-4">
                <span className="text-sm text-black/60">Color: </span>
                <span className="text-sm font-medium text-black">{photo.color}</span>
              </div>
            )}
            
            {photo?.description && (
              <p className="text-sm text-black/70 mb-6 leading-relaxed">
                {photo.description}
              </p>
            )}
            
            {photo?.price && (
              <div className="border-t border-black/10 pt-6 mb-6">
                <div className="flex items-baseline gap-2 mb-1">
                  <span className="text-3xl font-bold text-black">
                    {photo.price}
                  </span>
                  {photo.fullPrice && (
                    <span className="text-sm text-black/50 line-through">
                      {photo.fullPrice}
                    </span>
                  )}
                </div>
                <p className="text-xs text-black/60">
                  with eligible trade-in
                </p>
              </div>
            )}
            
            <div className="space-y-3">
              <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors">
                Add to cart
              </button>
              <button className="w-full bg-white hover:bg-gray-50 text-black font-medium py-3 px-4 rounded-lg border border-black/20 transition-colors">
                See device offers
              </button>
            </div>
            
            {album?.photos?.length > 1 && (
              <div className="mt-6 pt-6 border-t border-black/10">
                <p className="text-xs text-black/60 mb-3">
                  {index + 1} of {album.photos.length} devices
                </p>
                <div className="flex gap-2 overflow-x-auto pb-2">
                  {album.photos.map((p, idx) => (
                    <button
                      key={p.id}
                      onClick={() => setIndex(idx)}
                      className={
                        "flex-shrink-0 w-16 h-16 rounded-lg border-2 transition-all overflow-hidden " +
                        (idx === index
                          ? "border-blue-600 ring-2 ring-blue-100"
                          : "border-black/10 hover:border-black/30")
                      }
                    >
                      <img
                        src={resolveImage(p.url)}
                        alt={p.title}
                        className="w-full h-full object-cover"
                      />
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
