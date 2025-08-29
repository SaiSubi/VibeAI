#!/usr/bin/env python3

import google.generativeai as genai
import sys
import os
import json
from datetime import datetime

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Gemini_API_KEY

def test_gemini_pro():
    """Test Gemini Pro 2.5 (without search)"""
    print("=" * 60)
    print("TESTING GEMINI PRO 2.5 (without search)")
    print("=" * 60)
    
    # Configure the API
    genai.configure(api_key=Gemini_API_KEY)
    
    # Create model
    model = genai.GenerativeModel('gemini-2.5-pro')
    
    # Test prompt
    prompt = """
    Analyze this song for me:
    
    Title: "Ailasa Ailasa"
    Artist: "Yuvan Shankar Raja"
    
    Please provide:

1. **Energy Level**: Score from 0-10 (0=very low energy, 10=very high energy)
2. **Emotion Vector**: Provide a numerical vector [Happy, Sad, Angry] where each value is 0-10 (10 being strongest). Example: [8, 2, 1] means very happy, slightly sad, barely angry.
3. **Language**: Primary language of the song (English, Tamil, Hindi, Telugu, Malayalam, Kannada, Punjabi, etc.)
   For songs with multiple languages, use the primary language. Examples: 'My Universe' by Coldplay & BTS → 'English'
4. **Genre**: Primary musical genre (Pop, Rock, Hip-Hop, R&B, Electronic, Country, Jazz, Classical, Folk, Indie, Bollywood, Tamil Film, etc.)
5. **Lyrical Themes**: Select ONLY 1-5 most relevant themes from these 27 options (be selective and critical):
   - Hopeful Love, In Love, Lust, Toxic Relationship, Flirty, Longing, Breakup
   - Friendship, Family, Feel Good, Celebrating Life, Carefree, Escape from Life
   - Unhappy with life, Dreaming, Motivational, Reassuring, Confident
   - Insecure, Love Myself, Hate Myself, Reflection/Introspection, Nostalgia
   - Adventure, Home, Solitude, Spirituality
6. **Danceability Score**: Rate how easy it is to dance to this song (0-10, where 10=very danceable, 0=not danceable at all)
7. **Theme Scores**: For each selected theme, rate how strongly it applies (1-10, where 10=perfect match). Be critical and realistic - don't inflate scores. A 10 should be reserved for themes that are absolutely central to the song.
8. **Popularity Score**: Rate this song's popularity from 1-10 (1=obscure/unknown, 10=global hit/very famous)
    
    IMPORTANT: Think and provide the best possible answer.
    
    Return your response as valid JSON.
    """
    
    try:
        response = model.generate_content(prompt)
        print("✅ Gemini Pro 2.5 Response:")
        print(response.text)
        print("\n" + "-" * 60)
        
        # Try to parse as JSON - handle markdown formatting
        try:
            # Extract JSON from markdown if present
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]  # Remove ```json
            if text.endswith('```'):
                text = text[:-3]  # Remove ```
            
            json_response = json.loads(text.strip())
            print("✅ JSON parsed successfully!")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw text: {text}")
            return False
            
    except Exception as e:
        print(f"❌ Gemini Pro 2.5 Error: {e}")
        return False

def test_gemini_flash_with_search():
    """Test Gemini Flash 2.5 with search capabilities"""
    print("=" * 60)
    print("TESTING GEMINI FLASH 2.5 (with search)")
    print("=" * 60)
    
    # Configure the API
    generation_config = genai.types.GenerationConfig(
        temperature=0.0,  # Lowest temperature for most deterministic output
        top_p=1.0,        # Use all tokens (no nucleus sampling)
        top_k=1           # Use only the most likely token
    )
    
    # Create model with search and low randomness config
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config=generation_config)
    
    genai.configure(api_key=Gemini_API_KEY)
    
    
    # Test prompt with search instructions
    prompt = """
    Analyze this song for me. First, search for the required information about the song to ensure accuracy:
    
    Title: "Ailasa Ailasa"
    Artist: "Yuvan Shankar Raja"
    
    Please provide:

1. **Energy Level**: Score from 0-10 (0=very low energy, 10=very high energy)
2. **Emotion Vector**: Provide a numerical vector [Happy, Sad, Angry] where each value is 0-10 (10 being strongest). Example: [8, 2, 1] means very happy, slightly sad, barely angry.
3. **Language**: Primary language of the song (English, Tamil, Hindi, Telugu, Malayalam, Kannada, Punjabi, etc.)
   For songs with multiple languages, use the primary language. Examples: 'My Universe' by Coldplay & BTS → 'English'
4. **Genre**: Primary musical genre (Pop, Rock, Hip-Hop, R&B, Electronic, Country, Jazz, Classical, Folk, Indie, Bollywood, Tamil Film, etc.)
5. **Lyrical Themes**: Select ONLY 1-5 most relevant themes from these 27 options (be selective and critical):
   - Hopeful Love, In Love, Lust, Toxic Relationship, Flirty, Longing, Breakup
   - Friendship, Family, Feel Good, Celebrating Life, Carefree, Escape from Life
   - Unhappy with life, Dreaming, Motivational, Reassuring, Confident
   - Insecure, Love Myself, Hate Myself, Reflection/Introspection, Nostalgia
   - Adventure, Home, Solitude, Spirituality
6. **Danceability Score**: Rate how easy it is to dance to this song (0-10, where 10=very danceable, 0=not danceable at all)
7. **Theme Scores**: For each selected theme, rate how strongly it applies (1-10, where 10=perfect match). Be critical and realistic - don't inflate scores. A 10 should be reserved for themes that are absolutely central to the song.
8. **Popularity Score**: Rate this song's popularity from 1-10 (1=obscure/unknown, 10=global hit/very famous)
   
   IMPORTANT: Think, search for the required information, including lyrics, translation and meaning and what the community thinks the song means and its other attributes and provide the best possible answer.
   Return your response as valid JSON.
   """
    
    try:
        # Use regular generate_content since tools API is not available
        response = model.generate_content(prompt)
        
        print("✅ Gemini Flash 2.5 with Search Response:")
        print(response.text)
        print("\n" + "-" * 60)
        
        # Try to parse as JSON - handle markdown formatting
        try:
            # Extract JSON from markdown if present
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]  # Remove ```json
            if text.endswith('```'):
                text = text[:-3]  # Remove ```
            
            json_response = json.loads(text.strip())
            print("✅ JSON parsed successfully!")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw text: {text}")
            return False
            
    except Exception as e:
        print(f"❌ Gemini Flash 2.5 with Search Error: {e}")
        return False

def main():
    print(f"🚀 Starting Gemini API Tests at {datetime.now()}")
    print(f"Using API Key: {Gemini_API_KEY[:10]}..." if Gemini_API_KEY else "❌ No API key found!")
    
    if not Gemini_API_KEY:
        print("❌ Please set Gemini_API_KEY in your .env file")
        return
    
    # Test both models
    pro_success = test_gemini_pro()
    flash_success = test_gemini_flash_with_search()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Gemini Pro 2.5: {'✅ PASSED' if pro_success else '❌ FAILED'}")
    print(f"Gemini Flash 2.5 with Search: {'✅ PASSED' if flash_success else '❌ FAILED'}")
    
    if pro_success and flash_success:
        print("\n🎉 Both tests passed! Gemini integration is working.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
