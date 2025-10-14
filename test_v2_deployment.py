#!/usr/bin/env python3
"""
VibeAI v2 Production Deployment Test
Tests the integrated v2 functionality in the main FastAPI app
"""

import sys
import os
import asyncio
import httpx
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_v2_endpoints():
    """Test all v2 endpoints"""
    base_url = "http://localhost:8080"
    
    print("🧪 Testing VibeAI v2 Production Deployment")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: V2 Home Page
        print("Test 1: V2 Home Page")
        try:
            response = await client.get(f"{base_url}/v2/")
            if response.status_code == 200:
                print("✅ V2 home page loads successfully")
            else:
                print(f"❌ V2 home page failed: {response.status_code}")
        except Exception as e:
            print(f"❌ V2 home page error: {e}")
        
        # Test 2: V2 API Health Check
        print("\nTest 2: V2 API Health Check")
        try:
            response = await client.get(f"{base_url}/v2/api/playlists")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ V2 API is responding")
                    print(f"📊 Found {len(data.get('playlists', {}))} default playlists")
                else:
                    print(f"❌ V2 API returned error: {data.get('error')}")
            else:
                print(f"❌ V2 API failed: {response.status_code}")
        except Exception as e:
            print(f"❌ V2 API error: {e}")
        
        # Test 3: Agentic Search
        print("\nTest 3: Agentic Search")
        try:
            search_data = {
                "query": "happy energetic songs",
                "filters": {},
                "max_results": 5
            }
            response = await client.post(f"{base_url}/v2/api/agentic-search", json=search_data)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    songs = data.get('songs', [])
                    print(f"✅ Agentic search successful: {len(songs)} songs found")
                    print(f"📊 Search method: {data.get('search_method')}")
                    print(f"📊 Total candidates: {data.get('total_candidates', 0)}")
                    print(f"📊 Total unique: {data.get('total_unique', 0)}")
                    
                    if songs:
                        print("🎵 Sample results:")
                        for i, song in enumerate(songs[:3]):
                            print(f"  {i+1}. {song.get('title')} - {song.get('artist')}")
                else:
                    print(f"❌ Agentic search failed: {data.get('error')}")
            else:
                print(f"❌ Agentic search failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Agentic search error: {e}")
        
        # Test 4: Regular Search
        print("\nTest 4: Regular Search")
        try:
            search_data = {
                "query": "romantic songs",
                "filters": {"genres": ["Pop"]},
                "limit": 3
            }
            response = await client.post(f"{base_url}/v2/api/search", json=search_data)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    songs = data.get('songs', [])
                    print(f"✅ Regular search successful: {len(songs)} songs found")
                    print(f"📊 Used Gemini: {data.get('used_gemini')}")
                else:
                    print(f"❌ Regular search failed: {data.get('error')}")
            else:
                print(f"❌ Regular search failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Regular search error: {e}")
        
        # Test 5: Static Files
        print("\nTest 5: Static Files")
        try:
            response = await client.get(f"{base_url}/v2/static/css/styles.css")
            if response.status_code == 200:
                print("✅ CSS files served successfully")
            else:
                print(f"❌ CSS files failed: {response.status_code}")
        except Exception as e:
            print(f"❌ CSS files error: {e}")
        
        try:
            response = await client.get(f"{base_url}/v2/static/js/script.js")
            if response.status_code == 200:
                print("✅ JavaScript files served successfully")
            else:
                print(f"❌ JavaScript files failed: {response.status_code}")
        except Exception as e:
            print(f"❌ JavaScript files error: {e}")
        
        # Test 6: Database Connection
        print("\nTest 6: Database Connection")
        try:
            response = await client.get(f"{base_url}/v2/api/languages")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    languages = data.get('languages', [])
                    print(f"✅ Database connection successful: {len(languages)} languages found")
                else:
                    print(f"❌ Database query failed: {data.get('error')}")
            else:
                print(f"❌ Database test failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Database test error: {e}")

def test_imports():
    """Test that all v2 modules can be imported"""
    print("\n🔧 Testing Module Imports")
    print("=" * 30)
    
    try:
        from v2.song_manager import SongManager
        print("✅ SongManager imported successfully")
    except Exception as e:
        print(f"❌ SongManager import failed: {e}")
    
    try:
        from v2.song_search import SongSearchEngine
        print("✅ SongSearchEngine imported successfully")
    except Exception as e:
        print(f"❌ SongSearchEngine import failed: {e}")
    
    try:
        from v2.simplified_agentic_search import agentic_song_search
        print("✅ Agentic search imported successfully")
    except Exception as e:
        print(f"❌ Agentic search import failed: {e}")
    
    try:
        from v2.search_tools import SearchTools
        print("✅ SearchTools imported successfully")
    except Exception as e:
        print(f"❌ SearchTools import failed: {e}")
    
    try:
        from v2.vector_embeddings import VectorEmbeddingManager
        print("✅ VectorEmbeddingManager imported successfully")
    except Exception as e:
        print(f"❌ VectorEmbeddingManager import failed: {e}")

async def main():
    """Main test function"""
    print("🚀 VibeAI v2 Production Deployment Test")
    print("=" * 60)
    
    # Test imports first
    test_imports()
    
    # Test endpoints
    await test_v2_endpoints()
    
    print("\n🎉 Deployment test completed!")
    print("\n📋 Next Steps:")
    print("1. Set up Neon PostgreSQL database")
    print("2. Run database migration script")
    print("3. Deploy to production")
    print("4. Test in production environment")

if __name__ == "__main__":
    asyncio.run(main())
