import React, { useState } from "react";
import { createRoot } from "react-dom/client";

const offerData = {
  id: "65e5f7959a2139672ee90f2e",
  type: "SINGLE_OFFER",
  category: "INSTALL",
  cardId: "RG_HYBRID_OFFER",
  header: "Stay connected with Internet Backup",
  message: "Keep devices online if an outage or connection issue hits.",
  image: "mt_poster_RG_HYBRID_OFFER.png",
  expandCta: "Let's go",
  index: 48,
  version: "RG_HYBRID_OFFER-someversion",
  config: {
    extras: {},
    suppressForSmallBusiness: false,
    downloadSpeedMax: 0,
    alpha: false,
    beta: false,
  },
  generatedDates: [],
  imageUrl:
    "https://d3adodch6dgzf3.cloudfront.net/images/cards/RG_HYBRID_OFFER/mt_poster_RG_HYBRID_OFFER.png",
  hideImageOnExpandedCard: false,
  disableActionForReadOnlyMode: false,
};

const OfferWidget = ({ data }) => {
  const [expanded, setExpanded] = useState(false);

  const handleExpand = () => {
    if (!data.disableActionForReadOnlyMode) {
      setExpanded(true);
    }
  };

  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: "12px",
        maxWidth: "450px",
        margin: "20px auto",
        boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
        padding: "20px",
        background: "#fff",
        fontFamily: "Arial, sans-serif",
        transition: "box-shadow 0.3s ease",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = "0 4px 16px rgba(0,0,0,0.12)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = "0 2px 8px rgba(0,0,0,0.08)";
      }}
    >
      {!expanded || !data.hideImageOnExpandedCard ? (
        <img
          src={data.imageUrl}
          alt={data.header}
          style={{
            width: "100%",
            borderRadius: "8px",
            marginBottom: "16px",
            backgroundColor: "#f5f5f5",
          }}
          onError={(e) => {
            e.target.style.display = "none";
          }}
        />
      ) : null}
      <h2
        style={{
          fontSize: "1.5rem",
          marginBottom: "12px",
          color: "#00468B",
          fontWeight: 600,
        }}
      >
        {data.header}
      </h2>
      <p style={{ color: "#555", marginBottom: "20px", fontSize: "1rem", lineHeight: "1.5" }}>
        {data.message}
      </p>
      {!expanded && (
        <button
          onClick={handleExpand}
          disabled={data.disableActionForReadOnlyMode}
          style={{
            background: data.disableActionForReadOnlyMode ? "#ccc" : "#00468B",
            color: "#fff",
            border: "none",
            padding: "12px 32px",
            borderRadius: "24px",
            cursor: data.disableActionForReadOnlyMode ? "not-allowed" : "pointer",
            fontSize: "1rem",
            fontWeight: 500,
            transition: "background 0.2s",
          }}
          onMouseEnter={(e) => {
            if (!data.disableActionForReadOnlyMode) {
              e.target.style.background = "#003366";
            }
          }}
          onMouseLeave={(e) => {
            if (!data.disableActionForReadOnlyMode) {
              e.target.style.background = "#00468B";
            }
          }}
        >
          {data.expandCta}
        </button>
      )}
      {expanded && (
        <div
          style={{
            marginTop: "20px",
            padding: "16px",
            background: "#e8f5e9",
            borderRadius: "8px",
            border: "1px solid #4caf50",
          }}
        >
          <strong style={{ color: "#2e7d32", fontSize: "1.1rem" }}>
            ✓ Great choice!
          </strong>
          <p style={{ color: "#2e7d32", marginTop: "8px", marginBottom: "12px" }}>
            Internet Backup keeps you connected even during outages. Here's what you get:
          </p>
          <ul style={{ color: "#2e7d32", paddingLeft: "20px", lineHeight: "1.8" }}>
            <li>Automatic failover to backup connection</li>
            <li>Keep working, streaming, and browsing</li>
            <li>No manual switching required</li>
            <li>Peace of mind during outages</li>
          </ul>
          <button
            style={{
              marginTop: "16px",
              background: "#2e7d32",
              color: "#fff",
              border: "none",
              padding: "10px 24px",
              borderRadius: "20px",
              cursor: "pointer",
              fontSize: "0.95rem",
              fontWeight: 500,
            }}
            onClick={() => alert("Redirecting to setup...")}
          >
            Complete Setup
          </button>
        </div>
      )}
    </div>
  );
};

function App() {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(to bottom, #f0f7ff, #ffffff)",
        padding: "40px 20px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <div style={{ maxWidth: "600px", margin: "0 auto" }}>
        <div style={{ textAlign: "center", marginBottom: 30 }}>
          <h1
            style={{
              fontSize: 32,
              color: "#00468B",
              margin: "0 0 12px 0",
              fontWeight: 700,
            }}
          >
            Internet Backup Offer
          </h1>
          <p style={{ fontSize: 16, color: "#666", margin: 0 }}>
            Never lose your connection when you need it most
          </p>
        </div>

        <OfferWidget data={offerData} />

        <div
          style={{
            marginTop: 30,
            padding: 20,
            background: "#fff",
            borderRadius: 12,
            border: "1px solid #e0e0e0",
            textAlign: "center",
          }}
        >
          <p style={{ fontSize: 14, color: "#666", margin: 0 }}>
            💡 <strong>Did you know?</strong> Internet Backup uses your wireless
            network to keep you online during fiber or cable outages.
          </p>
        </div>
      </div>
    </div>
  );
}

createRoot(document.getElementById("att-internet-backup-offer-root")).render(
  <App />
);
