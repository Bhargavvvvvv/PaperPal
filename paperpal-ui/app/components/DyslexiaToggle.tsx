"use client";

import { useState, useEffect } from "react";

export default function DyslexiaToggle() {
    const [isActive, setIsActive] = useState(false);

    // 1. Check local storage when the component loads
    useEffect(() => {
        const savedMode = localStorage.getItem("dyslexiaMode") === "true";
        setIsActive(savedMode);

        if (savedMode) {
            document.body.classList.add("dyslexia-mode");
        }
    }, []);

    // 2. Handle the toggle click
    const toggleMode = () => {
        const newState = !isActive;
        setIsActive(newState);
        localStorage.setItem("dyslexiaMode", String(newState));

        if (newState) {
            document.body.classList.add("dyslexia-mode");
        } else {
            document.body.classList.remove("dyslexia-mode");
        }
    };

    // 3. Render the button
    return (
        <button
            onClick={toggleMode}
            style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                padding: "6px 14px",
                borderRadius: "20px",
                border: isActive ? "1px solid #d4a373" : "1px solid #e5e7eb",
                backgroundColor: isActive ? "#faedcd" : "#f9fafb",
                color: isActive ? "#5e3a15" : "#4b5563",
                fontSize: "0.85rem",
                fontWeight: "bold",
                cursor: "pointer",
                transition: "all 0.2s ease"
            }}
            title="Toggle Dyslexia Focus Mode"
        >
            <span>{isActive ? "Focus Mode On" : "Focus Mode Off"}</span>
        </button>
    );
}