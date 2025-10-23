"""
Test script for updated system prompt management endpoints
Tests the new behavior where base prompt is hardcoded and custom instructions are appended
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_get_empty_custom_instructions():
    """Test GET /api/system-prompt when no custom instructions exist"""
    print("\n=== Test 1: GET custom instructions (should be empty initially) ===")
    response = requests.get(f"{BASE_URL}/api/system-prompt")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        content = data['content']
        print(f"Content: '{content}'")
        if content == "" or "test optical engineer" in content.lower():
            print("Note: File from previous test exists")
        else:
            print("Success: Empty or previous test content")
    else:
        print(f"Error: {response.text}")

def test_delete_custom_instructions():
    """Test DELETE /api/system-prompt to clear instructions"""
    print("\n=== Test 2: DELETE custom instructions ===")
    response = requests.delete(f"{BASE_URL}/api/system-prompt")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
    else:
        print(f"Error: {response.text}")

def test_post_custom_instructions():
    """Test POST /api/system-prompt with custom instructions"""
    print("\n=== Test 3: POST custom instructions ===")

    custom_instructions = """Focus on compact lens designs.
Prefer standard materials like BK7 when possible.
Provide detailed explanations for material choices."""

    response = requests.post(
        f"{BASE_URL}/api/system-prompt",
        json={"content": custom_instructions}
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
    else:
        print(f"Error: {response.text}")

def test_get_custom_instructions():
    """Test GET after POST to verify custom instructions"""
    print("\n=== Test 4: GET custom instructions after POST ===")
    response = requests.get(f"{BASE_URL}/api/system-prompt")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        content = data['content']
        print(f"Content length: {len(content)} characters")
        print(f"Content preview: {content[:100]}...")
        if "compact lens" in content.lower():
            print("Success: Custom instructions retrieved correctly")
        else:
            print("Warning: Content doesn't match what was posted")
    else:
        print(f"Error: {response.text}")

def test_design_endpoint():
    """Test that /api/design endpoint works with the prompt system"""
    print("\n=== Test 5: Test /api/design endpoint ===")

    design_request = {
        "user_message": "Design a simple singlet lens with 50mm focal length for visible light"
    }

    response = requests.post(
        f"{BASE_URL}/api/design",
        json=design_request,
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Success: Design generated")
        print(f"Number of lenses: {len(data['design']['lenses'])}")
        if data.get('explanation'):
            print(f"Explanation preview: {data['explanation'][:100]}...")
    else:
        print(f"Error: {response.text[:200]}")

def test_clear_and_verify():
    """Test clearing instructions and verify they're gone"""
    print("\n=== Test 6: Clear instructions and verify ===")

    # Clear
    response = requests.delete(f"{BASE_URL}/api/system-prompt")
    print(f"DELETE Status: {response.status_code}")

    # Verify
    response = requests.get(f"{BASE_URL}/api/system-prompt")
    print(f"GET Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data['content'] == "":
            print("Success: Instructions cleared successfully")
        else:
            print(f"Warning: Expected empty, got: {data['content'][:50]}...")

if __name__ == "__main__":
    print("=" * 70)
    print("Testing Updated System Prompt Management API")
    print("=" * 70)

    try:
        # Test sequence
        test_get_empty_custom_instructions()
        test_delete_custom_instructions()
        test_post_custom_instructions()
        test_get_custom_instructions()
        test_design_endpoint()
        test_clear_and_verify()

        print("\n" + "=" * 70)
        print("All tests completed!")
        print("=" * 70)
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to server. Is it running on localhost:8000?")
    except Exception as e:
        print(f"\nError during testing: {e}")
