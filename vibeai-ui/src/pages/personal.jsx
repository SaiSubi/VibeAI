import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Input,
  Text,
  VStack,
  Image,
  HStack,
  Spinner
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { checkUserRegistered } from '../api';

const Personal = () => {
  const [accessKey, setAccessKey] = useState('');
  const [error, setError] = useState('');
  const [isCheckingUser, setIsCheckingUser] = useState(true);
  const [showModeChoice, setShowModeChoice] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    checkExistingUser();
  }, []);

  const checkExistingUser = async () => {
    try {
      const userId = localStorage.getItem("user_id");
      if (userId) {
        console.log("🔍 Checking if user is registered:", userId);
        const response = await checkUserRegistered(userId);
        
        if (response.registered) {
          console.log("✅ User is registered, redirecting to personalized home");
          navigate("/home");
          return;
        } else {
          console.log("❌ User not registered or tokens expired");
          // Clear invalid user_id
          localStorage.removeItem("user_id");
        }
      }
    } catch (error) {
      console.error("Error checking existing user:", error);
    } finally {
      setIsCheckingUser(false);
      setShowModeChoice(true);
    }
  };

  const handlePersonalizedAccess = () => {
    const validKey = "vibeaiforyou"; // Replace with your actual secret

    if (accessKey === validKey) {
      localStorage.setItem("vibeai_access_key", accessKey); // optional
      navigate("/landing");
    } else {
      setError("❌ Invalid access key. Please try again.");
    }
  };

  // Show loading screen while checking user
  if (isCheckingUser) {
    return (
      <Box
        minH="100vh"
        bg="black"
        color="white"
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        px={4}
      >
        <VStack spacing={6} textAlign="center">
          <Image src="/logo.png" alt="VibeAI Logo" boxSize="100px" />
          <Text fontSize="xl" fontWeight="bold">
            Welcome back to VibeAI
          </Text>
          <Text fontSize="md" color="gray.300">
            Checking your login status...
          </Text>
          <Spinner size="xl" color="green.400" />
          <Text fontSize="sm" color="gray.400">
            Please wait while we verify your account
          </Text>
        </VStack>
      </Box>
    );
  }

  // Show mode choice after checking user
  if (!showModeChoice) {
    return null;
  }

  return (
    <Box
      minH="100vh"
      bg="black"
      color="white"
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      px={4}
    >
      <VStack spacing={6} textAlign="center">
        <Image src="/logo.png" alt="VibeAI Logo" boxSize="100px" />
        <Text fontSize="2xl" fontWeight="bold">
          Welcome to VibeAI
        </Text>
        <Text fontSize="md" color="gray.300" maxW="md">
          Instantly generate playlists that match your mood. Choose a path:
        </Text>

        {/* Not Personalized Button */}
        <Button
          size="lg"
          colorScheme="green"
          width="250px"
          onClick={() => navigate("/homegen")}
        >
          General Mode🎵
        </Button>

        {/* Personalized Section */}
        <VStack spacing={2}>
          <HStack>
            <Input
              type="password"
              placeholder="Enter access key"
              value={accessKey}
              onChange={(e) => setAccessKey(e.target.value)}
              bg="white"
              color="black"
              width="200px"
            />
            <Button
              size="md"
              colorScheme="green"
              onClick={handlePersonalizedAccess}
            >
              Personalized Mode 🔐
            </Button>
          </HStack>
          {error && <Text color="red.300" fontSize="sm">{error}</Text>}
          <Text fontSize="sm" color="gray.400" maxW="sm" textAlign="center">
            Based on Spotify&apos;s updated terms, I need to manually add you as a user (25 user limit) before I can provide anything personalised.
            Send an email to <strong>vibeai16@gmail.com</strong> with your name and email ID linked to Spotify and I will add you as a user and share the access key.
          </Text>
        </VStack>
      </VStack>

      <Text fontSize="sm" mt={12}>
        Made by Sai Subramanian. Hope you enjoy :)
      </Text>
    </Box>
  );
};

export default Personal;