"""
Test client for the Optical Design Chat API
Run this script to test the backend without a frontend.
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_simple_design():
    """Test generating a simple optical design"""
    print("\n=== Testing Simple Lens Design ===")

    request_data = {
        "user_message": "Design a simple plano-convex lens with 50mm focal length for visible light"
    }

    response = requests.post(
        f"{BASE_URL}/api/design",
        json=request_data,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\n=== Generated Design ===")
        print(json.dumps(result, indent=2))
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_doublet_design():
    """Test generating an achromatic doublet"""
    print("\n=== Testing Achromatic Doublet Design ===")

    request_data = {
        "user_message": "Design an achromatic doublet lens system with 100mm focal length and 25mm diameter for astronomy applications"
    }

    response = requests.post(
        f"{BASE_URL}/api/design",
        json=request_data,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\n=== Generated Design ===")
        print(json.dumps(result, indent=2))
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_with_conversation_history():
    """Test with conversation history for context"""
    print("\n=== Testing With Conversation History ===")

    # First request
    first_request = {
        "user_message": "Design a simple converging lens"
    }

    print("\nFirst request...")
    response1 = requests.post(
        f"{BASE_URL}/api/design",
        json=first_request,
        headers={"Content-Type": "application/json"}
    )

    if response1.status_code != 200:
        print(f"First request failed: {response1.text}")
        return False

    first_result = response1.json()
    print("First design received")

    # Second request with history
    second_request = {
        "user_message": "Now make it shorter focal length and add another lens for chromatic correction",
        "conversation_history": [
            {"role": "user", "content": first_request["user_message"]},
            {"role": "assistant", "content": json.dumps(first_result["design"])}
        ]
    }

    print("\nSecond request with history...")
    response2 = requests.post(
        f"{BASE_URL}/api/design",
        json=second_request,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status: {response2.status_code}")

    if response2.status_code == 200:
        result = response2.json()
        print("\n=== Modified Design ===")
        print(json.dumps(result, indent=2))
        return True
    else:
        print(f"Error: {response2.text}")
        return False


def test_chat_endpoint():
    """Test the chat endpoint"""
    print("\n=== Testing Chat Endpoint ===")

    request_data = {
        "user_message": "Design a microscope objective lens with high numerical aperture"
    }

    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=request_data,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\n=== Chat Response ===")
        print(json.dumps(result, indent=2))
        return True
    else:
        print(f"Error: {response.text}")
        return False


def run_all_tests():
    """Run all test cases"""
    print("=" * 60)
    print("OPTICAL DESIGN CHAT API - TEST SUITE")
    print("=" * 60)

    tests = [
        ("Health Check", test_health_check),
        ("Simple Lens Design", test_simple_design),
        ("Achromatic Doublet Design", test_doublet_design),
        ("Chat Endpoint", test_chat_endpoint),
        ("Conversation History", test_with_conversation_history),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\nTest '{name}' failed with exception: {str(e)}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status}: {name}")

    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n{passed}/{total} tests passed")


if __name__ == "__main__":
    print("\nMake sure the server is running on http://localhost:8000")
    print("Start it with: python app.py\n")

    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server at http://localhost:8000")
        print("Please start the server first: python app.py")
