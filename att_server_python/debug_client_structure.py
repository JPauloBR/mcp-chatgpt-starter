#!/usr/bin/env python3
"""Debug script to examine OAuth client structure."""

import sys
import json
from pathlib import Path

# Try to import MCP and examine client structure
try:
    from mcp.shared.auth import OAuthClientInformationFull
    print("✓ Successfully imported OAuthClientInformationFull")
    print("\nExpected fields:")
    print(f"  {OAuthClientInformationFull.__annotations__}")
    print()
except ImportError as e:
    print(f"✗ Cannot import MCP library: {e}")
    print("  This is expected if running outside the server environment")
    sys.exit(1)

# Load and examine stored client
clients_file = Path(".oauth_data/clients.json")
if not clients_file.exists():
    print("✗ No clients.json found")
    sys.exit(1)

print("Loading stored client data...")
with open(clients_file, 'r') as f:
    data = json.load(f)

for client_id, client_data in data.items():
    print(f"\nStored Client: {client_id}")
    print(f"  Fields in JSON: {list(client_data.keys())}")
    print()
    
    # Try to create the object
    print("Attempting to create OAuthClientInformationFull object...")
    try:
        # Remove None values
        clean_data = {k: v for k, v in client_data.items() if v is not None}
        if 'client_secret_hash' in clean_data and clean_data['client_secret_hash'] is None:
            del clean_data['client_secret_hash']
        
        client_obj = OAuthClientInformationFull(**clean_data)
        print("✓ Successfully created client object")
        print(f"\nClient object attributes:")
        for attr in dir(client_obj):
            if not attr.startswith('_'):
                print(f"  {attr}: {getattr(client_obj, attr, 'N/A')}")
    except Exception as e:
        print(f"✗ Failed to create client object: {e}")
        print(f"\n  Error type: {type(e).__name__}")
        print(f"  Error details: {str(e)}")
