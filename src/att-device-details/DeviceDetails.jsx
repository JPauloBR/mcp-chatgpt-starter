import React, { useState } from "react";
import { ChevronLeft, ChevronRight, Heart, Share, Maximize2, Bookmark, Info } from "lucide-react";
import deviceData from "./device-data.json";

// Import base64-inlined images for ChatGPT widget compatibility
import {
  iphone_17_pro_max_1,
  iphone_17_pro_max_2,
  iphone_17_pro_max_3,
  iphone_17_pro_max_4,
  galaxy_s25_ultra_1,
  galaxy_s25_ultra_2,
  galaxy_s25_ultra_3,
} from "./images.generated.js";

// Map image paths to base64 data URLs
const imageMap = {
  "./images/iphone-17-pro-max-1.png": iphone_17_pro_max_1,
  "./images/iphone-17-pro-max-2.png": iphone_17_pro_max_2,
  "./images/iphone-17-pro-max-3.png": iphone_17_pro_max_3,
  "./images/iphone-17-pro-max-4.png": iphone_17_pro_max_4,
  "./images/galaxy-s25-ultra-1.png": galaxy_s25_ultra_1,
  "./images/galaxy-s25-ultra-2.png": galaxy_s25_ultra_2,
  "./images/galaxy-s25-ultra-3.png": galaxy_s25_ultra_3,
};

const resolveImage = (path) => imageMap[path] || path;

