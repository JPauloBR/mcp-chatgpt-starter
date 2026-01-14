import React from "react";
import { motion } from "framer-motion";
import { Star, X } from "lucide-react";

// Fallback placeholder for broken images
function ImageWithFallback({ src, alt, className }) {
  const [error, setError] = React.useState(false);
  
  if (error || !src) {
    return (
      <div className={`${className} bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center`}>
        <span className="text-white font-bold text-2xl">AT&T</span>
      </div>
    );
  }
  
  return (
    <img
      src={src}
      alt={alt}
      className={className}
      onError={() => setError(true)}
    />
  );
}

export default function Inspector({ place, onClose }) {
  if (!place) return null;
  return (
    <motion.div
      key={place.id}
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ type: "spring", bounce: 0, duration: 0.25 }}
      className="pizzaz-inspector absolute z-30 top-0 bottom-4 left-0 right-auto xl:left-auto xl:right-6 md:z-20 w-[340px] xl:w-[360px] xl:top-6 xl:bottom-8 pointer-events-auto"
    >
      <button
        aria-label="Close details"
        className="inline-flex absolute z-10 top-4 left-4 xl:top-4 xl:left-4 shadow-xl rounded-full p-2 bg-white ring ring-black/10 xl:shadow-2xl hover:bg-white"
        onClick={onClose}
      >
        <X className="h-[18px] w-[18px]" aria-hidden="true" />
      </button>
      <div className="relative h-full overflow-y-auto rounded-none xl:rounded-3xl bg-white text-black xl:shadow-xl xl:ring ring-black/10">
        <div className="relative mt-2 xl:mt-0 px-2 xl:px-0">
          <ImageWithFallback
            src={place.thumbnail}
            alt={place.name}
            className="w-full rounded-3xl xl:rounded-none h-80 object-cover xl:rounded-t-2xl"
          />
        </div>

        <div className="h-[calc(100%-11rem)] sm:h-[calc(100%-14rem)]">
          <div className="p-4 sm:p-5">
            <div className="text-2xl font-medium truncate">{place.name}</div>
            <div className="text-sm mt-1 opacity-70 flex items-center gap-1">
              <Star className="h-3.5 w-3.5" aria-hidden="true" />
              {place.rating.toFixed(1)}
              {place.type && <span>· {place.type === 'retail' ? 'Retail Store' : place.type === '5g-coverage' ? '5G Coverage' : 'Service Center'}</span>}
              <span>· {place.city}</span>
            </div>
            <div className="mt-3 flex flex-row items-center gap-3 font-medium text-sm">
              <div className="rounded-full bg-att-blue text-white cursor-pointer px-4 py-2 hover:bg-att-blue-dark transition">
                Visit store
              </div>
              <div className="rounded-full border-2 border-att-blue text-att-blue cursor-pointer px-4 py-2 hover:bg-att-blue/5 transition">
                Call store
              </div>
            </div>
            <div className="text-sm mt-5">
              <div className="mb-3">
                <div className="font-medium text-black/70 mb-1">Address</div>
                <div>{place.address || 'San Francisco, CA'}</div>
              </div>
              <div className="mb-3">
                <div className="font-medium text-black/70 mb-1">Hours</div>
                <div>{place.hours || 'Mon-Sat 10am-8pm'}</div>
              </div>
              {place.products && place.products.length > 0 && (
                <div className="mb-3">
                  <div className="font-medium text-black/70 mb-1">Available Products</div>
                  <div className="flex flex-wrap gap-2">
                    {place.products.map((product, idx) => (
                      <span key={idx} className="text-xs bg-att-blue/10 text-att-blue px-2 py-1 rounded-full">
                        {product}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {place.services && place.services.length > 0 && (
            <div className="px-4 sm:px-5 pb-4">
              <div className="text-lg font-medium mb-3">Services Offered</div>
              <ul className="space-y-2">
                {place.services.map((service, idx) => (
                  <li key={idx} className="flex items-center gap-2 text-sm">
                    <div className="h-1.5 w-1.5 rounded-full bg-att-blue" />
                    {service}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
