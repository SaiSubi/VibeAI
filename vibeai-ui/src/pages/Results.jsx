import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { createPlaylistFromGroq, logoutUser, BASE_URL } from '../api'; 

function Results() {
  const [isPlaylistCreated, setIsPlaylistCreated] = useState(false);
  const [playlistUrl, setPlaylistUrl] = useState('');
  const [isCreatingPlaylist, setIsCreatingPlaylist] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
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
          <button 
            onClick={async () => {
              setIsCreatingPlaylist(true);
              try {
                console.log("Creating playlist with recommendation:", recommendation);
                const response = await createPlaylistFromGroq(recommendation);
                console.log("Received response from createPlaylistFromGroq:", response);
                console.log("✅ Playlist successfully created. URL:", response.playlist_url);
                setPlaylistUrl(response.playlist_url);
                setIsPlaylistCreated(true);
              } catch (error) {
                console.error("Error creating playlist:", error);
              } finally {
                setIsCreatingPlaylist(false);
              }
            }} 
            disabled={isCreatingPlaylist}
            style={{
              backgroundColor: isCreatingPlaylist ? '#888' : '#2ecc71',
              color: 'white',
              fontSize: '20px',
              padding: '10px 30px',
              margin: '10px 0',
              border: 'none',
              borderRadius: '4px',
              cursor: isCreatingPlaylist ? 'not-allowed' : 'pointer',
              opacity: isCreatingPlaylist ? 0.6 : 1
            }}
          >
            {isCreatingPlaylist ? 'Creating Playlist...' : 'Create Playlist'}
          </button>
          
          {isCreatingPlaylist && (
            <div style={{ textAlign: 'center', marginTop: '10px', marginBottom: '20px' }}>
              <h3 style={{ marginBottom: '10px' }}>Creating your playlist...</h3>
              <img
                src="/loading.gif"
                alt="Loading"
                style={{
                  width: '100px',
                  height: '100px',
                  display: 'block',
                  margin: '0 auto'
                }}
              />
            </div>
          )}
          
          <p style={{ textAlign: 'center', maxWidth: '80%', margin: '20px 0' }}>
            Your Playlist is Waiting to be Created!
          </p>
        </>
      )}

      <button onClick={() => navigate('/home')} style={{ 
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

      <button onClick={handleLogout} disabled={isLoggingOut} style={{ 
        backgroundColor: isLoggingOut ? '#888' : 'white', 
        color: isLoggingOut ? 'white' : 'black', 
        fontSize: '14px', 
        padding: '5px 15px', 
        marginBottom: '10px',
        border: 'none',
        borderRadius: '4px',
        cursor: isLoggingOut ? 'not-allowed' : 'pointer',
        opacity: isLoggingOut ? 0.6 : 1
      }}>
        {isLoggingOut ? 'Logging Out...' : 'Logout'}
      </button>

      <footer style={{ fontSize: '12px', marginTop: 'auto' }}>
        Made by Sai Subramanian. Hope you Enjoy:)
      </footer>
    </div>
  );
}

export default Results;
