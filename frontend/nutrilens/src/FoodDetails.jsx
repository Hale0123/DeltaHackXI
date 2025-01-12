import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

function FoodDetails() {
    const location = useLocation();
    const navigate = useNavigate();
    const { image, result } = location.state || {};

    return (
        <div style={{ textAlign: "center", marginTop: "50px" }}>
            <h1>Food Details</h1>
            {image && <img src={image} alt="Food" style={{ width: "300px", marginBottom: "20px" }} />}
            {result && <p>{result}</p>}
            <button onClick={() => navigate("/")}>Back to Home</button>
        </div>
    );
}

export default FoodDetails;
