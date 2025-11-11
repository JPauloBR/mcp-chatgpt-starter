import React, { useState } from "react";
import { ChevronRight, Plus, Minus } from "lucide-react";

export default function AuthenticationScreen({ onAuthenticated, onGuestPayment }) {
  const [savedUsers] = useState([
    {
      id: "user-1",
      email: "jpaulo.araras@gmail.com",
      services: ["AT&T Mail", "Wireless", "Internet"],
    },
  ]);

  const handleUserSelect = (user) => {
    // Simulate authentication
    console.log('[Auth] User selected:', user.email);
    onAuthenticated({
      email: user.email,
      services: user.services,
      authenticated: true,
    });
  };

  return (
    <div className="flex items-center justify-center min-h-[600px] bg-white p-6">
      <div className="w-full max-w-md">
        {/* AT&T Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 mb-6">
            {/* AT&T Globe Icon */}
            <svg
              viewBox="0 0 200 200"
              className="w-full h-full"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle cx="100" cy="100" r="90" fill="#009FDB" />
              <circle cx="100" cy="100" r="70" fill="none" stroke="white" strokeWidth="3" />
              <path
                d="M 40 100 Q 100 60 160 100"
                stroke="white"
                strokeWidth="3"
                fill="none"
              />
              <path
                d="M 40 100 Q 100 140 160 100"
                stroke="white"
                strokeWidth="3"
                fill="none"
              />
              <line x1="100" y1="30" x2="100" y2="170" stroke="white" strokeWidth="3" />
            </svg>
          </div>
          <h1 className="text-2xl font-semibold text-gray-900 mb-2">
            Select user ID
          </h1>
          <p className="text-base text-gray-600">to continue</p>
        </div>

        {/* Saved User IDs */}
        {savedUsers.length > 0 && (
          <div className="space-y-3 mb-6">
            {savedUsers.map((user) => (
              <button
                key={user.id}
                onClick={() => handleUserSelect(user)}
                className="w-full flex items-center justify-between p-4 bg-white border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all group"
              >
                <div className="text-left">
                  <div className="font-medium text-gray-900 mb-1">
                    {user.email}
                  </div>
                  <div className="text-sm text-gray-500">
                    {user.services.join(" · ")}
                  </div>
                </div>
                <ChevronRight
                  className="h-5 w-5 text-gray-400 group-hover:text-blue-600 transition-colors"
                  aria-hidden="true"
                />
              </button>
            ))}
          </div>
        )}

        {/* Add/Remove User Options */}
        <div className="space-y-3 mb-8">
          <button className="w-full flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium py-2 px-3 hover:bg-blue-50 rounded-lg transition-colors">
            <Plus className="h-5 w-5" />
            <span>Add user ID</span>
          </button>
          <button className="w-full flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium py-2 px-3 hover:bg-blue-50 rounded-lg transition-colors">
            <Minus className="h-5 w-5" />
            <span>Remove user ID</span>
          </button>
        </div>

        {/* Pay Without Signing In */}
        <div className="pt-6 border-t border-gray-200">
          <button
            onClick={onGuestPayment}
            className="w-full flex items-center justify-center space-x-2 text-blue-600 hover:text-blue-700 font-semibold text-lg py-3 px-4 hover:bg-blue-50 rounded-lg transition-colors"
          >
            <span>Pay without signing in</span>
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>

        {/* Additional Help Text */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500">
            Don't have an account?{" "}
            <a href="#" className="text-blue-600 hover:text-blue-700 font-medium">
              Sign up
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
