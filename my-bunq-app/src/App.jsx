import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [showNotification, setShowNotification] = useState(false);
  const [showGift, setShowGift] = useState(false);
  const [offer, setOffer] = useState(null);
  const [loadingGift, setLoadingGift] = useState(false);

  // Show notification after 2 seconds
  useEffect(() => {
    const timer = setTimeout(() => setShowNotification(true), 2000);
    return () => clearTimeout(timer);
  }, []);

  // Handler for notification click
  const handleNotificationClick = () => {
    setLoadingGift(true);
    let loaded = false;

    try {
      fetch("http://localhost:8000/should-gift")
        .then((res) => res.json())
        .then((data) => {
          console.log("Successfully fetched gift data:", data);
          loaded = true;
          setOffer(data);
          setShowGift(true);
          setLoadingGift(false);
        });
    } catch (error) {
      console.error("Error fetching gift data:", error);
      loaded = true;
      setLoadingGift(false);
    }

    setTimeout(() => {
      if (!loaded) {
        // If fetch is slow, show the gift page anyway with a placeholder
        setOffer({
          company: "Loading...",
          product: "",
          discount_amount: 0,
          is_free: false,
          location: "",
          start_date: "",
          end_date: "",
          status: "loading",
          created_at: ""
        });
        setShowGift(true);
        setLoadingGift(false);
      }
    }, 5000);
  };

  // Show loading state while fetching the gift, but only if not already showing the gift
  if (loadingGift && !showGift) {
    return (
      <div className="gift-page">
        <div className="gift-header">
          <div className="gift-title">Loading your gift...</div>
        </div>
      </div>
    );
  }

  // Show the gift page if the gift is loaded
  if (showGift && offer) {
    return (
      <div className="gift-page">
        <div className="gift-header">
          <div className="gift-title">
            <div className="gift-company">{offer.company}</div>
            <div className="gift-main-offer">
              <span className="gift-highlight">{offer.product}</span>
            </div>
          </div>
        </div>
        <div className="gift-divider"></div>
        <div className="gift-body">
          <div className="gift-row">
            <span className="gift-label">Standaardtarief</span>
            <span className="gift-original-price">
              {offer.is_free
                ? "€" + offer.discount_amount.toFixed(2)
                : "€" + (offer.discount_amount + 3).toFixed(2)}
            </span>
            <span className="gift-discounted-label">voor</span>
            <span className="gift-discounted-price">
              {offer.is_free ? "€0.00" : "€" + offer.discount_amount.toFixed(2)}
            </span>
          </div>
          <div className="gift-row">
            <span className="gift-label">Locatie:</span>
            <span>{offer.location}</span>
          </div>
          <div className="gift-row">
            <span className="gift-label">Startdatum:</span>
            <span>{offer.start_date.slice(0, 10)}</span>
          </div>
          <div className="gift-row">
            <span className="gift-label">Einddatum:</span>
            <span>{offer.end_date.slice(0, 10)}</span>
          </div>
          <div className="gift-row">
            <span className="gift-label">Status:</span>
            <span className={`gift-status gift-status-${offer.status}`}>{offer.status}</span>
          </div>
        </div>
      </div>
    );
  }

  // Show the homescreen and notification
  return (
    <div className="app">
      <img src="/homescreen.jpg" alt="iPhone Homescreen" className="homescreen" />
      {showNotification && (
        <img
          src="/notification.png"
          alt="Notification"
          className="notification"
          onClick={handleNotificationClick}
        />
      )}
    </div>
  );
}

export default App;