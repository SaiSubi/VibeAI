#!/usr/bin/env python3
"""
VibeAI v2 - Agentic AI Song Search System
This module implements a multi-agent system using LangChain for intelligent song search.
"""

import json
import sys
import os
from typing import List, Dict, Optional, TypedDict, Annotated
from datetime import datetime

# LangChain imports
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Gemini_API_KEY
from search_tools import (
    embedding_song_search_tool,
    song_filter_search_tool,
    search_songs_by_name_tool,
    get_song_embedding_tool,
    generate_query_embedding_tool,
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

class AgenticSongSearch:
    def __init__(self):
        self.init_models()
        self.init_tools()
        self.init_agents()
        self.init_graph()
    
    def init_models(self):
        """Initialize Gemini models for different agents."""
        # Agent 1, 3, 4: Regular Gemini 2.5 Flash
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=Gemini_API_KEY,
            temperature=0.1
        )
        
        # Agent 2: Gemini with search grounding
        self.model_with_search = ChatGoogleGenerativeAI(
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
        def get_song_embedding(spotify_id: str) -> str:
            """Retrieve vector embedding for a specific song by Spotify ID."""
            embedding = get_song_embedding_tool(spotify_id)
            if embedding:
                return json.dumps(embedding)
            return "No embedding found for this song."
        
        @tool
        def generate_query_embedding(text: str) -> str:
            """Generate vector embedding for natural language text."""
            embedding = generate_query_embedding_tool(text)
            if embedding:
                return json.dumps(embedding)
            return "Failed to generate embedding."
        
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
            get_song_embedding,
            generate_query_embedding,
            search_songs_like
        ]
    
    def init_agents(self):
        """Initialize all 4 agents with their specific prompts and tools."""
        
        # Agent 1: Information Need Agent
        agent1_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are Agent 1: Information Need Agent. Your job is to analyze user queries and determine if additional information is needed.

Available database fields:
- Basic info: title, artist, album, release_year, spotify_id
- Audio features: energy_level, danceability_score, tempo, acousticness, popularity_score
- Analysis: mood_tags (happy,sad,angry), lyrical_themes, genre, language
- Descriptions: song_description

Your task:
1. Parse the user query and extract intent
2. Determine if additional information is needed from the internet
3. If lookup is needed, provide clear instructions for Agent 2

Return JSON format:
{
    "needs_lookup": true/false,
    "lookup_instructions": "specific instructions for Agent 2" or null,
    "user_intent": "what the user wants",
    "original_query": "original user query"
}

Examples:
- "Songs like Bohemian Rhapsody" → needs_lookup=True (get song info)
- "Songs from Elden Ring" → needs_lookup=True (game soundtrack list)
- "Happy energetic songs" → needs_lookup=False (direct search)
- "Hindi songs from 2020" → needs_lookup=False (filter search)"""),
            ("human", "{input}"),
            ("ai", "{agent_scratchpad}")
        ])
        
        self.agent1 = create_openai_tools_agent(self.model, [], agent1_prompt)
        
        # Agent 2: Lookup Agent
        agent2_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are Agent 2: Lookup Agent. You research the internet to find additional information.

Your task:
1. Receive instructions from Agent 1
2. Use web search to find relevant information
3. Return either text information or a list of songs

Return JSON format:
{
    "lookup_type": "text" or "song_list",
    "content": "text information" or [{"title": "Song Name", "artist": "Artist Name"}],
    "summary": "brief summary of findings"
}

Focus on:
- Song information (title, artist, genre, mood, themes)
- Soundtrack lists (games, movies, shows)
- Music style descriptions
- Artist discographies"""),
            ("human", "{input}"),
            ("ai", "{agent_scratchpad}")
        ])
        
        self.agent2 = create_openai_tools_agent(self.model_with_search, [], agent2_prompt)
        
        # Agent 3: Song Search Agent
        agent3_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are Agent 3: Song Search Agent. You decide how to search for songs and execute the search.

Available tools:
- embedding_song_search: For semantic queries like "happy songs", "workout music"
- song_filter_search: For specific attributes like "Hindi songs from 2020", "high energy rock"
- search_songs_by_name: For specific song references from Agent 2
- search_songs_like: For "songs like X" queries
- get_song_embedding: To get embeddings for specific songs
- generate_query_embedding: To convert text to embeddings

