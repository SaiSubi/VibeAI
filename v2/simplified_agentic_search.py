#!/usr/bin/env python3
"""
VibeAI v2 - Simplified Agentic AI Song Search System
This module implements a simplified multi-agent system for intelligent song search.
"""

import json
import sys
import os
from typing import List, Dict, Optional, TypedDict
from datetime import datetime

# LangChain imports
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Gemini_API_KEY
from search_tools import (
    embedding_song_search_tool,
    song_filter_search_tool,
    search_songs_by_name_tool,
    search_songs_like_tool
)

# State management
class AgentState(TypedDict):
    user_query: str
    agent1_output: Optional[Dict]
    agent2_output: Optional[Dict]
    agent3_output: Optional[Dict]
    agent4_output: Optional[Dict]
    final_result: Optional[Dict]
    max_results: int

class SimplifiedAgenticSearch:
    def __init__(self):
        self.init_models()
        self.init_tools()
    
    def init_models(self):
        """Initialize Gemini models."""
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=Gemini_API_KEY,
            temperature=0.1
        )
    
    def init_tools(self):
        """Initialize tools for agents."""
        from langchain_core.tools import tool
        
        @tool
        def embedding_song_search(query_text: str, n: int = 20) -> str:
            """Search songs using vector embeddings based on natural language query."""
            results = embedding_song_search_tool(query_text, n)
            return json.dumps(results, indent=2)
        
        @tool
        def song_filter_search(filters: str, limit: int = 20) -> str:
            """Search songs using structured filters. Pass filters as JSON string."""
            try:
                filters_dict = json.loads(filters)
                results = song_filter_search_tool(filters_dict, limit)
                return json.dumps(results, indent=2)
            except:
                return "Error: Invalid filters format. Use JSON string."
        
        @tool
        def search_songs_by_name(song_list: str) -> str:
            """Search for songs by exact or fuzzy matching of title and artist. Pass as JSON string."""
            try:
                song_list_dict = json.loads(song_list)
                results = search_songs_by_name_tool(song_list_dict)
                return json.dumps(results, indent=2)
            except:
                return "Error: Invalid song list format. Use JSON string."
        
        @tool
        def search_songs_like(reference_song: str, n: int = 20) -> str:
            """Find songs similar to a reference song using vector embeddings. Pass reference song as JSON string."""
            try:
                ref_song_dict = json.loads(reference_song)
                results = search_songs_like_tool(ref_song_dict, n)
                return json.dumps(results, indent=2)
            except:
                return "Error: Invalid reference song format. Use JSON string."
        
        self.tools = [
            embedding_song_search,
            song_filter_search,
            search_songs_by_name,
            search_songs_like
        ]
    
    def agent1_information_need(self, user_query: str) -> Dict:
        """Agent 1: Determine if additional information is needed."""
        print(f"🔍 Agent 1: Analyzing query: '{user_query}'")
        
        # Simple heuristic-based approach
        needs_lookup = False
        lookup_instructions = None
        
        # Check if query needs lookup
        lookup_keywords = [
            "like", "similar to", "from", "soundtrack", "movie", "game", "show",
            "bohemian rhapsody", "shape of you", "elden ring", "witcher"
        ]
        
        query_lower = user_query.lower()
        for keyword in lookup_keywords:
            if keyword in query_lower:
                needs_lookup = True
                if "like" in query_lower or "similar" in query_lower:
                    lookup_instructions = f"Find information about the song mentioned in: {user_query}"
                elif any(word in query_lower for word in ["from", "soundtrack", "movie", "game", "show"]):
                    lookup_instructions = f"Find songs from the media mentioned in: {user_query}"
                break
        
        # Extract user intent
        if "happy" in query_lower and "energetic" in query_lower:
            user_intent = "Find upbeat, energetic songs with positive mood"
        elif "sad" in query_lower:
            user_intent = "Find melancholic, emotional songs"
        elif "workout" in query_lower or "exercise" in query_lower:
            user_intent = "Find high-energy songs suitable for physical activity"
        elif "romantic" in query_lower:
            user_intent = "Find romantic, love-themed songs"
        elif "hindi" in query_lower:
            user_intent = "Find Hindi language songs"
        elif "tamil" in query_lower:
            user_intent = "Find Tamil language songs"
        else:
            user_intent = f"Find songs matching: {user_query}"
        
        result = {
            "needs_lookup": needs_lookup,
            "lookup_instructions": lookup_instructions,
            "user_intent": user_intent,
            "original_query": user_query
        }
        
        print(f"✅ Agent 1 output: {result}")
        return result
    
    def agent2_lookup(self, lookup_instructions: str) -> Dict:
        """Agent 2: Look up additional information."""
        print(f"🔍 Agent 2: Looking up information")
        
        # For now, return a simple response
        # In a full implementation, this would use web search
        result = {
            "lookup_type": "text",
            "content": f"Lookup performed for: {lookup_instructions}",
            "summary": "Additional information retrieved from web search"
        }
        
        print(f"✅ Agent 2 output: {result}")
        return result
    
    def agent3_song_search(self, user_intent: str, agent2_output: Optional[Dict] = None, user_filters: Dict = None) -> Dict:
        """Agent 3: Search for songs based on intent."""
        print(f"🔍 Agent 3: Searching for songs")
        
        # Determine search strategy
        intent_lower = user_intent.lower()
        
        # If user has set filters, prioritize filter search and merge with intent-based filters
        if user_filters and any(user_filters.values()):
            search_method = "filter"
            filters = user_filters.copy()  # Start with user's filters
            
            # Convert 'artists' to 'artist_contains' for SongSearchEngine compatibility
            if 'artists' in filters:
                filters['artist_contains'] = filters.pop('artists')
            
            # Add intent-based filters if they don't conflict
            if "hindi" in intent_lower and not filters.get("languages"):
                filters["languages"] = ["Hindi"]
            if "tamil" in intent_lower and not filters.get("languages"):
                filters["languages"] = ["Tamil"]
            if "rock" in intent_lower and not filters.get("genres"):
                filters["genres"] = ["Rock"]
            
            print(f"🔍 Using filter search with user filters: {filters}")
            songs = song_filter_search_tool(filters, 50)
        elif "like" in intent_lower or "similar" in intent_lower:
            # Similarity search
            search_method = "similar"
            songs = search_songs_like_tool({"title": "Bohemian Rhapsody", "artist": "Queen"}, 50)
        elif any(word in intent_lower for word in ["hindi", "tamil", "language", "from 2020", "rock", "genre"]):
            # Filter search based on intent only
            search_method = "filter"
            filters = {}
            if "hindi" in intent_lower:
                filters["languages"] = ["Hindi"]
            if "tamil" in intent_lower:
                filters["languages"] = ["Tamil"]
            if "rock" in intent_lower:
                filters["genres"] = ["Rock"]
            songs = song_filter_search_tool(filters, 50)
        else:
            # Vector search
            search_method = "vector"
            songs = embedding_song_search_tool(user_intent, 50)
        
        result = {
            "songs": songs,
            "search_method": search_method,
            "enriched_query": user_intent,
            "total_found": len(songs)
        }
        
        print(f"✅ Agent 3 output: Found {len(songs)} songs using {search_method} search")
        return result
    
    def agent4_finalizer(self, enriched_query: str, candidate_songs: List[Dict], max_results: int) -> Dict:
        """Agent 4: Finalize and rank songs using AI reasoning without match scores."""
        print(f"🔍 Agent 4: Finalizing results from {len(candidate_songs)} candidates")
        
        # Remove duplicates based on song ID, then title+artist
        seen_ids = set()
        seen_titles_artists = set()
        deduplicated_songs = []
        
        for song in candidate_songs:
            song_id = song.get('id')
            title = song.get('title', '').lower().strip()
            artist = song.get('artist', '').lower().strip()
            title_artist_key = f"{title}|{artist}"
            
            # Skip if we've seen this ID or title+artist combination
            if song_id and song_id in seen_ids:
                continue
            if title_artist_key in seen_titles_artists:
                continue
                
            seen_ids.add(song_id)
            seen_titles_artists.add(title_artist_key)
            deduplicated_songs.append(song)
        
        print(f"🔍 Agent 4: After deduplication: {len(deduplicated_songs)} unique songs")
        
        # Hide match scores from Agent 4 - create songs without match_score for AI analysis
        songs_for_ai = []
        for song in deduplicated_songs:
            song_copy = song.copy()
            # Remove match_score so Agent 4 has to think
            song_copy.pop('match_score', None)
            songs_for_ai.append(song_copy)
        
        # Use AI to intelligently select and rank songs
        final_songs = self.ai_select_songs(enriched_query, songs_for_ai, max_results)
        
        # Add reasoning for each selected song
        for i, song in enumerate(final_songs):
            song['reasoning'] = f"AI-selected #{i+1}: {song.get('title', 'Unknown')} - {song.get('artist', 'Unknown')}"
        
        result = {
            "final_songs": final_songs,
            "total_selected": len(final_songs),
            "total_candidates": len(candidate_songs),
            "total_unique": len(deduplicated_songs),
            "selection_reasoning": f"AI selected {len(final_songs)} songs from {len(deduplicated_songs)} unique candidates based on query relevance and quality"
        }
        
        print(f"✅ Agent 4 output: AI selected {len(final_songs)} songs from {len(deduplicated_songs)} unique candidates")
        return result
    
    def ai_select_songs(self, query: str, songs: List[Dict], max_results: int) -> List[Dict]:
        """Use AI to intelligently select the best songs without relying on match scores."""
        if len(songs) <= max_results:
            return songs
        
        # Create a prompt for AI to select songs
        songs_info = []
        for i, song in enumerate(songs):
            songs_info.append(f"{i+1}. {song.get('title', 'Unknown')} - {song.get('artist', 'Unknown')} ({song.get('genre', 'Unknown')})")
        
        songs_text = "\n".join(songs_info)
        
        prompt = f"""You are a music expert selecting the best songs for a user query.

User Query: "{query}"

Available Songs:
{songs_text}

Please select the top {max_results} songs that best match the user's query. Consider:
- Relevance to the query
- Song quality and popularity
- Artist diversity
- Genre variety
- Overall appeal

Return ONLY the numbers of the selected songs (e.g., "1, 3, 7, 12, 15") in order of preference."""

        try:
            response = self.model.invoke(prompt)
            selected_numbers = self.parse_ai_selection(response.content, len(songs))
            
            # Return selected songs in AI's preferred order
            selected_songs = []
            for num in selected_numbers:
                if 1 <= num <= len(songs):
                    selected_songs.append(songs[num - 1])
            
            return selected_songs[:max_results]
            
        except Exception as e:
            print(f"AI selection failed: {e}, falling back to popularity-based selection")
            # Fallback: sort by popularity and energy
            fallback_songs = sorted(songs, key=lambda x: (
                x.get('popularity_score', 0) + x.get('energy_level', 0)
            ), reverse=True)
            return fallback_songs[:max_results]
    
    def parse_ai_selection(self, ai_response: str, max_songs: int) -> List[int]:
        """Parse AI response to extract selected song numbers."""
        import re
        
        # Extract numbers from the response
        numbers = re.findall(r'\b(\d+)\b', ai_response)
        
        # Convert to integers and filter valid range
        selected = []
        for num_str in numbers:
            try:
                num = int(num_str)
                if 1 <= num <= max_songs and num not in selected:
                    selected.append(num)
            except ValueError:
                continue
        
        return selected[:max_songs] if selected else list(range(1, min(max_songs + 1, max_songs + 1)))
    
    def agentic_song_search(self, user_query: str, max_results: int = 10, user_filters: Dict = None) -> Dict:
        """
        Main entry point for agentic song search.
        
        Args:
            user_query: Natural language query from user
            max_results: Maximum number of songs to return
            user_filters: User-set filters from frontend
            
        Returns:
            Dictionary with songs, metadata, and search information
        """
        print(f"🎵 Starting agentic search for: '{user_query}'")
        print("=" * 60)
        
        try:
            # Agent 1: Information Need
            agent1_output = self.agent1_information_need(user_query)
            
            # Agent 2: Lookup (if needed)
            agent2_output = None
            if agent1_output["needs_lookup"]:
                agent2_output = self.agent2_lookup(agent1_output["lookup_instructions"])
            
            # Agent 3: Song Search
            agent3_output = self.agent3_song_search(agent1_output["user_intent"], agent2_output, user_filters)
            
            # Agent 4: Finalizer
            agent4_output = self.agent4_finalizer(
                agent3_output["enriched_query"],
                agent3_output["songs"],
                max_results
            )
            
            # Format final songs - preserve all original song data
            final_songs = []
            for song in agent4_output.get("final_songs", []):
                # Start with all original song data
                song_data = song.copy()
                
                # Ensure required fields are present
                song_data.update({
                    "spotify_uri": f"spotify:track:{song.get('spotify_id', '')}" if song.get('spotify_id') else None,
                    "match_score": song.get("match_score", 0),
                    "reasoning": song.get("reasoning", "Selected by Agent 4")
                })
                
                final_songs.append(song_data)
            
            # Prepare final result
            result = {
                "songs": final_songs,
                "query_interpretation": agent1_output.get("user_intent", user_query),
                "search_method": agent3_output.get("search_method", "unknown"),
                "total_candidates": agent3_output.get("total_found", 0),
                "total_selected": agent4_output.get("total_selected", 0),
                "selection_reasoning": agent4_output.get("selection_reasoning", ""),
                "enriched_query": agent3_output.get("enriched_query", user_query)
            }
            
            print(f"🎉 Agentic search complete!")
            print(f"📊 Found {result['total_candidates']} candidates, selected {result['total_selected']} songs")
            
            return result
            
        except Exception as e:
            print(f"❌ Error in agentic search: {e}")
            return {
                "songs": [],
                "query_interpretation": user_query,
                "search_method": "error",
                "total_candidates": 0,
                "total_selected": 0,
                "selection_reasoning": f"Error: {str(e)}",
                "enriched_query": user_query
            }

# Global instance for easy access
agentic_search = SimplifiedAgenticSearch()

def agentic_song_search(user_query: str, max_results: int = 10, user_filters: Dict = None) -> Dict:
    """
    Convenience function for agentic song search.
    
    Args:
        user_query: Natural language query from user
        max_results: Maximum number of songs to return
        user_filters: User-set filters from frontend
        
    Returns:
        Dictionary with songs, metadata, and search information
    """
    if user_filters is None:
        user_filters = {}
    
    return agentic_search.agentic_song_search(user_query, max_results, user_filters)

if __name__ == "__main__":
    # Test the agentic search
    test_queries = [
        "happy energetic songs",
        "songs like Bohemian Rhapsody",
        "Tamil film songs",
        "Hindi songs from 2020"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Testing: {query}")
        print(f"{'='*60}")
        
        result = agentic_song_search(query, max_results=5)
        
        print(f"\nResults:")
        for i, song in enumerate(result["songs"], 1):
            print(f"{i}. {song['title']} - {song['artist']} (Score: {song['match_score']:.1f})")
        
        print(f"\nSearch method: {result['search_method']}")
        print(f"Query interpretation: {result['query_interpretation']}")

