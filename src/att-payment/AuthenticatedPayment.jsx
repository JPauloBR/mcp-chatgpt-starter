import React, { useState } from "react";
import { ArrowLeft, Smartphone, Wifi, CreditCard, Building2, ChevronRight, CheckCircle2 } from "lucide-react";

export default function AuthenticatedPayment({ 
  accounts = [], 
  selectedService, 
  onAccountSelect, 
  onPaymentSubmit, 
  onSignOut 
}) {
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [paymentAmount, setPaymentAmount] = useState("");
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [errors, setErrors] = useState({});

  // Get icon for account type
  const getAccountIcon = (type) => {
    switch (type) {
      case "wireless":
        return <Smartphone className="w-6 h-6" />;
      case "internet":
        return <Wifi className="w-6 h-6" />;
      case "business":
        return <Building2 className="w-6 h-6" />;
      default:
        return <CreditCard className="w-6 h-6" />;
    }
  };

  // Handle account selection
  const handleAccountClick = (account) => {
    setSelectedAccount(account);
    // Pre-fill with balance if exists
    if (account.balance > 0) {
      setPaymentAmount(account.balance.toFixed(2));
    }
    // Select default payment method if available
    const defaultMethod = account.paymentMethods?.find(pm => pm.default);
    if (defaultMethod) {
      setSelectedPaymentMethod(defaultMethod);
    } else if (account.paymentMethods?.length > 0) {
      setSelectedPaymentMethod(account.paymentMethods[0]);
    }
    setErrors({});
  };

  // Validate payment amount
  const validateAmount = (amount) => {
    const numAmount = parseFloat(amount);
    if (!amount || amount.trim() === "") {
      return "Payment amount is required";
    }
    if (isNaN(numAmount) || numAmount <= 0) {
      return "Please enter a valid amount";
    }
    if (numAmount > 10000) {
      return "Maximum payment amount is $10,000";
    }
    return null;
  };

  // Handle payment submission
  const handleSubmit = () => {
    const newErrors = {};
    
    // Validate account selection
    if (!selectedAccount) {
      newErrors.account = "Please select an account";
    }
    
    // Validate amount
    const amountError = validateAmount(paymentAmount);
    if (amountError) {
      newErrors.amount = amountError;
    }
    
    // Validate payment method
    if (!selectedPaymentMethod && selectedAccount?.paymentMethods?.length === 0) {
      newErrors.paymentMethod = "Please add a payment method";
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    // Process payment
    setIsProcessing(true);
    
    setTimeout(() => {
      onPaymentSubmit({
        account: selectedAccount,
        amount: parseFloat(paymentAmount),
        paymentMethod: selectedPaymentMethod,
        type: "authenticated"
      });
      setIsProcessing(false);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={onSignOut}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Sign out
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Make a Payment</h1>
          <p className="text-gray-600 mt-2">Select an account and enter payment details</p>
        </div>

        {/* Account Selection */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Account</h2>
          {errors.account && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {errors.account}
            </div>
          )}
          <div className="grid gap-4 md:grid-cols-2">
            {accounts.map((account) => (
              <button
                key={account.accountId}
                onClick={() => handleAccountClick(account)}
                className={
                  "relative bg-white rounded-xl p-6 text-left transition-all duration-200 " +
                  (selectedAccount?.accountId === account.accountId
                    ? "ring-2 ring-blue-500 shadow-lg"
                    : "border border-gray-200 hover:border-blue-300 hover:shadow-md")
                }
              >
                {selectedAccount?.accountId === account.accountId && (
                  <div className="absolute top-4 right-4">
                    <CheckCircle2 className="w-6 h-6 text-blue-600" />
                  </div>
                )}
                
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-blue-50 rounded-lg text-blue-600">
                    {getAccountIcon(account.type)}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 text-lg mb-1">
                      {account.label}
                    </h3>
                    <p className="text-sm text-gray-500 mb-3">
                      Account {account.accountId}
                    </p>
                    <div className="flex items-baseline gap-2">
                      <span className="text-sm text-gray-600">Balance:</span>
                      <span className={
                        "text-2xl font-bold " +
                        (account.balance > 0 ? "text-red-600" : "text-green-600")
                      }>
                        ${account.balance.toFixed(2)}
                      </span>
                    </div>
                    {account.dueDate && account.balance > 0 && (
                      <p className="text-xs text-gray-500 mt-2">
                        Due {new Date(account.dueDate).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Payment Amount */}
        {selectedAccount && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Payment Amount</h2>
            {errors.amount && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {errors.amount}
              </div>
            )}
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <div className="flex items-center gap-3 mb-4">
                <label htmlFor="amount" className="text-gray-700 font-medium">
                  Amount to Pay
                </label>
                {selectedAccount.balance > 0 && (
                  <button
                    onClick={() => setPaymentAmount(selectedAccount.balance.toFixed(2))}
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Pay full balance
                  </button>
                )}
              </div>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 text-xl">
                  $
                </span>
                <input
                  id="amount"
                  type="number"
                  step="0.01"
                  min="0"
                  max="10000"
                  value={paymentAmount}
                  onChange={(e) => {
                    setPaymentAmount(e.target.value);
                    setErrors(prev => ({ ...prev, amount: null }));
                  }}
                  placeholder="0.00"
                  className={
                    "w-full pl-8 pr-4 py-4 text-2xl font-semibold border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all " +
                    (errors.amount ? "border-red-300" : "border-gray-300")
                  }
                />
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Enter an amount between $0.01 and $10,000.00
              </p>
            </div>
          </div>
        )}

        {/* Payment Method */}
        {selectedAccount && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Payment Method</h2>
            {errors.paymentMethod && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {errors.paymentMethod}
              </div>
            )}
            
            {selectedAccount.paymentMethods?.length > 0 ? (
              <div className="space-y-3">
                {selectedAccount.paymentMethods.map((method) => (
                  <button
                    key={method.id}
                    onClick={() => setSelectedPaymentMethod(method)}
                    className={
                      "w-full bg-white rounded-xl p-4 text-left transition-all duration-200 flex items-center justify-between " +
                      (selectedPaymentMethod?.id === method.id
                        ? "ring-2 ring-blue-500 shadow-lg"
                        : "border border-gray-200 hover:border-blue-300 hover:shadow-md")
                    }
                  >
                    <div className="flex items-center gap-4">
                      <div className="p-2 bg-gray-50 rounded-lg">
                        <CreditCard className="w-5 h-5 text-gray-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">
                          {method.brand} •••• {method.last4}
                        </p>
                        {method.default && (
                          <span className="text-xs text-blue-600 font-medium">Default</span>
                        )}
                      </div>
                    </div>
                    {selectedPaymentMethod?.id === method.id && (
                      <CheckCircle2 className="w-5 h-5 text-blue-600" />
                    )}
                  </button>
                ))}
                <button className="w-full bg-white rounded-xl p-4 text-left border border-dashed border-gray-300 hover:border-blue-400 hover:bg-blue-50 transition-all duration-200 flex items-center gap-3 text-blue-600">
                  <div className="p-2 bg-blue-50 rounded-lg">
                    <CreditCard className="w-5 h-5" />
                  </div>
                  <span className="font-medium">Add new payment method</span>
                </button>
              </div>
            ) : (
              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
                <p className="text-yellow-800 mb-4">
                  No saved payment methods found. Please add a payment method to continue.
                </p>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium">
                  Add Payment Method
                </button>
              </div>
            )}
          </div>
        )}

        {/* Submit Button */}
        {selectedAccount && (
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-600">Total Payment</span>
              <span className="text-3xl font-bold text-gray-900">
                ${paymentAmount || "0.00"}
              </span>
            </div>
            <button
              onClick={handleSubmit}
              disabled={isProcessing || !selectedAccount || !paymentAmount}
              className={
                "w-full py-4 rounded-lg font-semibold text-lg transition-all duration-200 " +
                (isProcessing || !selectedAccount || !paymentAmount
                  ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                  : "bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl")
              }
            >
              {isProcessing ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Processing...
                </span>
              ) : (
                "Submit Payment"
              )}
            </button>
            <p className="text-xs text-gray-500 text-center mt-4">
              By submitting, you authorize AT&T to charge the selected payment method.
            </p>
          </div>
        )}

        {/* Empty State */}
        {!selectedAccount && accounts.length === 0 && (
          <div className="bg-white rounded-xl p-12 text-center border border-gray-200">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CreditCard className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No accounts found</h3>
            <p className="text-gray-600">Please contact support to add payment accounts.</p>
          </div>
        )}
      </div>
    </div>
  );
}
