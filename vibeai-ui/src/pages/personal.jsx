import React, { useState } from 'react';
import {
  Box,
  Button,
  Input,
  Text,
  VStack,
  Image,
  HStack
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';

const Personal = () => {
  const [accessKey, setAccessKey] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handlePersonalizedAccess = () => {
    const validKey = "vibeaiforyou"; // Replace with your actual secret

    if (accessKey === validKey) {
      localStorage.setItem("vibeai_access_key", accessKey); // optional
      navigate("/landing");
    } else {
      setError("❌ Invalid access key. Please try again.");
    }
  };

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