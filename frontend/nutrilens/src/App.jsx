import React, { useState } from "react";

function App() {
    const [image, setImage] = useState(null);
    const [result, setResult] = useState("");

    const handleUpload = (e) => {
        setImage(e.target.files[0]);
    };

    const handleAnalyze = async () => {
        const formData = new FormData();
        formData.append("image", image);

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

    return (
        <div style={{ textAlign: "center", marginTop: "50px" }}>
            <h1>Food Analyzer</h1>
            <input type="file" accept="image/*" onChange={handleUpload} />
            <button onClick={handleAnalyze}>Analyze</button>
            {result && <p>Result: {result}</p>}
        </div>
    );
}

export default App;