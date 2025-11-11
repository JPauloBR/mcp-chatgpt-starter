import React from "react";
import { CheckCircle, Receipt, CreditCard, Home } from "lucide-react";

export default function ConfirmationScreen({
  confirmation,
  isAuthenticated,
  onMakeAnotherPayment,
  onReturnToAccount,
}) {
  if (!confirmation) {
    return (
      <div className="min-h-[600px] bg-white p-6 flex items-center justify-center">
        <p className="text-gray-500">No confirmation data available</p>
      </div>
    );
  }

  return (
    <div className="min-h-[600px] bg-white p-6 sm:p-8 lg:p-12">
      <div className="max-w-2xl mx-auto">
        {/* Success Icon */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-4">
            <CheckCircle className="h-12 w-12 text-green-600" />
          </div>
          <h1 className="text-3xl font-bold text-green-600 mb-2">
            Payment Successful!
          </h1>
          <p className="text-gray-600">
            Thank you for your payment. You will receive a confirmation email.
          </p>
        </div>

        {/* Payment Details */}
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Payment Details
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Confirmation:</span>
              <span className="font-mono font-medium text-gray-900">
                {confirmation.confirmationNumber}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Amount:</span>
              <span className="font-semibold text-gray-900">
                ${confirmation.amount?.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Date/Time:</span>
              <span className="text-gray-900">
                {new Date(confirmation.timestamp).toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={onMakeAnotherPayment}
            className="w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            <CreditCard className="h-5 w-5" />
            <span>Make Another Payment</span>
          </button>

          {isAuthenticated && (
            <button
              onClick={onReturnToAccount}
              className="w-full flex items-center justify-center space-x-2 bg-white hover:bg-gray-50 text-blue-600 font-semibold py-3 px-6 rounded-lg border-2 border-blue-600 transition-colors"
            >
              <Home className="h-5 w-5" />
              <span>Return to Account</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
