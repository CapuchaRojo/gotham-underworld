import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import LocalHostApp from "./LocalHostApp";

createRoot(document.getElementById("root")!).render(<StrictMode><LocalHostApp /></StrictMode>);
