"""
Test script for system prompt management endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_get_system_prompt():
    """Test GET /api/system-prompt endpoint"""
    print("\n=== Testing GET /api/system-prompt ===")
    response = requests.get(f"{BASE_URL}/api/system-prompt")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Content length: {len(data['content'])} characters")
        print(f"First 100 chars: {data['content'][:100]}...")
    else:
        print(f"Error: {response.text}")
    return response

def test_post_system_prompt():
    """Test POST /api/system-prompt endpoint"""
    print("\n=== Testing POST /api/system-prompt ===")

    test_prompt = """You are a test optical engineer. This is a test system prompt.

Test prompt content goes here with optical design requirements.

IMPORTANT: This is just a test prompt for verification."""

    response = requests.post(
        f"{BASE_URL}/api/system-prompt",
        json={"content": test_prompt}
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
    else:
        print(f"Error: {response.text}")
    return response

def test_get_after_post():
    """Verify the saved prompt can be retrieved"""
    print("\n=== Testing GET after POST ===")
    response = requests.get(f"{BASE_URL}/api/system-prompt")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Retrieved content: {data['content'][:100]}...")
        if "test optical engineer" in data['content'].lower():
            print("✓ Successfully retrieved the saved test prompt!")
        else:
            print("✗ Retrieved content doesn't match saved prompt")
    return response

if __name__ == "__main__":
    print("Testing System Prompt Management API")
    print("=" * 50)

    # Test 1: Get default prompt
    test_get_system_prompt()

    # Test 2: Save new prompt
    test_post_system_prompt()

    # Test 3: Get saved prompt
    test_get_after_post()

    print("\n" + "=" * 50)
    print("Tests completed!")
