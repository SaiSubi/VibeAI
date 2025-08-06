import React, { useState } from "react";
import { useEffect } from "react";
import { recommendVibe, logoutUser } from "../api";
import { useNavigate } from "react-router-dom";

function Home() {
  const [userPrompt, setUserPrompt] = useState("");
  const [myMusic, setMyMusic] = useState(true);
  const [newMusic, setNewMusic] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [recommendedText, setRecommendedText] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const userIdFromURL = urlParams.get("user_id");
    if (userIdFromURL) {
      localStorage.setItem("user_id", userIdFromURL);
      console.log("✅ Stored user_id in localStorage:", userIdFromURL);
    }
  }, []);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logoutUser();
      navigate('/');
    } catch (error) {
      console.error("Error during logout:", error);
      navigate('/');
    } finally {
      setIsLoggingOut(false);
    }
  };

  return (
    <div style={{
      backgroundColor: "#121212",
      color: "white",
      fontFamily: "sans-serif",
      minHeight: "100vh",
      padding: "20px",
      textAlign: "center",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "flex-start"
    }}>
      <style>
        {`
        .switch {
          position: relative;
          display: inline-block;
          width: 40px;
          height: 22px;
        }

        .switch input {
          opacity: 0;
          width: 0;
          height: 0;
        }

        .slider {
          position: absolute;
          cursor: pointer;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: #ccc;
          transition: 0.4s;
          border-radius: 22px;
        }

        .slider:before {
          position: absolute;
          content: "";
          height: 16px;
          width: 16px;
          left: 3px;
          bottom: 3px;
          background-color: white;
          transition: 0.4s;
          border-radius: 50%;
        }

        input:checked + .slider {
          background-color: #1DB954;
        }

        input:checked + .slider:before {
          transform: translateX(18px);
        }
        `}
      </style>
      
      <img src="/logo.png" alt="VibeAI Logo" style={{ width: "150px", marginBottom: "20px", marginTop: "20px" }} />
      <h1 style={{ marginBottom: "20px", fontSize: "2rem" }}>Welcome to VibeAI</h1>
      <p style={{ marginBottom: "30px", fontSize: "18px", maxWidth: "600px" }}>
        Tell me your mood and I'll create a playlist for you! 🎵
      </p>

      <div style={{ marginBottom: "20px", width: "100%", maxWidth: "500px" }}>
        <textarea
          value={userPrompt}
          onChange={(e) => setUserPrompt(e.target.value)}
          placeholder="Describe your mood or what you want to listen to..."
          style={{
            width: "100%",
            height: "100px",
            padding: "15px",
            fontSize: "16px",
            borderRadius: "8px",
            border: "2px solid #ccc",
            resize: "none",
            backgroundColor: "white",
            color: "black",
            fontFamily: "inherit"
          }}
        />
      </div>

      <button
        onClick={() => setUserPrompt("")}
        disabled={isLoading}
        style={{
          backgroundColor: "#888",
          color: "white",
          border: "none",
          padding: "8px 16px",
          borderRadius: "10px",
          marginTop: "10px",
          fontSize: "14px",
          cursor: isLoading ? "not-allowed" : "pointer",
          opacity: isLoading ? 0.6 : 1
        }}
      >
        Clear Text
      </button>

      <button
        onClick={async () => {
          setIsLoading(true);
          try {
            const response = await recommendVibe(userPrompt);
            setRecommendedText(response.groq_recommendations);
            navigate("/results", { state: { text: response.groq_recommendations } });
          } catch (err) {
            console.error("Recommendation failed:", err);
          } finally {
            setIsLoading(false);
          }
        }}
        disabled={!userPrompt.trim() || isLoading}
        style={{
          backgroundColor: isLoading ? "#888" : "#1DB954",
          color: "white",
          border: "none",
          padding: "15px 30px",
          fontSize: "18px",
          fontWeight: "bold",
          borderRadius: "8px",
          marginTop: "20px",
          marginBottom: "20px",
          cursor: isLoading ? "not-allowed" : "pointer",
          width: "100%",
          maxWidth: "300px"
        }}
      >
        Recommend Songs
      </button>

      {isLoading && (
        <div style={{ textAlign: "center", marginTop: "20px", marginBottom: "30px" }}>
          <h3 style={{ marginBottom: "10px" }}>Loading..........</h3>
          <img
            src="/loading.gif"
            alt="Loading"
            style={{
              width: "100px",
              height: "100px",
              display: "block",
              margin: "0 auto"
            }}
          />
        </div>
      )}

      <h3 style={{ marginTop: "30px", marginBottom: "15px" }}>Get Inspired & Play with</h3>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "10px", marginTop: "10px", width: "100%", maxWidth: "500px" }}>
        <div
          onClick={() => setUserPrompt("I just met someone new! Can you play Arijit Singh's and Shreya Ghosal's falling in love songs?")}
          style={{
            backgroundColor: "#eee",
            color: "#000",
            padding: "15px",
            borderRadius: "10px",
            width: "100%",
            margin: "0 auto",
            wordWrap: "break-word",
            whiteSpace: "normal",
            cursor: "pointer",
            fontSize: "14px"
          }}
        >
          I just met someone new! Can you play Arijit Singh's and Shreya Ghosal's falling in love songs?
        </div>
        <div
          onClick={() => setUserPrompt("I have a tough exam coming up, I need motivation, I feel Battle Symphony, Unstoppable, give me more?")}
          style={{
            backgroundColor: "#eee",
            color: "#000",
            padding: "15px",
            borderRadius: "10px",
            width: "100%",
            margin: "0 auto",
            wordWrap: "break-word",
            whiteSpace: "normal",
            cursor: "pointer",
            fontSize: "14px"
          }}
        >
          I have a tough exam coming up, I need motivation, I feel Battle Symphony, Unstoppable, give me more?
        </div>
        <div
          onClick={() => setUserPrompt("I have my school friends over and we used to play a lot of fifa, can you play some of the best fifa songs?")}
          style={{
            backgroundColor: "#eee",
            color: "#000",
            padding: "15px",
            borderRadius: "10px",
            width: "100%",
            margin: "0 auto",
            wordWrap: "break-word",
            whiteSpace: "normal",
            cursor: "pointer",
            fontSize: "14px"
          }}
        >
          I have my school friends over and we used to play a lot of fifa, can you play some of the best fifa songs?
        </div>
        <div
          onClick={() => setUserPrompt("I love slow melodious Indian songs like SPB's and Arijit's, can you give me something similar in english?")}
          style={{
            backgroundColor: "#eee",
            color: "#000",
            padding: "15px",
            borderRadius: "10px",
            width: "100%",
            margin: "0 auto",
            wordWrap: "break-word",
            whiteSpace: "normal",
            cursor: "pointer",
            fontSize: "14px"
          }}
        >
          I love slow melodious Indian songs like SPB's and Arijit's, can you give me something similar in english?
        </div>
      </div>

      <button
        onClick={handleLogout}
        disabled={isLoading || isLoggingOut}
        style={{
          marginTop: "30px",
          padding: "8px 20px",
          borderRadius: "6px",
          backgroundColor: isLoggingOut ? "#888" : "white",
          color: isLoggingOut ? "white" : "#000",
          border: "1px solid #ccc",
          opacity: (isLoading || isLoggingOut) ? 0.6 : 1,
          cursor: (isLoading || isLoggingOut) ? "not-allowed" : "pointer",
          fontSize: "14px"
        }}
      >
        {isLoggingOut ? "Logging Out..." : "Logout"}
      </button>

      <footer style={{ marginTop: "30px", fontSize: "12px", color: "#ccc" }}>
        Made by Sai Subramanian. Hope you Enjoy:)
      </footer>
    </div>
  );
}

export default Home;