import React, { Suspense } from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import "@/styles/theme.css";
import "leaflet/dist/leaflet.css";
import "./i18n"; // ⚠️ Initialize i18n BEFORE App
import App from "@/App";
import AppErrorBoundary from "./components/AppErrorBoundary";
import Loader from "./components/Loader";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <Suspense fallback={<Loader text="Loading..." />}>
      <AppErrorBoundary>
        <App />
      </AppErrorBoundary>
    </Suspense>
  </React.StrictMode>,
);
