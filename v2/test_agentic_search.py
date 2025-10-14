#!/usr/bin/env python3
"""
VibeAI v2 - Test Suite for Agentic Search System
This module tests the agentic search system with various query types.
"""

import sys
import os
import time
from typing import List, Dict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simplified_agentic_search import agentic_song_search

class AgenticSearchTester:
    def __init__(self):
        self.test_results = []
    
    def run_test(self, query: str, expected_methods: List[str] = None, max_results: int = 5) -> Dict:
        """
        Run a single test case.
        
        Args:
            query: Test query
            expected_methods: Expected search methods (for validation)
            max_results: Maximum results to return
            
        Returns:
            Test result dictionary
        """
        print(f"\n{'='*60}")
        print(f"🧪 Testing: '{query}'")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            result = agentic_song_search(query, max_results)
            end_time = time.time()
            
            # Validate result structure
            required_keys = ["songs", "query_interpretation", "search_method", "total_candidates", "total_selected"]
            missing_keys = [key for key in required_keys if key not in result]
            
            if missing_keys:
                print(f"❌ Missing keys in result: {missing_keys}")
                return {"status": "failed", "error": f"Missing keys: {missing_keys}"}
            
            # Display results
            print(f"\n📊 Results:")
            print(f"   Query interpretation: {result['query_interpretation']}")
            print(f"   Search method: {result['search_method']}")
            print(f"   Candidates found: {result['total_candidates']}")
            print(f"   Songs selected: {result['total_selected']}")
            print(f"   Response time: {end_time - start_time:.2f} seconds")
            
            if result['songs']:
                print(f"\n🎵 Top songs:")
                for i, song in enumerate(result['songs'][:3], 1):
                    print(f"   {i}. {song['title']} - {song['artist']} (Score: {song['match_score']:.1f})")
            else:
                print(f"\n❌ No songs returned")
            
            # Validate search method if expected
            if expected_methods and result['search_method'] not in expected_methods:
                print(f"⚠️  Unexpected search method: {result['search_method']} (expected: {expected_methods})")
            
            test_result = {
                "status": "passed",
                "query": query,
                "result": result,
                "response_time": end_time - start_time,
                "expected_methods": expected_methods
            }
            
            self.test_results.append(test_result)
            return test_result
            
        except Exception as e:
            end_time = time.time()
            print(f"❌ Test failed with error: {e}")
            
            test_result = {
                "status": "failed",
                "query": query,
                "error": str(e),
                "response_time": end_time - start_time
            }
            
            self.test_results.append(test_result)
            return test_result
    
    def run_all_tests(self):
        """Run comprehensive test suite."""
        print("🎵 VibeAI v2 - Agentic Search Test Suite")
        print("=" * 60)
        
        # Test cases with expected behaviors
        test_cases = [
            # Simple semantic queries (should use vector search)
            {
                "query": "happy energetic songs",
                "expected_methods": ["vector"],
                "description": "Simple semantic query"
            },
            {
                "query": "sad breakup songs",
                "expected_methods": ["vector"],
                "description": "Emotional semantic query"
            },
            {
                "query": "workout music",
                "expected_methods": ["vector"],
                "description": "Activity-based query"
            },
            
            # Specific attribute queries (should use filter search)
            {
                "query": "Hindi songs from 2020",
                "expected_methods": ["filter"],
                "description": "Language and year filter"
            },
            {
                "query": "high energy rock songs",
                "expected_methods": ["filter"],
                "description": "Genre and energy filter"
            },
            {
                "query": "Tamil film songs",
                "expected_methods": ["filter", "vector"],
                "description": "Language and genre filter"
            },
            
            # "Songs like X" queries (should use similar search)
            {
                "query": "songs like Bohemian Rhapsody",
                "expected_methods": ["similar", "vector"],
                "description": "Similarity-based query"
            },
            {
                "query": "songs similar to Shape of You",
                "expected_methods": ["similar", "vector"],
                "description": "Similarity query with different phrasing"
            },
            
            # External knowledge queries (should trigger lookup)
            {
                "query": "songs from Elden Ring soundtrack",
                "expected_methods": ["name", "vector"],
                "description": "Game soundtrack query"
            },
            {
                "query": "music from The Witcher 3",
                "expected_methods": ["name", "vector"],
                "description": "Game music query"
            },
            
            # Complex multi-criteria queries
            {
                "query": "upbeat Hindi songs for workout",
                "expected_methods": ["hybrid", "vector", "filter"],
                "description": "Multi-criteria query"
            },
            {
                "query": "romantic Bollywood songs from 2010s",
                "expected_methods": ["hybrid", "filter"],
                "description": "Complex filter query"
            }
        ]
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test {i}/{total_tests}: {test_case['description']}")
            result = self.run_test(
                test_case["query"],
                test_case["expected_methods"],
                max_results=5
            )
            
            if result["status"] == "passed":
                passed_tests += 1
        
        # Summary
        print(f"\n{'='*60}")
        print(f"📊 TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
        
        # Performance summary
        response_times = [r["response_time"] for r in self.test_results if "response_time" in r]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            print(f"\n⏱️  Performance:")
            print(f"   Average response time: {avg_time:.2f}s")
            print(f"   Fastest response: {min_time:.2f}s")
            print(f"   Slowest response: {max_time:.2f}s")
        
        # Method distribution
        methods_used = [r["result"]["search_method"] for r in self.test_results if r["status"] == "passed"]
        method_counts = {}
        for method in methods_used:
            method_counts[method] = method_counts.get(method, 0) + 1
        
        print(f"\n🔍 Search methods used:")
        for method, count in method_counts.items():
            print(f"   {method}: {count} times")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": passed_tests/total_tests*100,
            "avg_response_time": avg_time if response_times else 0,
            "method_distribution": method_counts
        }
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        print(f"\n{'='*60}")
        print(f"🧪 EDGE CASE TESTS")
        print(f"{'='*60}")
        
        edge_cases = [
            "",  # Empty query
            "asdfghjkl",  # Nonsensical query
            "songs",  # Very vague query
            "songs like a song that doesn't exist",  # Non-existent reference
            "songs from a movie that doesn't exist",  # Non-existent movie
        ]
        
        for query in edge_cases:
            print(f"\n🔍 Testing edge case: '{query}'")
            result = self.run_test(query, max_results=3)
            
            if result["status"] == "passed":
                print(f"✅ Handled gracefully: {len(result['result']['songs'])} songs returned")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")

def main():
    """Run the test suite."""
    tester = AgenticSearchTester()
    
    # Run main test suite
    summary = tester.run_all_tests()
    
    # Run edge case tests
    tester.test_edge_cases()
    
    print(f"\n🎉 Test suite complete!")
    
    # Return summary for programmatic use
    return summary

if __name__ == "__main__":
    main()
