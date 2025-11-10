import React from "react";
import { CheckCircle2, Wifi, Zap, X } from "lucide-react";
import { motion } from "framer-motion";

export default function AvailabilityResults({ address, availability, plans, onClose }) {
  const { fiber, internetAir, availablePlans = [] } = availability;

  const filteredPlans = availablePlans.map((planId) => plans[planId]).filter(Boolean);

  return (
    <motion.div
      initial={{ x: "100%" }}
      animate={{ x: 0 }}
      exit={{ x: "100%" }}
      transition={{ type: "spring", damping: 30, stiffness: 300 }}
      className="absolute top-0 right-0 bottom-0 w-full lg:w-[480px] xl:w-[520px] bg-white shadow-2xl z-40 overflow-y-auto"
    >
      {/* Header */}
      <div className="sticky top-0 bg-white border-b border-gray-200 p-6 z-10">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {fiber || internetAir ? "Great news! AT&T" : "Limited availability at:"}
              {fiber && " Fiber"}
              {fiber && internetAir && " &"}
              {internetAir && " Internet Air"}
              {(fiber || internetAir) && " is available"}
            </h2>
            <p className="text-sm text-gray-600">{address}</p>
            <button className="text-sm text-blue-600 hover:underline mt-1">Change</button>
          </div>
          <button
            onClick={onClose}
            className="ml-4 p-2 hover:bg-gray-100 rounded-full transition-colors"
            aria-label="Close"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Availability Status */}
        <div className="mt-4 space-y-2">
          {fiber && (
            <div className="flex items-center space-x-2 text-sm">
              <CheckCircle2 className="h-5 w-5 text-blue-600" />
              <span className="font-medium text-gray-900">AT&T Fiber available</span>
              <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-semibold rounded">
                Up to 5 Gig
              </span>
            </div>
          )}
          {internetAir && (
            <div className="flex items-center space-x-2 text-sm">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              <span className="font-medium text-gray-900">AT&T Internet Air available</span>
              <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs font-semibold rounded">
                5G Wireless
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Plans */}
      <div className="p-6 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Pick an internet plan</h3>

        {filteredPlans.map((plan) => (
          <PlanCard key={plan.id} plan={plan} />
        ))}

        {filteredPlans.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <p>No plans available for this location</p>
          </div>
        )}

        {/* Additional Info */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-100">
          <div className="flex items-start space-x-3">
            <Zap className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-gray-700">
              <p className="font-semibold mb-1">Need help choosing a speed?</p>
              <p className="text-gray-600">
                Answer two questions to find out which fiber plan is best for your home.
              </p>
              <button className="text-blue-600 hover:underline mt-2 font-medium">
                Help me choose
              </button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function PlanCard({ plan }) {
  return (
    <div className="border border-gray-200 rounded-xl p-5 hover:border-blue-300 hover:shadow-md transition-all">
      {plan.badge && (
        <div className="mb-3">
          <span className="inline-flex items-center px-2.5 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded">
            ⭐ {plan.badge}
          </span>
        </div>
      )}

      <div className="mb-3">
        <h4 className="text-sm font-medium text-gray-600 mb-1">{plan.name}</h4>
        <p className="text-2xl font-bold text-gray-900">{plan.speed}</p>
      </div>

      <div className="mb-4">
        <div className="flex items-baseline space-x-2">
          {plan.originalPrice > plan.price && (
            <span className="text-lg text-gray-400 line-through">${plan.originalPrice}.00/mo.</span>
          )}
          <span className="text-3xl font-bold text-gray-900">${plan.price}.00</span>
          <span className="text-gray-600">/mo</span>
        </div>
        <p className="text-xs text-gray-500 mt-1">Plus taxes and fees</p>
      </div>

      {/* Features */}
      <ul className="space-y-2 mb-5">
        {plan.features.map((feature, idx) => (
          <li key={idx} className="flex items-start text-sm text-gray-700">
            <CheckCircle2 className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
            <span>{feature}</span>
          </li>
        ))}
      </ul>

      {/* Action Button */}
      <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-full transition-colors duration-200">
        Select this plan
      </button>

      {plan.type === "fiber" && (
        <div className="mt-3 flex items-center justify-center space-x-2 text-xs text-gray-500">
          <Wifi className="h-3 w-3" />
          <span>Wi-Fi 6 gateway included</span>
        </div>
      )}
    </div>
  );
}
