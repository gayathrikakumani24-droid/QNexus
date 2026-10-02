"""
Notice: Qnexus has migrated from Qdrant to Pinecone Cloud.
This script delegates to sync_pinecone.py for backward compatibility.
"""
import sys
from sync_pinecone import main

if __name__ == "__main__":
    print("[NOTICE] sync_qdrant.py is deprecated. Delegating to sync_pinecone.py...")
    main()
