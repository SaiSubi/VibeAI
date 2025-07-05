import React, { useState } from "react";
import { useEffect } from "react";
import { recommendVibe } from "../api";
import { useNavigate } from "react-router-dom";

function Home() {
  const [userPrompt, setUserPrompt] = useState("");
  const [myMusic, setMyMusic] = useState(true);
  const [newMusic, setNewMusic] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
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

  /*
  const toggleMyMusic = () => {
    if (!myMusic) {
      setMyMusic(true);
      setNewMusic(false);
    } else {
      setMyMusic(false);
    }
  };

  const toggleNewMusic = () => {
    if (!newMusic) {
      setNewMusic(true);
      setMyMusic(false);
    } else {
      setNewMusic(false);
    }
  };
  */

  return (
    <>
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
      <div style={{
        backgroundColor: "#121212",
        color: "white",
        fontFamily: "sans-serif",
        minHeight: "100vh",
        padding: "20px",
        textAlign: "center"
      }}>
        <img src="/logo.png" alt="VibeAI Logo" style={{ width: "100px", margin: "0 auto" }} />
        <h2>Welcome User! Ready to Vibe?</h2>

        <div style={{ display: "flex", justifyContent: "center", gap: "10px", margin: "20px 0" }}>
          <textarea
            placeholder="Tell me your vibe here"
            value={userPrompt}
            onChange={(e) => setUserPrompt(e.target.value)}
            disabled={isLoading}
            style={{
              width: "300px",
              height: "200px",
              backgroundColor: "#ddd",
              color: "black",
              border: "none",
              padding: "10px",
              resize: "none"
            }}
          />
          {/*
          <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", gap: "10px", alignItems: "flex-start" }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", color: "white" }}>
              <span>My Music</span>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={myMusic}
                  onChange={() => {
                    if (!myMusic) {
                      setMyMusic(true);
                      setNewMusic(false);
                    } else {
                      setMyMusic(false);
                    }
                  }}
                  disabled={isLoading}
                />
                <span className="slider round"></span>
              </label>
            </div>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", color: "white" }}>
              <span>New Music</span>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={newMusic}
                  onChange={() => {
                    if (!newMusic) {
                      setNewMusic(true);
                      setMyMusic(false);
                    } else {
                      setNewMusic(false);
                    }
                  }}
                  disabled={isLoading}
                />
                <span className="slider round"></span>
              </label>
            </div>
          */}
            <button
              onClick={() => setUserPrompt("")}
              disabled={isLoading}
              style={{
                backgroundColor: "#888",
                color: "white",
                border: "none",
                padding: "6px 12px",
                borderRadius: "10px",
                marginTop: "10px",
                fontSize: "12px",
                cursor: isLoading ? "not-allowed" : "pointer",
                opacity: isLoading ? 0.6 : 1
              }}
            >
              Clear Text
            </button>
          {/* 
          </div>
          */}
        </div>

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
          padding: "10px 30px",
          fontSize: "18px",
          fontWeight: "bold",
          borderRadius: "5px",
          marginBottom: "20px",
          cursor: isLoading ? "not-allowed" : "pointer"
        }}
      >
        Recommend Songs
      </button>

      {isLoading && (
        <div style={{ textAlign: "center", marginTop: "10px", marginBottom: "30px" }}>
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

      <h3>Get Inspired & Play with</h3>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "10px", marginTop: "10px" }}>
        <div
          onClick={() => setUserPrompt("I just met someone new! Can you play Arijit Singh’s and Shreya Ghosal’s falling in love songs?")}
          style={{
            backgroundColor: "#eee",
            color: "#000",
            padding: "10px",
            borderRadius: "10px",
            width: "100%",
            maxWidth: "500px",
            margin: "0 auto",
            wordWrap: "break-word",
            whiteSpace: "normal",
            cursor: "pointer"
          }}
        >
          I just met someone new! Can you play Arijit Singh’s and Shreya Ghosal’s falling in love songs?
        </div>
        <div
          onClick={() => setUserPrompt("I have a tough exam coming up, I need motivation, I feel Battle Symphony, Unstoppable, give me more?")}
          style={{
            backgroundColor: "#eee",
            color: "#000",
            padding: "10px",
            borderRadius: "10px",
            width: "100%",
            maxWidth: "500px",
            margin: "0 auto",
            wordWrap: "break-word",
            whiteSpace: "normal",
            cursor: "pointer"
          }}
        >
          I have a tough exam coming up, I need motivation, I feel Battle Symphony, Unstoppable, give me more?
        </div>
        <div
          onClick={() => setUserPrompt("I have my school friends over and we used to play a lot of fifa, can you play some of the best fifa songs?")}
          style={{
            backgroundColor: "#eee",
            color: "#000",
            padding: "10px",
            borderRadius: "10px",
            width: "100%",
            maxWidth: "500px",
            margin: "0 auto",
            wordWrap: "break-word",
            whiteSpace: "normal",
            cursor: "pointer"
          }}
        >
          I have my school friends over and we used to play a lot of fifa, can you play some of the best fifa songs?
        </div>
        <div
          onClick={() => setUserPrompt("I love slow melodious Indian songs like SPB’s and Arijit’s, can you give me something similar in english?")}
          style={{
            backgroundColor: "#eee",
            color: "#000",
            padding: "10px",
            borderRadius: "10px",
            width: "100%",
            maxWidth: "500px",
            margin: "0 auto",
            wordWrap: "break-word",
            whiteSpace: "normal",
            cursor: "pointer"
          }}
        >
          I love slow melodious Indian songs like SPB’s and Arijit’s, can you give me something similar in english?
        </div>
      </div>

      <button
        onClick={() => navigate("/")}
        disabled={isLoading}
        style={{
          marginTop: "20px",
          padding: "6px 16px",
          borderRadius: "4px",
          backgroundColor: "white",
          color: "#000",
          border: "1px solid #ccc",
          opacity: isLoading ? 0.6 : 1,
          cursor: isLoading ? "not-allowed" : "pointer"
        }}
      >
        Logout
      </button>

      <footer style={{ marginTop: "30px", fontSize: "12px", color: "#ccc" }}>
        Made by Sai Subramanian. Hope you Enjoy:)
      </footer>
      </div>
    </>
  );
}

export default Home;