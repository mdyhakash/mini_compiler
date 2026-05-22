#!/usr/bin/env python3
"""
Debug script to check AST JSON file
"""

import json
import sys

if len(sys.argv) < 2:
    print("Usage: python3 debug.py ast.json")
    sys.exit(1)

filename = sys.argv[1]

print(f"Reading {filename}...")
with open(filename, 'r') as f:
    content = f.read()

print("\n=== File Contents ===")
print(content[:500])  # First 500 chars
print("\n...")

print("\n=== Trying to parse JSON ===")
try:
    # Try to fix common JSON issues
    content = content.replace(',\n{\"end\": true}\n]', '\n,{\"end\": true}\n]')
    data = json.loads(content)
    print(f"✓ JSON parsed successfully!")
    print(f"  Total items: {len(data)}")
    
    # Count node types
    node_types = {}
    for item in data:
        if 'type' in item:
            node_type = item['type']
            node_types[node_type] = node_types.get(node_type, 0) + 1
    
    print(f"\n=== Node Type Summary ===")
    for node_type, count in sorted(node_types.items()):
        print(f"  {node_type}: {count}")
    
    # Show first few nodes
    print(f"\n=== First 5 Nodes ===")
    for i, item in enumerate(data[:5]):
        print(f"{i}: {item}")
    
except json.JSONDecodeError as e:
    print(f"✗ JSON parsing failed!")
    print(f"  Error: {e}")
    print(f"  Position: line {e.lineno}, column {e.colno}")
    
    # Show context around error
    lines = content.split('\n')
    start = max(0, e.lineno - 3)
    end = min(len(lines), e.lineno + 2)
    print(f"\n=== Context around error ===")
    for i in range(start, end):
        marker = " >>> " if i == e.lineno - 1 else "     "
        print(f"{marker}{i+1}: {lines[i]}")