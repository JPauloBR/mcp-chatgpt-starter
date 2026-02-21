#!/usr/bin/env python3
"""Test script to verify OAuth client data loads correctly."""

import sys
import json
from pathlib import Path

# Test loading the clients.json file
clients_file = Path(".oauth_data/clients.json")

if not clients_file.exists():
    print("✗ clients.json not found")
    sys.exit(1)

print("Testing client data loading...")
print("=" * 50)

with open(clients_file, 'r') as f:
    data = json.load(f)

for client_id, client_data in data.items():
    print(f"\nClient ID: {client_id}")
    print(f"  Name: {client_data.get('client_name')}")
    print(f"  Redirect URIs: {client_data.get('redirect_uris')}")
    print(f"  Grant Types: {client_data.get('grant_types')}")
    
    # Check for problematic fields
    if 'client_secret_hash' in client_data:
        if client_data['client_secret_hash'] is None:
            print(f"  ✗ client_secret_hash is null (WILL CAUSE ISSUES)")
        else:
            print(f"  ✓ client_secret_hash is present")
    else:
        print(f"  ✓ client_secret_hash not present (OK)")
    
    # Verify all required fields
    required_fields = ['client_id', 'client_name', 'redirect_uris', 'grant_types']
    missing = [f for f in required_fields if f not in client_data]
    
    if missing:
        print(f"  ✗ Missing required fields: {missing}")
    else:
        print(f"  ✓ All required fields present")

print("\n" + "=" * 50)
print("✓ Client data validation complete!")
