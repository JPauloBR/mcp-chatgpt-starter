import React from "react";
import { createRoot } from "react-dom/client";
import plansData from "./plans.json";
import { Signal, Shield, Wifi, Globe, Tv, Award, MessageSquare, Zap } from "lucide-react";

// Icon mapping for features
const iconMap = {
  signal: Signal,
  shield: Shield,
  wifi: Wifi,
  globe: Globe,
  tv: Tv,
  award: Award,
  message: MessageSquare,
  "5g": Zap,
};

function App() {
  const plans = plansData?.plans || [];

  return (
    <div className="antialiased w-full text-black px-4 pb-2 border border-black/10 rounded-2xl sm:rounded-3xl overflow-hidden bg-white">
      <div className="max-w-full">
        {/* Header */}
        <div className="flex flex-row items-center gap-4 sm:gap-4 border-b border-black/5 py-4">
          <div className="sm:w-18 w-16 aspect-square rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center text-white font-bold text-2xl">
            AT&T
          </div>
          <div>
            <div className="text-base sm:text-xl font-medium">
              Wireless Plans
            </div>
            <div className="text-sm text-black/60">
              Compare unlimited plans and find the right fit
            </div>
          </div>
        </div>

        {/* Plans Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 py-4">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className="border border-black/10 rounded-xl p-4 hover:shadow-lg transition-shadow bg-white relative"
            >
              {/* Badge */}
              {plan.badge && (
                <div className="absolute top-4 right-4">
                  <div className="bg-blue-100 text-blue-700 text-xs font-semibold px-2 py-1 rounded-full flex items-center gap-1">
                    <Award className="h-3 w-3" />
                    {plan.badge}
                  </div>
                </div>
              )}

              {/* Plan Header */}
              <div className="mb-4">
                <div className="text-lg font-bold text-black mb-1">
                  {plan.name}
                  <sup className="text-xs font-normal ml-1">{plan.tier}</sup>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-blue-600">
                    {plan.price}
                  </span>
                  {plan.originalPrice && (
                    <span className="text-sm text-black/40 line-through">
                      {plan.originalPrice}
                    </span>
                  )}
                </div>
                <div className="text-xs text-black/60 mt-1">
                  {plan.priceNote}
                </div>
              </div>

              {/* Features List */}
              <div className="space-y-3 mb-4">
                {plan.features.map((feature, idx) => {
                  const IconComponent = iconMap[feature.icon] || Signal;
                  return (
                    <div key={idx} className="flex gap-3">
                      <div className="flex-shrink-0 mt-0.5">
                        <IconComponent
                          strokeWidth={1.5}
                          className="h-4 w-4 text-blue-600"
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-black leading-snug">
                          {feature.title}
                        </div>
                        {feature.description && (
                          <div className="text-xs text-black/60 mt-1">
                            {feature.description}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Select Button */}
              <button
                type="button"
                className="w-full cursor-pointer inline-flex items-center justify-center rounded-lg bg-blue-600 text-white px-4 py-2.5 text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                Select plan
              </button>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {plans.length === 0 && (
          <div className="py-12 text-center text-black/60">
            No plans available.
          </div>
        )}

        {/* Footer Note */}
        <div className="border-t border-black/5 pt-4 pb-2">
          <div className="text-xs text-black/60 text-center">
            Prices below after discount with eligible AutoPay and paperless billing. Discounts start within two bills. Taxes and fees extra. Add'l charges, usage, speed & other restr's apply.
          </div>
        </div>
      </div>
    </div>
  );
}

createRoot(document.getElementById("att-plans-list-root")).render(<App />);
