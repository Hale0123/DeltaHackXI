import React, { useRef, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import './App.css';

function Home() {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [result, setResult] = useState("");
    const [cameraEnabled, setCameraEnabled] = useState(false);
    const [mode, setMode] = useState("camera");
    const [selectedFile, setSelectedFile] = useState(null);
    const [capturedImage, setCapturedImage] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        if (mode === "camera") {
            enableCamera();
        } else {
            disableCamera();
        }
    
        // Cleanup to disable camera when component unmounts
        return () => {
            disableCamera();
        };
    }, [mode]);
    
    const enableCamera = async () => {
        try {
            if (cameraEnabled) return; // Prevent multiple activations
            setCameraEnabled(true);
    
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
    
                // Play video only when metadata is loaded
                videoRef.current.onloadedmetadata = () => {
                    videoRef.current.play().catch((err) => {
                        console.error("Video playback failed:", err);
                    });
                };
            }
        } catch (err) {
            console.error("Error enabling camera:", err);
        }
    };
    
    

    const disableCamera = () => {
        if (videoRef.current && videoRef.current.srcObject) {
            const tracks = videoRef.current.srcObject.getTracks();
            tracks.forEach((track) => track.stop()); // Stop all video tracks
            videoRef.current.srcObject = null; // Clear video source
        }
        setCameraEnabled(false);
    };
    

    const captureImage = () => {
        const canvas = canvasRef.current;
        const video = videoRef.current;
        if (canvas && video) {
            const ctx = canvas.getContext("2d");
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            const dataUrl = canvas.toDataURL("image/jpeg");
            setCapturedImage(dataUrl); // Store captured image
            return dataUrl;
        }
    };

    const handleAnalyze = async () => {
        let formData = new FormData();

        if (mode === "camera") {
            const imageData = captureImage();
            const blob = await fetch(imageData).then((res) => res.blob());
            formData.append("image", blob, "captured.jpg");
        } else if (mode === "upload" && selectedFile) {
            formData.append("image", selectedFile, selectedFile.name);
        } else {
            alert("Please capture an image or upload a file.");
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:5000/analyze", { method: "POST", body: formData });
            const data = await response.json();
            setResult(data.message);
            navigate("/details", { state: { image: capturedImage, result: data.message } });
        } catch (err) {
            console.error("Error:", err);
        }
    };

    let modeChangeTimeout;
    const handleModeChange = (newMode) => {
        clearTimeout(modeChangeTimeout);
        modeChangeTimeout = setTimeout(() => {
        setMode(newMode);
        }, 300); // Delay mode change by 300ms
    };


    useEffect(() => {
        if (mode === "camera") {
            enableCamera();
        } else {
            disableCamera();
        }

        // Cleanup to ensure camera is stopped when the component unmounts
        return () => {
            disableCamera();
        };
    }, [mode]);

    return (
        <div style={{ textAlign: "center", marginTop: "50px" }}>
            <h1>NutriLens</h1>

            <div style={{ margin: "20px 0" }}>
                <p>
                    <span style={{ marginRight: "10px", fontSize: "18px" }}>
                        {mode === "camera" ? "📷 Camera Mode" : "📂 Upload Mode"}
                    </span>
                </p>
                <input
    type="range"
    min="0"
    max="1"
    step="1"
    value={mode === "camera" ? "0" : "1"}
    onChange={(e) => setMode(e.target.value === "0" ? "camera" : "upload")}
    style={{
        width: "80px", // Shorter width
        height: "30px", // Thicker bar
        accentColor: "#4caf50", // Green color for the bar
        borderRadius: "15px", // Rounded bar
        appearance: "none", // Remove default styles
    }}
/>

            </div>

            {mode === "camera" && (
                <div>
                    <video
                        ref={videoRef}
                        style={{ width: "100%", maxWidth: "500px", border: "2px solid black" }}
                    ></video>
                    <canvas ref={canvasRef} style={{ display: "none" }} width="500" height="400"></canvas>
                </div>
            )}

            {mode === "upload" && (
                <div>
                    <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => setSelectedFile(e.target.files[0])}
                        style={{ marginTop: "20px" }}
                    />
                </div>
            )}

            <button onClick={handleAnalyze} style={{ marginTop: "20px" }}>Analyze</button>
        </div>
    );
}

export default Home;
