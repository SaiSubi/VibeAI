#!/usr/bin/env python3
"""
VibeAI v2 - Generate Embeddings for Entire Database
This script processes all songs in the database to generate vector embeddings.
"""

import time
from vector_embeddings import VectorEmbeddingManager

def main():
    """Generate embeddings for all songs in the database"""
    print("🎵 VibeAI v2 - Full Database Embedding Generation")
    print("=" * 60)
    
    # Initialize manager
    manager = VectorEmbeddingManager()
    
    # Get current stats
    stats = manager.get_embedding_stats()
    print(f"📊 Database Stats:")
    print(f"   Total songs: {stats['total_songs']}")
    print(f"   Songs with embeddings: {stats['songs_with_embeddings']}")
    print(f"   Songs without embeddings: {stats['songs_without_embeddings']}")
    print(f"   Coverage: {stats['embedding_coverage']:.1f}%")
    
    if stats['songs_without_embeddings'] == 0:
        print("✅ All songs already have embeddings!")
        return
    
    # Calculate estimated time (no rate limiting)
    estimated_minutes = stats['songs_without_embeddings'] * 0.1  # ~0.1 seconds per song
    estimated_hours = estimated_minutes / 60
    
    print(f"\n⏰ Estimated time: {estimated_minutes:.1f} minutes ({estimated_hours:.1f} hours)")
    print(f"🔄 Processing in batches of 25 songs each (no rate limiting)")
    print(f"📝 Progress will be saved after each batch")
    
    # Auto-proceed for non-interactive execution
    print(f"\n🚀 Auto-starting embedding generation for {stats['songs_without_embeddings']} songs...")
    
    print(f"\n🚀 Starting embedding generation...")
    print("=" * 60)
    
    total_processed = 0
    total_errors = 0
    batch_size = 25
    batch_number = 1
    
    start_time = time.time()
    
    while True:
        print(f"\n📦 Batch {batch_number} - Processing {batch_size} songs...")
        
        # Process batch
        results = manager.generate_embeddings_for_songs(limit=batch_size)
        
        batch_processed = results['processed']
        batch_errors = results['errors']
        
        total_processed += batch_processed
        total_errors += batch_errors
        
        print(f"✅ Batch {batch_number} complete: {batch_processed} processed, {batch_errors} errors")
        
        # Check if we're done
        if batch_processed == 0:
            print("🎉 All songs processed!")
            break
        
        # Update stats
        current_stats = manager.get_embedding_stats()
        print(f"📊 Progress: {current_stats['songs_with_embeddings']}/{current_stats['total_songs']} songs ({current_stats['embedding_coverage']:.1f}%)")
        
        batch_number += 1
        
        # No delay between batches - process as fast as possible
        if batch_processed > 0:
            print(f"⚡ Processing next batch immediately...")
    
    # Final summary
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "=" * 60)
    print("🎉 FULL DATABASE EMBEDDING GENERATION COMPLETE!")
    print("=" * 60)
    print(f"📊 Total songs processed: {total_processed}")
    print(f"❌ Total errors: {total_errors}")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes ({total_time/3600:.1f} hours)")
    
    # Final stats
    final_stats = manager.get_embedding_stats()
    print(f"📈 Final coverage: {final_stats['embedding_coverage']:.1f}%")
    print(f"🎵 Songs with embeddings: {final_stats['songs_with_embeddings']}")
    
    print("\n✅ Embedding generation complete! You can now use vector search.")

if __name__ == "__main__":
    main()
