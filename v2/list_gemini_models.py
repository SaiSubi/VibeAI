#!/usr/bin/env python3

import google.generativeai as genai
import sys
import os

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Gemini_API_KEY

def list_models():
    """List available Gemini models"""
    genai.configure(api_key=Gemini_API_KEY)
    
    try:
        models = genai.list_models()
        print("Available Gemini models:")
        for model in models:
            if 'gemini' in model.name.lower():
                print(f"- {model.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