export default function DeviceDetails({ deviceId = "iphone-17-pro-max" }) {
  const device = deviceData.devices[deviceId] || deviceData.devices["iphone-17-pro-max"];
  const [selectedColor, setSelectedColor] = useState(device.colors.find(c => c.selected) || device.colors[0]);
  const [selectedModel, setSelectedModel] = useState(device.models.find(m => m.selected) || device.models[0]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % device.gallery.length);
  };

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + device.gallery.length) % device.gallery.length);
  };

  return (
    <div className="bg-white rounded-3xl overflow-hidden shadow-sm border border-gray-200 max-w-5xl mx-auto font-sans text-gray-900">
      {/* Header / Nav (Mock) */}
      <div className="flex items-center gap-2 p-4 text-sm font-medium text-gray-600 border-b border-gray-100">
        <ChevronLeft className="w-4 h-4" />
        <span>See all phones</span>
      </div>

      <div className="flex flex-col md:flex-row">
        {/* Left Column: Image Gallery */}
        <div className="md:w-1/2 p-6 relative">
          <div className="absolute top-6 left-6 flex gap-3 z-10">
            <button className="p-2 rounded-full hover:bg-gray-100 transition-colors">
              <Heart className="w-5 h-5 text-blue-600" />
            </button>
            <button className="p-2 rounded-full hover:bg-gray-100 transition-colors">
              <Share className="w-5 h-5 text-blue-600" />
            </button>
          </div>
          
          <div className="absolute top-6 right-6 z-10">
             <button className="p-2 rounded-full hover:bg-gray-100 transition-colors">
              <Maximize2 className="w-5 h-5 text-blue-600" />
            </button>
          </div>

          <div className="relative aspect-square flex items-center justify-center my-8">
            <img 
              src={resolveImage(device.gallery[currentImageIndex])} 
              alt={`${device.name} in ${selectedColor.name}`}
              className="max-h-full max-w-full object-contain mix-blend-multiply"
            />
            
            {/* Navigation Arrows */}
            <button 
              onClick={prevImage}
              className="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center rounded-full bg-white shadow-md border border-gray-100 hover:bg-gray-50"
            >
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            </button>
            <button 
              onClick={nextImage}
              className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center rounded-full bg-white shadow-md border border-gray-100 hover:bg-gray-50"
            >
              <ChevronRight className="w-5 h-5 text-gray-600" />
            </button>
          </div>

          {/* Thumbnails */}
          <div className="flex justify-center gap-3 mt-4 overflow-x-auto pb-2">
            {device.gallery.map((img, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentImageIndex(idx)}
                className={`w-12 h-12 rounded-lg border-2 p-1 ${
                  currentImageIndex === idx ? "border-blue-600" : "border-transparent hover:border-gray-300"
                }`}
              >
                <img src={resolveImage(img)} alt="" className="w-full h-full object-contain" />
              </button>
            ))}
          </div>
          
          <div className="mt-8 flex items-center justify-center gap-2 text-sm">
             <div className="flex text-black text-lg">
                {"★".repeat(Math.floor(device.rating))}
                {"★".slice(0, device.rating % 1 >= 0.5 ? 1 : 0)} 
             </div>
             <span className="font-bold">{device.rating}</span>
             <span className="text-gray-500 underline decoration-gray-400 decoration-1 underline-offset-2">
                | {device.reviewCount} Write a review
             </span>
          </div>
          
           <div className="mt-2 text-center text-sm font-medium text-blue-700 hover:underline cursor-pointer">
             Learn more about this device
           </div>
        </div>

        {/* Right Column: Product Details */}
        <div className="md:w-1/2 p-6 md:pl-0 md:pr-12">
          {/* Tagline */}
          <div className="text-transparent bg-clip-text bg-gradient-to-r from-orange-500 via-pink-500 to-purple-600 font-semibold text-sm mb-1">
            {device.tagline}
          </div>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-4">{device.name}</h1>
          
          {/* Pricing */}
          <div className="flex items-start justify-between mb-6">
            <div>
               <div className="text-xs text-gray-500 mb-1">{device.fullPrice}</div>
               <div className="flex items-baseline gap-1">
                 <span className="text-xs font-medium text-gray-700">As low as</span>
                 <span className="text-3xl font-bold text-gray-900">{device.discountPrice}</span>
               </div>
               <div className="text-xs text-gray-500 mt-1">with eligible trade-in</div>
               <div className="text-xs text-gray-500">Retail price: {device.retailPrice}</div>
            </div>
          </div>

          <div className="text-xs text-gray-600 mb-4">
            Limited Time. Req's trade-in of eligible device and elig. unlimited plan (speed restr's apply). Price after up to $1100 in credits over 36 mos. Other terms apply. <span className="underline cursor-pointer">See offer details</span>
          </div>

          <div className="text-xs text-gray-600 mb-6">
            All monthly pricing req's 0% APR, 36-mo. installment agmt. $0 down for well-qual. customers. Tax on full price due at sale. Restrictions apply. <span className="underline cursor-pointer">See price details</span>
          </div>

          {/* Offers Card */}
          <div className="bg-blue-50/50 rounded-xl p-4 mb-8 flex gap-4 items-start relative overflow-hidden">
            <div className="bg-blue-500 text-white rounded-full p-2 mt-1 shrink-0">
               <span className="font-bold text-lg">$</span>
            </div>
            <div className="flex-1">
               <div className="flex justify-between items-start">
                  <h3 className="font-bold text-gray-900 text-lg">You have 6 offers available</h3>
                  <a href="#" className="text-blue-700 text-sm font-semibold hover:underline">See all offers ›</a>
               </div>
               
               <div className="mt-3">
                  <div className="font-bold text-gray-900 text-base">{device.offerText}</div>
                  <div className="text-sm text-gray-600 mt-1">{device.offerSubtext}</div>
                  <div className="mt-3 text-blue-700 font-semibold text-sm cursor-pointer hover:underline">
                    Estimate trade-in value ›
                  </div>
               </div>
            </div>
             <div className="absolute right-4 top-1/2 -translate-y-1/2">
                <button className="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-full shadow-lg transition-transform hover:scale-105">
                   <Bookmark className="w-5 h-5 fill-current" />
                </button>
             </div>
             
             {/* Pagination dots for offers */}
             <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-1.5">
                <div className="w-2 h-2 rounded-full border border-blue-500 bg-transparent"></div>
                <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                <div className="w-2 h-2 rounded-full bg-gray-300"></div>
                <div className="w-2 h-2 rounded-full bg-gray-300"></div>
             </div>
          </div>

          {/* Model Selection */}
          <div className="mb-6">
            <div className="flex justify-between items-baseline mb-2">
               <span className="font-bold text-gray-900">Model</span>
               <button className="text-blue-700 text-sm font-medium flex items-center gap-1">
                 <Maximize2 className="w-3 h-3" /> Compare all iPhones
               </button>
            </div>
            
            <div className="flex gap-4">
              {device.models.map(model => (
                <button
                  key={model.id}
                  onClick={() => setSelectedModel(model)}
                  className={`flex-1 p-3 rounded-xl border-2 text-center transition-all ${
                    selectedModel.id === model.id 
                      ? "border-blue-600 bg-blue-50/20" 
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <div className="font-bold text-gray-900">{model.name}</div>
                  <div className="text-xs text-gray-500 mt-1">{model.display}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Color Selection */}
          <div className="mb-8">
            <div className="mb-3">
              <span className="font-bold text-gray-900">Color: </span>
              <span className="text-gray-700">{selectedColor.name}</span>
            </div>
            <div className="flex gap-3">
              {device.colors.map((color) => (
                <button
                  key={color.name}
                  onClick={() => setSelectedColor(color)}
                  className={`w-10 h-10 rounded-full border-2 relative flex items-center justify-center transition-all ${
                    selectedColor.name === color.name
                      ? "border-blue-600 ring-2 ring-blue-100 ring-offset-2"
                      : "border-transparent hover:scale-105"
                  }`}
                  aria-label={color.name}
                >
                  <div 
                    className="w-full h-full rounded-full border border-black/10 shadow-inner"
                    style={{ backgroundColor: color.hex }}
                  />
                </button>
              ))}
            </div>
          </div>

        </div>
      </div>
      
      {/* Footer Sticky Bar (Mocking the "Continue" area from screenshot) */}
      <div className="sticky bottom-0 bg-white border-t border-gray-200 p-4 flex items-center justify-between z-20">
         <div className="flex flex-col">
            <div className="flex items-baseline gap-1">
               <span className="font-bold text-gray-900 text-lg">{device.discountPrice}</span>
               <span className="text-xs text-gray-500">Monthly</span>
            </div>
            <div className="text-[10px] text-gray-400">Plus taxes and fees.</div>
         </div>
         
         <button className="bg-[#0057B8] hover:bg-[#004899] text-white px-12 py-3 rounded-full font-bold text-lg transition-colors shadow-lg">
            Continue
         </button>
      </div>
    </div>
  );
}
