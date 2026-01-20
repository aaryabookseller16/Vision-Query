/**
 * main.jsx
 *
 * Entry point for the VisionQuery React application.
 *
 * Responsibilities:
 * - Import global CSS resets (index.css)
 * - Mount the root <App /> component into the DOM
 * - Wrap the app in React.StrictMode for dev-time checks
 *
 * Note:
 * - No application logic should live here.
 * - UI and state belong in App.jsx and child components.
 */

import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./index.css";

// Create the React root and render the application
createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