Your task:
1. Analyze the user intent and Agent 2 output (if available)
2. Choose appropriate search strategy
3. Execute searches using tools
4. Return up to 50 songs with match scores

Return JSON format:
{
    "songs": [list of songs with id, spotify_id, match_score, title, artist],
    "search_method": "vector", "filter", "hybrid", "name", or "similar",
    "enriched_query": "detailed description of what user wants",
    "total_found": number
}

Decision logic:
- Vector search: Vague/semantic queries ("happy songs", "workout music")
- Filter search: Specific attributes ("Hindi songs from 2020", "high energy rock")
- Name search: Specific song references from Agent 2
- Similar search: "songs like X" queries
- Hybrid: Combine multiple approaches"""),
            ("human", "{input}"),
            ("ai", "{agent_scratchpad}")
        ])
        
        self.agent3 = create_openai_tools_agent(self.model, self.tools, agent3_prompt)
        
        # Agent 4: Finalizer Agent
        agent4_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are Agent 4: Finalizer Agent. You rank and select the final songs to return.

Your task:
1. Receive enriched query and candidate songs from Agent 3
2. Rank songs based on user intent and relevance
3. Select the best songs (up to max_results)
4. Provide reasoning for your selections

Return JSON format:
{
    "final_songs": [ordered list with id, spotify_id, title, artist, match_score, reasoning],
    "total_selected": number,
    "selection_reasoning": "explanation of ranking criteria"
}

Consider:
- Match score from Agent 3
- User intent and context
- Song quality and popularity
- Diversity in results
- Relevance to query"""),
            ("human", "{input}"),
            ("ai", "{agent_scratchpad}")
        ])
        
        self.agent4 = create_openai_tools_agent(self.model, [], agent4_prompt)
    
    def init_graph(self):
        """Initialize the LangGraph workflow."""
        
        # Create agent executors
        self.agent1_executor = AgentExecutor(agent=self.agent1, tools=[], verbose=True)
        self.agent2_executor = AgentExecutor(agent=self.agent2, tools=[], verbose=True)
        self.agent3_executor = AgentExecutor(agent=self.agent3, tools=self.tools, verbose=True)
        self.agent4_executor = AgentExecutor(agent=self.agent4, tools=[], verbose=True)
        
        # Define workflow functions
        def agent1_node(state: AgentState) -> AgentState:
            """Agent 1: Information Need Agent."""
            print(f"🔍 Agent 1: Analyzing query: '{state['user_query']}'")
            
            result = self.agent1_executor.invoke({
                "input": f"User query: {state['user_query']}"
            })
            
            try:
                agent1_output = json.loads(result["output"])
            except:
                agent1_output = {
                    "needs_lookup": False,
                    "lookup_instructions": None,
                    "user_intent": state['user_query'],
                    "original_query": state['user_query']
                }
            
            state["agent1_output"] = agent1_output
            print(f"✅ Agent 1 output: {agent1_output}")
            return state
        
        def agent2_node(state: AgentState) -> AgentState:
            """Agent 2: Lookup Agent."""
            print(f"🔍 Agent 2: Looking up information")
            
            lookup_instructions = state["agent1_output"]["lookup_instructions"]
            result = self.agent2_executor.invoke({
                "input": f"Lookup instructions: {lookup_instructions}"
            })
            
            try:
                agent2_output = json.loads(result["output"])
            except:
                agent2_output = {
                    "lookup_type": "text",
                    "content": "Lookup failed",
                    "summary": "Could not retrieve additional information"
                }
            
            state["agent2_output"] = agent2_output
            print(f"✅ Agent 2 output: {agent2_output}")
            return state
        
        def agent3_node(state: AgentState) -> AgentState:
            """Agent 3: Song Search Agent."""
            print(f"🔍 Agent 3: Searching for songs")
            
            # Prepare input for Agent 3
            user_intent = state["agent1_output"]["user_intent"]
            agent2_output = state.get("agent2_output")
            
            if agent2_output:
                input_text = f"User intent: {user_intent}\nAdditional info from lookup: {json.dumps(agent2_output)}"
            else:
                input_text = f"User intent: {user_intent}"
            
            result = self.agent3_executor.invoke({
                "input": input_text
            })
            
            try:
                agent3_output = json.loads(result["output"])
            except:
                agent3_output = {
                    "songs": [],
                    "search_method": "vector",
                    "enriched_query": user_intent,
                    "total_found": 0
                }
            
            state["agent3_output"] = agent3_output
            print(f"✅ Agent 3 output: Found {agent3_output.get('total_found', 0)} songs")
            return state
        
        def agent4_node(state: AgentState) -> AgentState:
            """Agent 4: Finalizer Agent."""
            print(f"🔍 Agent 4: Finalizing results")
            
            enriched_query = state["agent3_output"]["enriched_query"]
            candidate_songs = state["agent3_output"]["songs"]
            max_results = state["max_results"]
            
            input_text = f"""Enriched query: {enriched_query}
Candidate songs: {json.dumps(candidate_songs[:20])}  # Limit to first 20 for prompt
Max results needed: {max_results}"""
            
            result = self.agent4_executor.invoke({
                "input": input_text
            })
            
            try:
                agent4_output = json.loads(result["output"])
            except:
                # Fallback: return top songs by match score
                sorted_songs = sorted(candidate_songs, key=lambda x: x.get('match_score', 0), reverse=True)
                agent4_output = {
                    "final_songs": sorted_songs[:max_results],
                    "total_selected": min(len(sorted_songs), max_results),
                    "selection_reasoning": "Fallback: ranked by match score"
                }
            
            state["agent4_output"] = agent4_output
            print(f"✅ Agent 4 output: Selected {agent4_output.get('total_selected', 0)} songs")
            return state
        
        def should_lookup(state: AgentState) -> str:
            """Determine if lookup is needed."""
            needs_lookup = state["agent1_output"].get("needs_lookup", False)
            return "lookup" if needs_lookup else "search"
        
        # Build the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent1", agent1_node)
        workflow.add_node("agent2", agent2_node)
        workflow.add_node("agent3", agent3_node)
        workflow.add_node("agent4", agent4_node)
        
        # Add edges
        workflow.set_entry_point("agent1")
        workflow.add_conditional_edges(
            "agent1",
            should_lookup,
            {
                "lookup": "agent2",
                "search": "agent3"
            }
        )
        workflow.add_edge("agent2", "agent3")
        workflow.add_edge("agent3", "agent4")
        workflow.add_edge("agent4", END)
        
        # Compile the graph
        self.graph = workflow.compile()
    
    def agentic_song_search(self, user_query: str, max_results: int = 20) -> Dict:
        """
        Main entry point for agentic song search.
        
        Args:
            user_query: Natural language query from user
            max_results: Maximum number of songs to return
            
        Returns:
            Dictionary with songs, metadata, and search information
        """
        print(f"🎵 Starting agentic search for: '{user_query}'")
        print("=" * 60)
        
        # Initialize state
        initial_state = {
            "user_query": user_query,
            "agent1_output": None,
            "agent2_output": None,
            "agent3_output": None,
            "agent4_output": None,
            "final_result": None,
            "max_results": max_results
        }
        
        try:
            # Run the workflow
            final_state = self.graph.invoke(initial_state)
            
            # Extract results
            agent4_output = final_state["agent4_output"]
            agent3_output = final_state["agent3_output"]
            agent1_output = final_state["agent1_output"]
            
            # Format final songs
            final_songs = []
            for song in agent4_output.get("final_songs", []):
                song_data = {
                    "id": song.get("id"),
                    "spotify_id": song.get("spotify_id"),
                    "spotify_uri": f"spotify:track:{song.get('spotify_id', '')}",
                    "title": song.get("title"),
                    "artist": song.get("artist"),
                    "match_score": song.get("match_score", 0),
                    "reasoning": song.get("reasoning", "Selected by Agent 4")
                }
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
agentic_search = AgenticSongSearch()

def agentic_song_search(user_query: str, max_results: int = 20) -> Dict:
    """
    Convenience function for agentic song search.
    
    Args:
        user_query: Natural language query from user
        max_results: Maximum number of songs to return
        
    Returns:
        Dictionary with songs, metadata, and search information
    """
    return agentic_search.agentic_song_search(user_query, max_results)

if __name__ == "__main__":
    # Test the agentic search
    test_queries = [
        "happy energetic songs",
        "songs like Bohemian Rhapsody",
        "Tamil film songs",
        "songs from Elden Ring soundtrack"
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
