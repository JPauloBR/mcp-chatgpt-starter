import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import { AnimatePresence, motion } from "framer-motion";
import AuthenticationScreen from "./AuthenticationScreen";
import ServiceSelector from "./ServiceSelector";
import AuthenticatedPayment from "./AuthenticatedPayment";
import UnauthenticatedPayment from "./UnauthenticatedPayment";
import ConfirmationScreen from "./ConfirmationScreen";
import paymentData from "./payment-data.json";
import { useOpenAiGlobal } from "../use-openai-global";
import { useMaxHeight } from "../use-max-height";
import { Maximize2 } from "lucide-react";

export default function App() {
  const displayMode = useOpenAiGlobal("displayMode");
  const maxHeight = useMaxHeight() ?? undefined;
  
  // Main application state
  const [currentView, setCurrentView] = useState("loading"); // "loading", "auth", "authenticated", "unauthenticated", "confirmation"
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [widgetState, setWidgetState] = useState({});
  
  // Payment flow state
  const [paymentFlowState, setPaymentFlowState] = useState({
    selectedService: null, // wireless, internet, etc.
    accountInfo: null, // authenticated account or unauthenticated lookup
    paymentData: {
      amount: null,
      paymentMethod: null,
      accountIdentifier: null,
      zipCode: null,
    },
    confirmation: null,
  });

  // Check for pre-provided data from ChatGPT
  useEffect(() => {
    let attempts = 0;
    const maxAttempts = 10;
    const retryDelay = 100;
    
    const checkForState = () => {
      attempts++;
      console.log(`[Payment Widget] Attempt ${attempts}/${maxAttempts}: Checking for toolInput...`);
      console.log('[Payment Widget] window.openai exists:', typeof window !== "undefined" && !!window.openai);
      console.log('[Payment Widget] window.openai.toolInput:', window.openai?.toolInput);
      
      if (typeof window !== "undefined" && window.openai?.toolInput) {
        const toolInput = window.openai.toolInput;
        console.log('[Payment Widget] ✅ Tool input received:', toolInput);
        setWidgetState(toolInput || {});
        
        // Check payment flow hint from ChatGPT
        if (toolInput.paymentFlow === "guest") {
          console.log('[Payment Widget] Guest payment flow detected');
          setIsAuthenticated(false);
          
          // If service type also provided, go directly to unauthenticated payment
          if (toolInput.serviceType) {
            console.log('[Payment Widget] Service type provided:', toolInput.serviceType);
            setPaymentFlowState(prev => ({
              ...prev,
              selectedService: toolInput.serviceType,
            }));
          }
          // Go to unauthenticated view (will show service selector if no service selected)
          setCurrentView("unauthenticated");
        } else if (toolInput.paymentFlow === "authenticated") {
          console.log('[Payment Widget] Authenticated payment flow detected');
          setIsAuthenticated(true);
          setCurrentView("authenticated");
          
          // Pre-populate service type if provided
          if (toolInput.serviceType) {
            setPaymentFlowState(prev => ({
              ...prev,
              selectedService: toolInput.serviceType,
            }));
          }
        } else {
          // No flow specified, show default auth screen
          console.log('[Payment Widget] No flow hint, showing auth screen');
          setCurrentView("auth");
        }
      } else if (attempts < maxAttempts) {
        console.log(`[Payment Widget] ⏳ Tool input not ready, retrying in ${retryDelay}ms...`);
        setTimeout(checkForState, retryDelay);
      } else {
        console.log('[Payment Widget] ❌ Max attempts reached, showing auth screen');
        setCurrentView("auth");
      }
    };
    
    checkForState();
  }, []);

  // Update widget state for ChatGPT
  useEffect(() => {
    if (
      typeof window !== "undefined" &&
      window.oai &&
      typeof window.oai.widget.setState === "function"
    ) {
      window.oai.widget.setState({
        view: currentView,
        isAuthenticated,
        paymentFlowState,
      });
    }
  }, [currentView, isAuthenticated, paymentFlowState]);

  // Handler: User authenticates
  const handleAuthenticated = (userData) => {
    console.log('[Payment Widget] User authenticated:', userData);
    setIsAuthenticated(true);
    setCurrentView("authenticated");
  };

  // Handler: User chooses guest payment
  const handleGuestPayment = () => {
    console.log('[Payment Widget] User chose guest payment');
    setIsAuthenticated(false);
    setCurrentView("unauthenticated");
  };

  // Handler: Service type selected (unauthenticated flow)
  const handleServiceSelect = (serviceType) => {
    console.log('[Payment Widget] Service selected:', serviceType);
    setPaymentFlowState(prev => ({
      ...prev,
      selectedService: serviceType,
    }));
  };

  // Handler: Account selected (authenticated flow)
  const handleAccountSelect = (accountInfo) => {
    console.log('[Payment Widget] Account selected:', accountInfo);
    setPaymentFlowState(prev => ({
      ...prev,
      accountInfo,
      paymentData: {
        ...prev.paymentData,
        amount: accountInfo.balance > 0 ? accountInfo.balance : null,
      },
    }));
  };

  // Handler: Payment submitted
  const handlePaymentSubmit = (paymentDetails) => {
    console.log('[Payment Widget] Payment submitted:', paymentDetails);
    
    // Simulate payment processing
    setTimeout(() => {
      const confirmationNumber = `ATT-PAY-${Math.random().toString(36).substr(2, 9).toUpperCase()}`;
      const confirmation = {
        ...paymentDetails,
        confirmationNumber,
        timestamp: new Date().toISOString(),
        status: 'success',
      };
      
      setPaymentFlowState(prev => ({
        ...prev,
        confirmation,
      }));
      
      setCurrentView("confirmation");
    }, 1500);
  };

  // Handler: Make another payment
  const handleMakeAnotherPayment = () => {
    console.log('[Payment Widget] Make another payment');
    setPaymentFlowState({
      selectedService: null,
      accountInfo: null,
      paymentData: {
        amount: null,
        paymentMethod: null,
        accountIdentifier: null,
        zipCode: null,
      },
      confirmation: null,
    });
    
    if (isAuthenticated) {
      setCurrentView("authenticated");
    } else {
      setCurrentView("unauthenticated");
    }
  };

  // Handler: Return to authentication
  const handleReturnToAuth = () => {
    console.log('[Payment Widget] Return to auth');
    setIsAuthenticated(false);
    setPaymentFlowState({
      selectedService: null,
      accountInfo: null,
      paymentData: {
        amount: null,
        paymentMethod: null,
        accountIdentifier: null,
        zipCode: null,
      },
      confirmation: null,
    });
    setCurrentView("auth");
  };

  // Loading state
  if (currentView === "loading") {
    return (
      <div className="flex items-center justify-center min-h-[480px] bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading payment options...</p>
        </div>
      </div>
    );
  }

  // Main render with container
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <div
        style={{
          maxHeight: displayMode === "fullscreen" ? undefined : maxHeight,
          height: displayMode === "fullscreen" ? "100vh" : "auto",
          minHeight: displayMode === "fullscreen" ? "100vh" : 600,
        }}
        className={
          "relative antialiased w-full overflow-auto " +
          (displayMode === "fullscreen"
            ? "rounded-none border-0 flex-1"
            : "border border-black/10 dark:border-white/10 rounded-2xl sm:rounded-3xl")
        }
      >
        {/* Fullscreen button */}
        {displayMode !== "fullscreen" && currentView !== "auth" && (
          <button
            aria-label="Enter fullscreen"
            className="absolute top-4 right-4 z-30 rounded-full bg-white text-black shadow-lg ring ring-black/5 p-2.5 pointer-events-auto"
            onClick={() => {
              if (window?.webplus?.requestDisplayMode) {
                window.webplus.requestDisplayMode({ mode: "fullscreen" });
              }
            }}
          >
            <Maximize2
              strokeWidth={1.5}
              className="h-4.5 w-4.5"
              aria-hidden="true"
            />
          </button>
        )}

        {/* Main content with transitions */}
        <div className="w-full h-full">
          <AnimatePresence mode="wait">
            {currentView === "auth" && (
              <motion.div
                key="auth"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <AuthenticationScreen
                  onAuthenticated={handleAuthenticated}
                  onGuestPayment={handleGuestPayment}
                />
              </motion.div>
            )}

            {currentView === "authenticated" && (
              <motion.div
                key="authenticated"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                <AuthenticatedPayment
                  accounts={paymentData.mockAccounts.authenticated}
                  selectedService={paymentFlowState.selectedService}
                  onAccountSelect={handleAccountSelect}
                  onPaymentSubmit={handlePaymentSubmit}
                  onSignOut={handleReturnToAuth}
                />
              </motion.div>
            )}

            {currentView === "unauthenticated" && !paymentFlowState.selectedService && (
              <motion.div
                key="service-selector"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                <ServiceSelector
                  services={paymentData.serviceTypes}
                  onServiceSelect={handleServiceSelect}
                  onSignIn={handleReturnToAuth}
                />
              </motion.div>
            )}

            {currentView === "unauthenticated" && paymentFlowState.selectedService && (
              <motion.div
                key="unauthenticated-payment"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                <UnauthenticatedPayment
                  selectedService={paymentFlowState.selectedService}
                  serviceData={paymentData.serviceTypes.find(
                    s => s.id === paymentFlowState.selectedService
                  )}
                  mockAccounts={paymentData.mockAccounts.unauthenticated}
                  onPaymentSubmit={handlePaymentSubmit}
                  onBack={() => setPaymentFlowState(prev => ({ ...prev, selectedService: null }))}
                />
              </motion.div>
            )}

            {currentView === "confirmation" && (
              <motion.div
                key="confirmation"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.3 }}
              >
                <ConfirmationScreen
                  confirmation={paymentFlowState.confirmation}
                  isAuthenticated={isAuthenticated}
                  onMakeAnotherPayment={handleMakeAnotherPayment}
                  onReturnToAccount={handleReturnToAuth}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

createRoot(document.getElementById("att-payment-root")).render(<App />);
