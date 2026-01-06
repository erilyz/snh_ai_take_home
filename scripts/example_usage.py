#!/usr/bin/env python3
"""
Example usage of the HTTP Server Coding Challenge.
Run this after starting the server with: ./run.sh
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")


def main():
    print("🌳 HTTP Server Coding Challenge - Example Usage")
    
    # Health check
    response = requests.get(f"{BASE_URL}/health")
    print_response("1. Health Check", response)
    
    # Get empty trees
    response = requests.get(f"{BASE_URL}/api/tree")
    print_response("2. Get Trees (Empty)", response)
    
    # Create root node
    response = requests.post(
        f"{BASE_URL}/api/tree",
        json={"label": "root"}
    )
    print_response("3. Create Root Node", response)
    root_id = response.json()["id"]

    # Create bear node (child of root)
    response = requests.post(
        f"{BASE_URL}/api/tree",
        json={"label": "bear", "parent_id": root_id}
    )
    print_response("4. Create 'bear' Node (child of root)", response)
    bear_id = response.json()["id"]

    # Create cat node (child of bear)
    response = requests.post(
        f"{BASE_URL}/api/tree",
        json={"label": "cat", "parent_id": bear_id}
    )
    print_response("5. Create 'cat' Node (child of bear)", response)

    # Create another root tree
    response = requests.post(
        f"{BASE_URL}/api/tree",
        json={"label": "another_root"}
    )
    print_response("6. Create Another Root Tree", response)
    
    # Get full tree structure
    response = requests.get(f"{BASE_URL}/api/tree")
    print_response("7. Get Complete Tree Structure", response)
    
    # Try to create node with non-existent parent (error case)
    response = requests.post(
        f"{BASE_URL}/api/tree",
        json={"label": "orphan", "parent_id": 999}
    )
    print_response("8. Error Case - Parent Not Found", response)
    
    print("\n✅ Example completed! Check http://localhost:8000/docs for interactive API documentation.")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server.")
        print("Please start the server first with: ./run.sh")
        print("Then run this script in a new terminal.")

