import React from "react";
import { createRoot } from "react-dom/client";

// Sample recommendations data
const recommendations = [
  {
    id: "657759fa955b48e62586b36c",
    type: "OTHER",
    category: "OFFERS",
    cardId: "RG_SECURITY_OFFER",
    header: "AT&T ActiveArmor internet security",
    message: "Included with your Internet Plan",
    image: "forYou_security.png",
    expandCta: "Activate",
    index: 21,
    version: "RG_SECURITY_OFFER-20200903",
    imageUrl:
      "https://d3adodch6dgzf3.cloudfront.net/images/cards/RG_SECURITY_OFFER/forYou_security.png",
  },
  {
    id: "657759fa955b48e62586b37d",
    type: "OTHER",
    category: "OFFERS",
    cardId: "FIBER_UPGRADE",
    header: "Upgrade to AT&T Fiber",
    message: "Get faster speeds up to 5 Gig",
    image: "forYou_fiber.png",
    expandCta: "Learn More",
    index: 22,
    imageUrl:
      "https://www.att.com/ecms/dam/att/consumer/help/images/service-1col/u-verse-tv-logo-200x200.png",
  },
  {
    id: "657759fa955b48e62586b38e",
    type: "OTHER",
    category: "OFFERS",
    cardId: "WIRELESS_BUNDLE",
    header: "Bundle and Save",
    message: "Get $20/mo off when you bundle wireless + internet",
    image: "forYou_bundle.png",
    expandCta: "View Offer",
    index: 23,
    imageUrl:
      "https://www.att.com/ecms/dam/att/consumer/global/devices/phones/apple/apple-iphone-15-pro/carousel/max-blue-1.png",
  },
];

const RecommendationCard = ({ offer }) => (
  <div
    style={{
      maxWidth: 360,
      border: "1px solid #e0e0e0",
      borderRadius: 12,
      boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
      overflow: "hidden",
      fontFamily: "Arial, sans-serif",
      background: "#fff",
      margin: 16,
      transition: "transform 0.2s, box-shadow 0.2s",
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = "translateY(-4px)";
      e.currentTarget.style.boxShadow = "0 4px 16px rgba(0,0,0,0.12)";
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = "translateY(0)";
      e.currentTarget.style.boxShadow = "0 2px 8px rgba(0,0,0,0.08)";
    }}
  >
    <img
      src={offer.imageUrl}
      alt={offer.header}
      style={{
        width: "100%",
        objectFit: "cover",
        height: 160,
        backgroundColor: "#f5f5f5",
      }}
      onError={(e) => {
        e.target.style.display = "none";
      }}
    />
    <div style={{ padding: 20 }}>
      <h2
        style={{
          fontSize: 20,
          margin: "0 0 8px 0",
          color: "#00468B",
          fontWeight: 600,
        }}
      >
        {offer.header}
      </h2>
      <p style={{ fontSize: 15, margin: "0 0 16px 0", color: "#444" }}>
        {offer.message}
      </p>
      <button
        style={{
          background: "#00468B",
          color: "#fff",
          border: "none",
          borderRadius: 24,
          padding: "12px 28px",
          fontSize: 16,
          cursor: "pointer",
          fontWeight: 500,
          transition: "background 0.2s",
        }}
        onMouseEnter={(e) => {
          e.target.style.background = "#003366";
        }}
        onMouseLeave={(e) => {
          e.target.style.background = "#00468B";
        }}
        onClick={() => alert(`${offer.expandCta} clicked for: ${offer.header}`)}
      >
        {offer.expandCta}
      </button>
    </div>
  </div>
);

function App() {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(to bottom, #f8f9fa, #ffffff)",
        padding: "40px 20px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <h1
            style={{
              fontSize: 36,
              color: "#00468B",
              margin: "0 0 12px 0",
              fontWeight: 700,
            }}
          >
            For You
          </h1>
          <p style={{ fontSize: 18, color: "#666", margin: 0 }}>
            Personalized recommendations based on your AT&T services
          </p>
        </div>

        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "center",
            gap: 20,
          }}
        >
          {recommendations.map((offer) => (
            <RecommendationCard key={offer.id} offer={offer} />
          ))}
        </div>

        <div
          style={{
            textAlign: "center",
            marginTop: 40,
            padding: 20,
            background: "#f0f7ff",
            borderRadius: 12,
            border: "1px solid #d0e4ff",
          }}
        >
          <p style={{ fontSize: 16, color: "#00468B", margin: 0 }}>
            💡 <strong>Tip:</strong> These offers are tailored to your account.
            Check back regularly for new recommendations!
          </p>
        </div>
      </div>
    </div>
  );
}

createRoot(document.getElementById("att-for-you-root")).render(<App />);
