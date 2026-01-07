import React from "react";
import { createRoot } from "react-dom/client";
import DeviceDetails from "./DeviceDetails";
import { useWidgetProps } from "../use-widget-props";

function App() {
  const props = useWidgetProps({ deviceId: "iphone-17-pro-max" });
  
  return (
    <div className="antialiased w-full min-h-screen bg-gray-50 py-8 px-4 flex justify-center">
      <DeviceDetails deviceId={props?.deviceId} />
    </div>
  );
}

createRoot(document.getElementById("att-device-details-root")).render(<App />);
