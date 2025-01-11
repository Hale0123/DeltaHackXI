import React, { useRef, useState, useEffect } from "react";

function App() {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [result, setResult] = useState("");
    const [cameraEnabled, setCameraEnabled] = useState(false);
    const [mode, setMode] = useState("camera"); // Default to "camera" mode
    const [selectedFile, setSelectedFile] = useState(null);

    // Start the camera
    const enableCamera = async () => {
        try {
            setCameraEnabled(true);
            const stream = await navigator.mediaDevices.getUserMedia({
                video: true,
            });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                videoRef.current.play();
            }
        } catch (err) {
            console.error("Error enabling camera:", err);
        }
    };

    // Stop the camera
    const disableCamera = () => {
        if (videoRef.current && videoRef.current.srcObject) {
            const tracks = videoRef.current.srcObject.getTracks();
            tracks.forEach((track) => track.stop());
            setCameraEnabled(false);
        }
    };

    // Capture a frame from the video feed
    const captureImage = () => {
        const canvas = canvasRef.current;
        const video = videoRef.current;

        if (canvas && video) {
            const ctx = canvas.getContext("2d");
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            // Convert canvas to a data URL (image format)
            return canvas.toDataURL("image/jpeg");
        }
    };

    // Handle File Upload
    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
    };

    // Handle Analyze Button Click
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
            const response = await fetch("http://127.0.0.1:5000/analyze", {
                method: "POST",
                body: formData,
            });
            const data = await response.json();
            setResult(data.message);
        } catch (err) {
            console.error("Error:", err);
        }
    };

    // Handle Slider Change
    const handleSliderChange = (event) => {
        const newMode = event.target.value === "0" ? "camera" : "upload";

        if (newMode === "upload") {
            disableCamera();
        }

        if (newMode === "camera") {
            enableCamera();
        }

        setMode(newMode);
    };

    // Enable the camera automatically on first load if "camera" mode is active
    useEffect(() => {
        if (mode === "camera" && !cameraEnabled) {
            enableCamera();
        }
        // Cleanup on unmount
        return () => {
            disableCamera();
        };
    }, [mode]);

    return (
        <div style={{ textAlign: "center", marginTop: "50px" }}>
            <h1>NutriLens</h1>

            {/* Sliding Toggle */}
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
                    onChange={handleSliderChange}
                    style={{
                        width: "150px", // Shortened length
                        height: "20px", // Increased size
                        margin: "10px auto",
                        display: "block",
                        accentColor: "#4caf50",
                    }}
                />
            </div>

            {/* Camera Mode */}
            {mode === "camera" && (
                <div>
                    <div style={{ position: "relative", marginTop: "20px" }}>
                        <video
                            ref={videoRef}
                            style={{
                                width: "100%",
                                maxWidth: "500px",
                                border: "2px solid black",
                            }}
                        ></video>
                        <canvas
                            ref={canvasRef}
                            style={{ display: "none" }}
                            width="500"
                            height="400"
                        ></canvas>
                    </div>
                </div>
            )}

            {/* Upload Mode */}
            {mode === "upload" && (
                <div>
                    <input
                        type="file"
                        accept="image/*"
                        onChange={handleFileChange}
                        style={{ marginTop: "20px" }}
                    />
                </div>
            )}

            {/* Analyze Button */}
            <button onClick={handleAnalyze} style={{ marginTop: "20px" }}>
                Analyze
            </button>

            {/* Result */}
            {result && <p>Result: {result}</p>}
        </div>
    );
}

export default App;
