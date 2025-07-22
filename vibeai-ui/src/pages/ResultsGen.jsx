import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { createPlaylistFromGroq, BASE_URL } from '../api'; 

function ResultsGen() {
  const [isPlaylistCreated, setIsPlaylistCreated] = useState(false);
  const [playlistUrl, setPlaylistUrl] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  console.log("useLocation() in Results:", location);
  const [recommendation, setRecommendation] = useState('');

  useEffect(() => {
    console.log("Location state in Results:", location.state);
    if (location.state?.text) {
      setRecommendation(location.state.text);
    } else {
      console.warn("⚠️ No recommendation text found in location state.");
    }
  }, [location.state]);

  return (
    <div style={{ 
      backgroundColor: '#1a1a1a', 
      color: 'white', 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      padding: '20px', 
      minHeight: '100vh' 
    }}>
      <img src="/logo.png" alt="VibeAI Logo" style={{ width: '150px', marginBottom: '10px' }} />
      <h2>Your Recommendations are Ready!</h2>
      
      <textarea
        value={recommendation}
        readOnly
        style={{
          width: '90%',
          maxWidth: '500px',
          height: '200px',
          backgroundColor: '#d3d3d3',
          color: 'black',
          padding: '10px',
          margin: '20px 0',
          fontSize: '16px',
          resize: 'none',
          border: 'none',
          borderRadius: '4px'
        }}
      />

      {isPlaylistCreated ? (
        <>
          <h3>Playlist Created</h3>
          {playlistUrl && (
            <a href={playlistUrl} target="_blank" rel="noopener noreferrer">
              <button style={{ 
                backgroundColor: '#2ecc71', 
                color: 'white', 
                fontSize: '20px', 
                padding: '10px 30px', 
                margin: '10px 0',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}>
                Play on Spotify
              </button>
            </a>
          )}
          <p style={{ textAlign: 'center', maxWidth: '80%', margin: '20px 0' }}>
            Your Playlist is Ready!!!
          </p>
        </>
      ) : (
        <>
          <button onClick={async () => {
            try {
              console.log("Creating playlist with recommendation:", recommendation);
              const response = await createPlaylistFromGroq(recommendation, false);
              console.log("Received response from createPlaylistFromGroq:", response);
              console.log("✅ Playlist successfully created. URL:", response.playlist_url);
              setPlaylistUrl(response.playlist_url);
              setIsPlaylistCreated(true);
            } catch (error) {
              console.error("Error creating playlist:", error);
            }
          }} style={{
            backgroundColor: '#2ecc71',
            color: 'white',
            fontSize: '20px',
            padding: '10px 30px',
            margin: '10px 0',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}>
            Create Playlist
          </button>
          <p style={{ textAlign: 'center', maxWidth: '80%', margin: '20px 0' }}>
            Your Playlist is Waiting to be Created!
          </p>
        </>
      )}

      <button onClick={() => navigate('/homegen')} style={{ 
        backgroundColor: '#27ae60', 
        color: 'white', 
        fontSize: '20px', 
        padding: '10px 30px', 
        marginBottom: '20px',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer'
      }}>
        New Vibe
      </button>

      <button onClick={() => navigate('/')} style={{ 
        backgroundColor: 'white', 
        color: 'black', 
        fontSize: '14px', 
        padding: '5px 15px', 
        marginBottom: '10px',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer'
      }}>
        Logout
      </button>

      <footer style={{ fontSize: '12px', marginTop: 'auto' }}>
        Made by Sai Subramanian. Hope you Enjoy:)
      </footer>
    </div>
  );
}

export default ResultsGen;
