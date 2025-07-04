import axios from "axios";

// 🔐 Utility to extract user ID from browser cookies
const getUserIdFromCookie = () => {
  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith("user_id="));
  return match ? match.split("=")[1] : null;
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
    const userId = getUserIdFromCookie();
    if (!userId) throw new Error("Missing user ID");

    const formData = new FormData();
    formData.append("vibe_prompt", prompt);

    const response = await axios.post(
      `${BASE_URL}/groq-recommend-vibe?user_id=${userId}`,
      formData,
      {
        withCredentials: true,
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching recommendations:", error);
    return { error: "Failed to get recommendations" };
  }
};

// 🎧 Convert Groq-generated recommendation text into a Spotify playlist
export const createPlaylistFromGroq = async (recommendationText) => {
  try {
    const userId = getUserIdFromCookie();
    if (!userId) throw new Error("Missing user ID");

    const formData = new FormData();
    formData.append("recommendation_text", recommendationText);

    const response = await axios.post(
      `${BASE_URL}/groq-to-playlist?user_id=${userId}`,
      formData,
      {
        withCredentials: true,
      }
    );

    return response.data; // This should contain the playlist link
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
    const response = await axios.get(`${BASE_URL}/check_refresh_token`, {
      withCredentials: true,
    });
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
      {},
      { withCredentials: true }
    );
    return response.data;
  } catch (error) {
    console.error("Error refreshing access token:", error);
    return { error: "Failed to refresh access token" };
  }
};
