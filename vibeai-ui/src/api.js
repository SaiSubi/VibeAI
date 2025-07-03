import axios from "axios";

const getUserIdFromCookie = () => {
  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith("user_id="));
  return match ? match.split("=")[1] : null;
};

export const BASE_URL = "https://vibeai-backend.onrender.com"; // Updated to live backend

export const getHealth = async () => {
  try {
    const response = await axios.get(`${BASE_URL}/`);
    return response.data;
  } catch (error) {
    console.error("Backend connection failed:", error);
    return { message: "Error connecting to backend" };
  }
};

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

export { createPlaylistFromGroq as createPlaylistFromGROQ };