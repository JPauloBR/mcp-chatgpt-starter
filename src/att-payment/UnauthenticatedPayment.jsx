import React, { useState } from "react";
import { ArrowLeft, CreditCard, Building2, Phone, Mail, AlertCircle } from "lucide-react";

export default function UnauthenticatedPayment({
  selectedService,
  serviceData,
  mockAccounts,
  onPaymentSubmit,
  onBack,
}) {
  const [step, setStep] = useState(1); // 1: Account lookup, 2: Payment details
  const [accountIdentifier, setAccountIdentifier] = useState("");
  const [zipCode, setZipCode] = useState("");
  const [accountInfo, setAccountInfo] = useState(null);
  const [paymentAmount, setPaymentAmount] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("credit-card"); // credit-card or bank-account
  const [isProcessing, setIsProcessing] = useState(false);
  const [errors, setErrors] = useState({});
  
  // Credit card fields
  const [cardNumber, setCardNumber] = useState("");
  const [expirationDate, setExpirationDate] = useState("");
  const [cvv, setCvv] = useState("");
  const [cardholderName, setCardholderName] = useState("");
  const [billingZip, setBillingZip] = useState("");
  
  // Bank account fields
  const [routingNumber, setRoutingNumber] = useState("");
  const [accountNumber, setAccountNumber] = useState("");
  const [accountHolderName, setAccountHolderName] = useState("");
  const [accountType, setAccountType] = useState("checking");

  // Validate account identifier
  const validateIdentifier = () => {
    if (!accountIdentifier) {
      return "Account identifier is required";
    }
    if (selectedService === "wireless" && accountIdentifier.length !== 10) {
      return "Wireless number must be 10 digits";
    }
    return null;
  };

  // Validate ZIP code
  const validateZipCode = () => {
    if (!zipCode) {
      return "ZIP code is required";
    }
    if (zipCode.length !== 5 || !/^\d{5}$/.test(zipCode)) {
      return "ZIP code must be 5 digits";
    }
    return null;
  };

  // Handle account lookup
  const handleLookupAccount = () => {
    const newErrors = {};
    
    const identifierError = validateIdentifier();
    if (identifierError) {
      newErrors.identifier = identifierError;
    }
    
    const zipError = validateZipCode();
    if (zipError) {
      newErrors.zip = zipError;
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    // Look up account in mock data
    const account = mockAccounts[accountIdentifier];
    if (account && account.zipCode === zipCode) {
      setAccountInfo({
        accountId: accountIdentifier,
        ...account
      });
      setPaymentAmount(account.balance.toFixed(2));
      setStep(2);
      setErrors({});
    } else {
      setErrors({
        identifier: "Account not found or ZIP code doesn't match"
      });
    }
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

  // Validate credit card
  const validateCreditCard = () => {
    const errors = {};
    if (!cardNumber || cardNumber.replace(/\s/g, "").length !== 16) {
      errors.cardNumber = "Card number must be 16 digits";
    }
    if (!expirationDate || !/^\d{2}\/\d{2}$/.test(expirationDate)) {
      errors.expirationDate = "Format: MM/YY";
    }
    if (!cvv || cvv.length < 3) {
      errors.cvv = "CVV required";
    }
    if (!cardholderName) {
      errors.cardholderName = "Cardholder name required";
    }
    if (!billingZip || billingZip.length !== 5) {
      errors.billingZip = "ZIP code must be 5 digits";
    }
    return errors;
  };

  // Validate bank account
  const validateBankAccount = () => {
    const errors = {};
    if (!routingNumber || routingNumber.length !== 9) {
      errors.routingNumber = "Routing number must be 9 digits";
    }
    if (!accountNumber || accountNumber.length < 4) {
      errors.accountNumber = "Account number required";
    }
    if (!accountHolderName) {
      errors.accountHolderName = "Account holder name required";
    }
    return errors;
  };

  // Handle payment submission
  const handleSubmit = () => {
    const newErrors = {};
    
    // Validate amount
    const amountError = validateAmount(paymentAmount);
    if (amountError) {
      newErrors.amount = amountError;
    }
    
    // Validate payment method
    if (paymentMethod === "credit-card") {
      Object.assign(newErrors, validateCreditCard());
    } else {
      Object.assign(newErrors, validateBankAccount());
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    // Process payment
    setIsProcessing(true);
    
    setTimeout(() => {
      onPaymentSubmit({
        account: accountInfo,
        amount: parseFloat(paymentAmount),
        paymentMethod: paymentMethod === "credit-card" ? {
          type: "credit-card",
          last4: cardNumber.slice(-4),
          brand: "Credit Card"
        } : {
          type: "bank-account",
          last4: accountNumber.slice(-4),
          accountType
        },
        type: "unauthenticated"
      });
      setIsProcessing(false);
    }, 1500);
  };

  // Format card number
  const formatCardNumber = (value) => {
    const v = value.replace(/\s+/g, "").replace(/[^0-9]/gi, "");
    const matches = v.match(/\d{4,16}/g);
    const match = (matches && matches[0]) || "";
    const parts = [];
    for (let i = 0; i < match.length; i += 4) {
      parts.push(match.substring(i, i + 4));
    }
    if (parts.length) {
      return parts.join(" ");
    }
    return value;
  };

  // Format expiration date
  const formatExpirationDate = (value) => {
    const v = value.replace(/\s+/g, "").replace(/[^0-9]/gi, "");
    if (v.length >= 2) {
      return v.slice(0, 2) + "/" + v.slice(2, 4);
    }
    return v;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Guest Payment</h1>
          <p className="text-gray-600 mt-2">{serviceData?.name || "Make a payment"}</p>
        </div>

        {/* Step Indicator */}
        <div className="flex items-center justify-center mb-8">
          <div className="flex items-center gap-2">
            <div className={"w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold " + (step === 1 ? "bg-blue-600 text-white" : "bg-green-600 text-white")}>
              {step > 1 ? "✓" : "1"}
            </div>
            <span className="text-sm font-medium text-gray-600">Account Info</span>
          </div>
          <div className="w-16 h-0.5 bg-gray-300 mx-2" />
          <div className="flex items-center gap-2">
            <div className={"w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold " + (step === 2 ? "bg-blue-600 text-white" : "bg-gray-300 text-gray-600")}>
              2
            </div>
            <span className="text-sm font-medium text-gray-600">Payment Details</span>
          </div>
        </div>

        {/* Step 1: Account Lookup */}
        {step === 1 && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Enter Account Information</h2>
              
              {/* Account Identifier */}
              <div className="mb-4">
                <label htmlFor="identifier" className="block text-sm font-medium text-gray-700 mb-2">
                  {serviceData?.identifierLabel || "Account Number"}
                </label>
                <input
                  id="identifier"
                  type="text"
                  value={accountIdentifier}
                  onChange={(e) => {
                    setAccountIdentifier(e.target.value);
                    setErrors(prev => ({ ...prev, identifier: null }));
                  }}
                  placeholder={serviceData?.identifierPlaceholder || "Enter account number"}
                  className={
                    "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all " +
                    (errors.identifier ? "border-red-300" : "border-gray-300")
                  }
                />
                {errors.identifier && (
                  <p className="mt-2 text-sm text-red-600 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {errors.identifier}
                  </p>
                )}
              </div>

              {/* ZIP Code */}
              <div className="mb-6">
                <label htmlFor="zip" className="block text-sm font-medium text-gray-700 mb-2">
                  Billing ZIP Code
                </label>
                <input
                  id="zip"
                  type="text"
                  maxLength="5"
                  value={zipCode}
                  onChange={(e) => {
                    setZipCode(e.target.value.replace(/\D/g, ""));
                    setErrors(prev => ({ ...prev, zip: null }));
                  }}
                  placeholder="12345"
                  className={
                    "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all " +
                    (errors.zip ? "border-red-300" : "border-gray-300")
                  }
                />
                {errors.zip && (
                  <p className="mt-2 text-sm text-red-600 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {errors.zip}
                  </p>
                )}
              </div>

              <button
                onClick={handleLookupAccount}
                className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Continue
              </button>
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> For testing, use account number <code className="bg-blue-100 px-1 rounded">{selectedService === "wireless" ? "4705959137" : "338086151"}</code> with ZIP <code className="bg-blue-100 px-1 rounded">30092</code>
              </p>
            </div>
          </div>
        )}

        {/* Step 2: Payment Details */}
        {step === 2 && accountInfo && (
          <div className="space-y-6">
            {/* Account Summary */}
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-3">Account Summary</h3>
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">Account:</span>
                <span className="font-medium">{accountInfo.accountId}</span>
              </div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">Balance:</span>
                <span className="text-xl font-bold text-red-600">${accountInfo.balance.toFixed(2)}</span>
              </div>
            </div>

            {/* Payment Amount */}
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-4">Payment Amount</h3>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 text-xl">$</span>
                <input
                  type="number"
                  step="0.01"
                  value={paymentAmount}
                  onChange={(e) => {
                    setPaymentAmount(e.target.value);
                    setErrors(prev => ({ ...prev, amount: null }));
                  }}
                  className={
                    "w-full pl-8 pr-4 py-3 text-xl font-semibold border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none " +
                    (errors.amount ? "border-red-300" : "border-gray-300")
                  }
                />
                {errors.amount && (
                  <p className="mt-2 text-sm text-red-600">{errors.amount}</p>
                )}
              </div>
            </div>

            {/* Payment Method Selection */}
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-4">Payment Method</h3>
              <div className="flex gap-3 mb-6">
                <button
                  onClick={() => setPaymentMethod("credit-card")}
                  className={
                    "flex-1 py-3 px-4 border-2 rounded-lg font-medium transition-all " +
                    (paymentMethod === "credit-card"
                      ? "border-blue-600 bg-blue-50 text-blue-700"
                      : "border-gray-300 text-gray-700 hover:border-gray-400")
                  }
                >
                  <CreditCard className="w-5 h-5 mx-auto mb-1" />
                  Credit Card
                </button>
                <button
                  onClick={() => setPaymentMethod("bank-account")}
                  className={
                    "flex-1 py-3 px-4 border-2 rounded-lg font-medium transition-all " +
                    (paymentMethod === "bank-account"
                      ? "border-blue-600 bg-blue-50 text-blue-700"
                      : "border-gray-300 text-gray-700 hover:border-gray-400")
                  }
                >
                  <Building2 className="w-5 h-5 mx-auto mb-1" />
                  Bank Account
                </button>
              </div>

              {/* Credit Card Form */}
              {paymentMethod === "credit-card" && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Card Number</label>
                    <input
                      type="text"
                      maxLength="19"
                      value={cardNumber}
                      onChange={(e) => {
                        setCardNumber(formatCardNumber(e.target.value));
                        setErrors(prev => ({ ...prev, cardNumber: null }));
                      }}
                      placeholder="1234 5678 9012 3456"
                      className={
                        "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none " +
                        (errors.cardNumber ? "border-red-300" : "border-gray-300")
                      }
                    />
                    {errors.cardNumber && <p className="mt-1 text-sm text-red-600">{errors.cardNumber}</p>}
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Expiration Date</label>
                      <input
                        type="text"
                        maxLength="5"
                        value={expirationDate}
                        onChange={(e) => {
                          setExpirationDate(formatExpirationDate(e.target.value));
                          setErrors(prev => ({ ...prev, expirationDate: null }));
                        }}
                        placeholder="MM/YY"
                        className={
                          "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none " +
                          (errors.expirationDate ? "border-red-300" : "border-gray-300")
                        }
                      />
                      {errors.expirationDate && <p className="mt-1 text-sm text-red-600">{errors.expirationDate}</p>}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">CVV</label>
                      <input
                        type="text"
                        maxLength="4"
                        value={cvv}
                        onChange={(e) => {
                          setCvv(e.target.value.replace(/\D/g, ""));
                          setErrors(prev => ({ ...prev, cvv: null }));
                        }}
                        placeholder="123"
                        className={
                          "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none " +
                          (errors.cvv ? "border-red-300" : "border-gray-300")
                        }
                      />
                      {errors.cvv && <p className="mt-1 text-sm text-red-600">{errors.cvv}</p>}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Cardholder Name</label>
                    <input
                      type="text"
                      value={cardholderName}
                      onChange={(e) => {
                        setCardholderName(e.target.value);
                        setErrors(prev => ({ ...prev, cardholderName: null }));
                      }}
                      placeholder="John Doe"
                      className={
                        "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none " +
                        (errors.cardholderName ? "border-red-300" : "border-gray-300")
                      }
                    />
                    {errors.cardholderName && <p className="mt-1 text-sm text-red-600">{errors.cardholderName}</p>}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Billing ZIP Code</label>
                    <input
                      type="text"
                      maxLength="5"
                      value={billingZip}
                      onChange={(e) => {
                        setBillingZip(e.target.value.replace(/\D/g, ""));
                        setErrors(prev => ({ ...prev, billingZip: null }));
                      }}
                      placeholder="12345"
                      className={
                        "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none " +
                        (errors.billingZip ? "border-red-300" : "border-gray-300")
                      }
                    />
                    {errors.billingZip && <p className="mt-1 text-sm text-red-600">{errors.billingZip}</p>}
                  </div>
                </div>
              )}

              {/* Bank Account Form */}
              {paymentMethod === "bank-account" && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Account Type</label>
                    <select
                      value={accountType}
                      onChange={(e) => setAccountType(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    >
                      <option value="checking">Checking</option>
                      <option value="savings">Savings</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Routing Number</label>
                    <input
                      type="text"
                      maxLength="9"
                      value={routingNumber}
                      onChange={(e) => {
                        setRoutingNumber(e.target.value.replace(/\D/g, ""));
                        setErrors(prev => ({ ...prev, routingNumber: null }));
                      }}
                      placeholder="123456789"
                      className={
                        "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none " +
                        (errors.routingNumber ? "border-red-300" : "border-gray-300")
                      }
                    />
                    {errors.routingNumber && <p className="mt-1 text-sm text-red-600">{errors.routingNumber}</p>}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Account Number</label>
                    <input
                      type="text"
                      value={accountNumber}
                      onChange={(e) => {
                        setAccountNumber(e.target.value.replace(/\D/g, ""));
                        setErrors(prev => ({ ...prev, accountNumber: null }));
                      }}
                      placeholder="1234567890"
                      className={
                        "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none " +
                        (errors.accountNumber ? "border-red-300" : "border-gray-300")
                      }
                    />
                    {errors.accountNumber && <p className="mt-1 text-sm text-red-600">{errors.accountNumber}</p>}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Account Holder Name</label>
                    <input
                      type="text"
                      value={accountHolderName}
                      onChange={(e) => {
                        setAccountHolderName(e.target.value);
                        setErrors(prev => ({ ...prev, accountHolderName: null }));
                      }}
                      placeholder="John Doe"
                      className={
                        "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none " +
                        (errors.accountHolderName ? "border-red-300" : "border-gray-300")
                      }
                    />
                    {errors.accountHolderName && <p className="mt-1 text-sm text-red-600">{errors.accountHolderName}</p>}
                  </div>
                </div>
              )}
            </div>

            {/* Submit Button */}
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <span className="text-gray-600">Total Payment</span>
                <span className="text-3xl font-bold text-gray-900">${paymentAmount || "0.00"}</span>
              </div>
              <button
                onClick={handleSubmit}
                disabled={isProcessing}
                className={
                  "w-full py-4 rounded-lg font-semibold text-lg transition-all duration-200 " +
                  (isProcessing
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
                By submitting, you authorize AT&T to charge the provided payment method.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
