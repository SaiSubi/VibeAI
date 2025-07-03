import React from 'react';
import { Box, Button, Image, Text, VStack } from '@chakra-ui/react';
import { useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Landing = () => {
  const navigate = useNavigate();

  useEffect(() => {
    console.log("🟡 Landing component mounted");

    const checkToken = async () => {
      console.log("🟠 Calling /check_refresh_token...");
      try {
        const response = await axios.get("http://localhost:8000/check_refresh_token", {
          withCredentials: true,
        });
        console.log("🟢 Response from /check_refresh_token:", JSON.stringify(response.data));

        if (response.data.valid) {
          console.log("✅ Valid refresh token found. Redirecting /home...");
          navigate("/home");
        } else {
          console.log("❌ Invalid or missing token. Staying on landing page.");
        }
      } catch (error) {
        console.error("🔴 Token check failed:", error);
        if (error.response) {
          console.error("🔴 Server responded with status:", error.response.status);
          console.error("🔴 Response data:", error.response.data);
        } else if (error.request) {
          console.error("🔴 No response received. Request:", error.request);
        } else {
          console.error("🔴 Error setting up request:", error.message);
        }
      }
    };

    checkToken();
  }, []);

  return (
    <Box
      minH="100vh"
      bg="black"
      color="white"
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="space-between"
      p={4}
    >
      <VStack spacing={4} mt={6}>
        <Image src="/logo.png" alt="VibeAI Logo" boxSize="100px" />
        <Text fontSize="lg" textAlign="center">
          Create custom music playlists that match your mood!
        </Text>
        <Button
          bg="#1DB954"
          color="white"
          size="lg"
          _hover={{ bg: "#1ed760" }}
          onClick={() => {
            window.location.href = "http://localhost:8000/login";
          }}
        >
          LOGIN WITH SPOTIFY
        </Button>
        <Box w="full" h="300px" bg="gray.300" display="flex" alignItems="center" justifyContent="center">
          <Text color="black">DEMO VIDEO</Text>
        </Box>
        <Text fontSize="md" textAlign="center">
          Let your imagination &amp; love for music run wild!
        </Text>
        <Button
          bg="#1DB954"
          color="white"
          size="md"
          _hover={{ bg: "#1ed760" }}
          onClick={() => {
            window.location.href = "http://localhost:8000/login";
          }}
        >
          Try it Yourself
        </Button>
      </VStack>

      <Text fontSize="sm" mt={8} mb={2}>
        Made by Sai Subramanian. Hope you Enjoy:)
      </Text>
    </Box>
  );
};

export default Landing;