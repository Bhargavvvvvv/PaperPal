"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import "./globals.css";
import DyslexiaToggle from "./components/DyslexiaToggle"
export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState("");
  const [dragging, setDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped?.type === "application/pdf") setFile(dropped);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const picked = e.target.files?.[0];
    if (picked) setFile(picked);
  };

  const handleUploadSubmit = async () => {
    if (!file || isUploading) return;
    setIsUploading(true);
    console.log("check1")
    try {
      const formData = new FormData();
      formData.append("file", file);
      if (question.trim()) {
        formData.append("question", question.trim());
      }

      const response = await fetch("http://127.0.0.1:5000/api/process-document", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }

      const data = await response.json();

      if (data.status === "success") {
        console.log("success")
        // Save the backend data to sessionStorage so the next page can read it
        sessionStorage.setItem("chatHistory", JSON.stringify(data.chat_history));
        sessionStorage.setItem("fileName", file.name);

        // Navigate to the chat page
        router.push("/chat");
      } else {
        alert(data.message || "An error occurred while processing the document.");
      }
    } catch (error) {
      console.log("check2")
      console.error("Upload failed:", error);
      alert("Failed to upload the document. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const dropzoneClass = [
    "dropzone",
    dragging ? "dropzone--dragging" : "",
    file && !dragging ? "dropzone--has-file" : "",
  ].filter(Boolean).join(" ");

  return (
    <div className="upload-page">
      <div className="upload-page__bg" />
      <div className="upload-page__blob--green" />
      <div className="upload-page__blob--orange" />

      <div className="upload-page__header">
        <div className="upload-page__logo-row">
          <span className="upload-page__logo-icon">📄</span>
          <h1 className="upload-page__logo-text">
            Paper<span>Pal</span>
          </h1>
          <DyslexiaToggle />
        </div>
        <p className="upload-page__tagline">
          Upload your research paper and get clear, easy to understand answers designed for every kind of thinker.
        </p>
      </div>

      <div className="upload-card">
        <div
          className={dropzoneClass}
          onClick={() => !isUploading && fileInputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          style={{ cursor: isUploading ? "not-allowed" : "pointer" }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            style={{ display: "none" }} onChange={handleFileChange}
            disabled={isUploading}
          />

          {file ? (
            <>
              <span className="dropzone__icon"></span>
              <p className="dropzone__file-name">{file.name}</p>
              <p className="dropzone__file-size">
                {(file.size / 1024).toFixed(0)} KB — click to change
              </p>
            </>
          ) : (
            <>
              <span className="dropzone__icon">📂</span>
              <p className="dropzone__title">Drop your PDF here</p>
              <p className="dropzone__sub">or click to browse files</p>
            </>
          )}
        </div>

        <div className="question-field">
          <label className="question-field__label">
            Got a question? <span>(optional)</span>
          </label>
          <textarea
            className="question-field__textarea"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. What is the main finding of this paper?"
            rows={3}
            disabled={isUploading}
          />
          <p className="question-field__hint">
            If you skip this, we'll generate a clear summary automatically.
          </p>
        </div>

        <button
          onClick={handleUploadSubmit}
          disabled={!file || isUploading}
          className={`submit-btn ${file && !isUploading ? "submit-btn--active" : "submit-btn--disabled"}`}
        >
          {isUploading ? "Processing Paper..." : file ? "Analyse Paper" : "Upload a PDF to continue"}
        </button>
      </div>

      <p className="upload-page__a11y-note">
        Designed with dyslexia friendly fonts and spacing for comfortable reading.
      </p>
    </div>
  );
}