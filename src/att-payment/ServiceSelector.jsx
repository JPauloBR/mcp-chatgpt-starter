import React from "react";
import {
  Signal,
  Router,
  CreditCard,
  Monitor,
  Tv,
  Briefcase,
  ChevronRight,
} from "lucide-react";

// Map icon names to Lucide components
const iconMap = {
  signal: Signal,
  router: Router,
  "credit-card": CreditCard,
  monitor: Monitor,
  tv: Tv,
  briefcase: Briefcase,
};

export default function ServiceSelector({ services, onServiceSelect, onSignIn }) {
  const handleServiceClick = (serviceId) => {
    console.log('[ServiceSelector] Service selected:', serviceId);
    onServiceSelect(serviceId);
  };

  return (
    <div className="min-h-[600px] bg-white p-6 sm:p-8 lg:p-12">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Pay without signing in
          </h1>
          <p className="text-lg text-gray-600">
            Choose the service you want to pay:
          </p>
        </div>

        {/* Service Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          {services.map((service) => {
            const IconComponent = iconMap[service.icon] || Signal;
            
            return (
              <button
                key={service.id}
                onClick={() => handleServiceClick(service.id)}
                className="relative flex flex-col items-center justify-center p-6 bg-white border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:shadow-lg transition-all transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 group min-h-[160px]"
              >
                {/* Icon */}
                <div className="mb-4 p-3 bg-blue-50 rounded-full group-hover:bg-blue-100 transition-colors">
                  <IconComponent
                    className="h-8 w-8 text-blue-600"
                    strokeWidth={2}
                    aria-hidden="true"
                  />
                </div>

                {/* Service Name */}
                <div className="text-center">
                  <h3 className="text-base font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                    {service.name}
                  </h3>
                </div>

                {/* Hover Arrow */}
                <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
                  <ChevronRight className="h-5 w-5 text-blue-600" />
                </div>
              </button>
            );
          })}
        </div>

        {/* Sign In Link */}
        <div className="text-center pt-6 border-t border-gray-200">
          <p className="text-gray-600">
            Not sure?{" "}
            <button
              onClick={onSignIn}
              className="text-blue-600 hover:text-blue-700 font-semibold inline-flex items-center space-x-1 hover:underline"
            >
              <span>Sign in to your account</span>
              <ChevronRight className="h-4 w-4" />
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
