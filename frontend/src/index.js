import React, { Suspense } from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import "@/styles/theme.css";
import "leaflet/dist/leaflet.css";
import App from "@/App";
import "./i18n"; // Initialize i18n
import AppErrorBoundary from "./components/AppErrorBoundary";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <Suspense fallback={
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ width: '64px', height: '64px', margin: '0 auto 1rem', border: '4px solid #ec4899', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
          <p>Loading...</p>
        </div>
      </div>
    }>
      <AppErrorBoundary>
        <App />
      </AppErrorBoundary>
    </Suspense>
  </React.StrictMode>,
);
