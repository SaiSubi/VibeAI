import axios from "axios";

// Ensure cookies are included in all requests by default
axios.defaults.withCredentials = true;

// 🔐 Utility to extract user ID from localStorage
const getUserId = () => {
  return localStorage.getItem("user_id");
};

// 🌐 Base URL of the backend API
export const BASE_URL = "https://vibeai-backend.onrender.com"; // Updated to live backend

// ✅ Check if the backend is live and responsive
export const getHealth = async () => {
  try {
    const response = await axios.get(`${BASE_URL}/`);
    return response.data;
  } catch (error) {
    console.error("Backend connection failed:", error);
    return { message: "Error connecting to backend" };
  }
};

// 🎵 Send a mood prompt to Groq to get a music recommendation message
export const recommendVibe = async (prompt) => {
  try {
    const userId = getUserId();
    if (!userId) throw new Error("Missing user ID");

    const response = await axios.post(
      `${BASE_URL}/groq-recommend-vibe`,
      {
        user_id: userId,
        vibe_prompt: prompt
      }
    );
    console.log("✅ Groq recommendation response:", response.data);
    if (response.data) {
      return response.data;
    } else {
      return { error: "No recommendation data received" };
    }
  } catch (error) {
    console.error("Error fetching recommendations:", error);
    return { error: "Failed to get recommendations" };
  }
};

// 🎧 Convert Groq-generated recommendation text into a Spotify playlist
export const createPlaylistFromGroq = async (recommendationText) => {
  try {
    const userId = getUserId();
    if (!userId) throw new Error("Missing user ID");

    const response = await axios.post(
      `${BASE_URL}/groq-to-playlist`,
      {
        user_id: userId,
        groq_response: recommendationText
      }
    );
    console.log("✅ Playlist creation response:", response.data);
    if (response.data && response.data.playlist_url) {
      return response.data; // This should contain the playlist link
    } else {
      return { error: "No playlist URL received" };
    }
  } catch (error) {
    console.error("Error creating playlist:", error);
    return { error: "Failed to create playlist" };
  }
};

// 🧼 Temporary backward-compatible export alias
export { createPlaylistFromGroq as createPlaylistFromGROQ };

// 🔄 Check if the user's refresh token is valid
export const checkRefreshToken = async () => {
  try {
    const userId = localStorage.getItem("user_id");
    if (!userId) {
      console.log("No user ID found in localStorage.");
      return { valid: false };
    }
    const response = await axios.get(
      `${BASE_URL}/check_refresh_token?user_id=${userId}`
    );
    console.log("✅ Refresh token check response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error checking refresh token:", error);
    return { valid: false };
  }
};

// ♻️ Manually refresh the user's Spotify access token using their user ID
export const refreshAccessToken = async (userId) => {
  try {
    const response = await axios.post(
      `${BASE_URL}/refresh_token?user_id=${userId}`,
      {}
    );
    return response.data;
  } catch (error) {
    console.error("Error refreshing access token:", error);
    return { error: "Failed to refresh access token" };
  }
};
