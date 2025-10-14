import axios from "axios";

// Ensure cookies are included in all requests by default
axios.defaults.withCredentials = true;

// 🔐 Utility to extract user ID from localStorage
const getUserId = () => {
  return localStorage.getItem("user_id");
};

// 🌐 Base URL of the backend API
export const BASE_URL = process.env.Backend_API_URL || "https://vibeai-backend-534228867297.us-west1.run.app" || "http://localhost:8000"; // Use environment variable with Cloud Run fallback
// export const BASE_URL = "https://vibeai-backend.onrender.com"; // Render backend (old)
// export const BASE_URL = "http://localhost:8000"; // Local development

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
export const recommendVibe = async (prompt, personalize = true) => {
  try {
    let payload;

    if (personalize) {
      const userId = getUserId();
      if (!userId) throw new Error("Missing user ID");
      payload = {
        user_id: userId,
        vibe_prompt: prompt
      };
    } else {
      payload = {
        vibe_prompt: prompt,
        personalize: false
      };
    }

    const response = await axios.post(`${BASE_URL}/groq-recommend-vibe`, payload);
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
export const createPlaylistFromGroq = async (recommendationText, personalize = true) => {
  try {
    let payload;

    if (personalize) {
      const userId = getUserId();
      if (!userId) throw new Error("Missing user ID");
      payload = {
        user_id: userId,
        groq_response: recommendationText
      };
    } else {
      payload = {
        groq_response: recommendationText,
        personalize: false
      };
    }

    const response = await axios.post(`${BASE_URL}/groq-to-playlist`, payload);
    console.log("✅ Playlist creation response:", response.data);
    if (response.data && response.data.playlist_url) {
      return response.data;
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
      `${BASE_URL}/refresh_token`,
      { user_id: userId }
    );
    return response.data;
  } catch (error) {
    console.error("Error refreshing access token:", error);
    return { error: "Failed to refresh access token" };
  }
};

// 🚪 Logout user by removing their tokens from the database
export const logoutUser = async () => {
  try {
    const userId = getUserId();
    if (!userId) {
      console.log("No user ID found in localStorage.");
      return { success: false, message: "No user ID found" };
    }
    
    const response = await axios.post(`${BASE_URL}/logout`, { user_id: userId });
    console.log("✅ Logout response:", response.data);
    
    // Clear user data from localStorage
    localStorage.removeItem("user_id");
    localStorage.removeItem("vibeai_access_key");
    
    return response.data;
  } catch (error) {
    console.error("Error during logout:", error);
    // Still clear localStorage even if backend call fails
    localStorage.removeItem("user_id");
    localStorage.removeItem("vibeai_access_key");
    return { success: false, error: "Failed to logout" };
  }
};

// 🔍 Check if a user is registered with Spotify (for auto-login)
export const checkUserRegistered = async (userId) => {
  try {
    if (!userId) {
      console.log("No user ID provided for registration check.");
      return { registered: false };
    }
    
    const response = await axios.get(`${BASE_URL}/check_user_registered?user_id=${userId}`);
    console.log("✅ User registration check response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error checking user registration:", error);
    return { registered: false };
  }
};

// 🎵 V2 Agentic Search API functions
export const agenticSearch = async (query, filters = {}, maxResults = 10) => {
  try {
    const response = await axios.post(`${BASE_URL}/v2/api/agentic-search`, {
      query,
      filters,
      max_results: maxResults
    });
    console.log("✅ Agentic search response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Agentic search failed:", error);
    return { error: "Failed to perform agentic search" };
  }
};

export const getDefaultPlaylists = async () => {
  try {
    const response = await axios.get(`${BASE_URL}/v2/api/playlists`);
    console.log("✅ Default playlists response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Failed to get playlists:", error);
    return { error: "Failed to get playlists" };
  }
};

export const getAvailableArtists = async () => {
  try {
    const response = await axios.get(`${BASE_URL}/v2/api/artists`);
    console.log("✅ Available artists response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Failed to get artists:", error);
    return { error: "Failed to get artists" };
  }
};

export const getAvailableLanguages = async () => {
  try {
    const response = await axios.get(`${BASE_URL}/v2/api/languages`);
    console.log("✅ Available languages response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Failed to get languages:", error);
    return { error: "Failed to get languages" };
  }
};
