"""FastForm API Testing Suite

This script provides comprehensive testing for all FastForm APIs in logical order:

1. User Management APIs - Create, read, update, delete users
2. Annotation Management APIs - Create, read, update, delete form templates
3. FastFormBuild APIs - Parse forms and create templates with AI
4. FastFill APIs - Fill existing forms with user data
5. Error Handling & Edge Cases - Test various failure scenarios
"""

import json
import time
import uuid
import sys
import os
import base64
import requests
import pprint
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))

try:
    from app.config import APIKeys
    import pymupdf
except ImportError as e:
    print(f"Warning: Could not import required modules: {e}")
    print("Some tests may be skipped if dependencies are missing")

LOCAL_BASE_URL = "http://localhost:8000"
PRODUCTION_BASE_URL = (
    "https://fastform.jollydune-3875217e.westus2.azurecontainerapps.io"
)

USE_PRODUCTION = False
BASE_URL = PRODUCTION_BASE_URL if USE_PRODUCTION else LOCAL_BASE_URL

print(f"Testing against: {BASE_URL}")


# Test data generators
def generate_test_user_id():
    """Generate a unique test user ID"""
    return f"test_user_{uuid.uuid4().hex[:8]}"


def generate_test_annotation_name():
    """Generate a unique test annotation name"""
    return f"test_form_{uuid.uuid4().hex[:8]}"


# Common headers
HEADERS = {"accept": "application/json", "Content-Type": "application/json"}


# Helper function for API calls
def make_request(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    expected_status: Optional[int] = None,
) -> Tuple[int, Any]:
    """Make an API request and return response with error handling"""
    url = f"{BASE_URL}/v1{endpoint}"
    print(f"\n{method.upper()} {url}")

    if data:
        print(f"Request Data: {json.dumps(data, indent=2)}")

    if method.lower() == "get":
        response = requests.get(url, headers=HEADERS)
    elif method.lower() == "post":
        response = requests.post(url, headers=HEADERS, json=data)
    elif method.lower() == "put":
        response = requests.put(url, headers=HEADERS, json=data)
    elif method.lower() == "delete":
        response = requests.delete(url, headers=HEADERS)

    print(f"Status: {response.status_code}")

    if expected_status and response.status_code != expected_status:
        print(f"Expected status {expected_status}, got {response.status_code}")
    elif expected_status and response.status_code == expected_status:
        print(f"Status matches expected {expected_status}")

    try:
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        return response.status_code, response_data
    except Exception as e:
        print(f"Response: {response.text}, {e}")
        return response.status_code, response.text


class FastFormAPITester:
    """Comprehensive API testing class for FastForm"""

    def __init__(self):
        self.created_user_id = None
        self.created_annotation_id = None
        self.fastformbuild_thread_id = None
        self.fastfill_thread_id = None
        self.test_results = []

    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }
        self.test_results.append(result)
        status = "PASS" if success else "FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"  Details: {details}")

    def test_api_root(self):
        """Test API Root Endpoint"""
        print("\nTesting API Root Endpoint")

        status, response = make_request("GET", "/", expected_status=200)
        success = status == 200 and "FastForm API" in str(response)
        self.log_test_result("API Root Endpoint", success)
        return success

    def test_user_management(self):
        """Test User Management APIs"""
        print("\nTesting User Management APIs")

        # 1.1 Create User API Test
        print("Testing User Creation")
        test_user_id = generate_test_user_id()
        user_data = {"id": test_user_id, "email": f"{test_user_id}@example.com"}

        status, response = make_request("POST", "/user", user_data, expected_status=201)
        success = (
            status == 201
            and response.get("id") == test_user_id
            and response.get("email") == user_data["email"]
        )
        self.log_test_result("Create User", success)

        if success:
            self.created_user_id = response["id"]
            print(f"User created successfully with ID: {test_user_id}")
        else:
            return False

        # 1.2 Get User API Test
        print("Testing User Retrieval")
        status, response = make_request(
            "GET", f"/user/{self.created_user_id}", expected_status=200
        )
        success = (
            status == 200
            and response.get("id") == self.created_user_id
            and response.get("email") == user_data["email"]
        )
        self.log_test_result("Get User", success)

        # 1.3 Update User API Test
        print("Testing User Update")
        updated_email = f"updated_{self.created_user_id}@example.com"
        update_data = {"id": self.created_user_id, "email": updated_email}

        status, response = make_request(
            "PUT", f"/user/{self.created_user_id}", update_data, expected_status=200
        )
        success = (
            status == 200
            and response.get("id") == self.created_user_id
            and response.get("email") == updated_email
        )
        self.log_test_result("Update User", success)

        return True

    def test_annotation_management(self):
        """Test Annotation Management APIs"""
        print("\nTesting Annotation Management APIs")

        if not self.created_user_id:
            print("Skipping annotation tests - no user created")
            return False

        # 2.1 Create Annotation API Test
        print("Testing Annotation Creation")
        annotation_name = generate_test_annotation_name()
        sample_form_structure = {
            "title": "Sample Contact Form",
            "description": "A simple contact form for testing",
            "elements": [
                {
                    "title": "Full Name",
                    "description": "User's full name",
                    "bbox": [{"x": None, "y": None}, {"x": None, "y": None}],
                    "element_name": "TextField",
                    "value": None,
                },
                {
                    "title": "Email",
                    "description": "User's email address",
                    "bbox": [{"x": None, "y": None}, {"x": None, "y": None}],
                    "element_name": "TextField",
                    "value": None,
                },
                {
                    "title": "Message",
                    "description": "User's message",
                    "bbox": [{"x": None, "y": None}, {"x": None, "y": None}],
                    "element_name": "TextAreaField",
                    "value": None,
                },
            ],
        }

        annotation_data = {
            "name": annotation_name,
            "description": "Test annotation for API testing",
            "structure": json.dumps(sample_form_structure),
            "user_id": self.created_user_id,
        }

        status, response = make_request(
            "POST", "/annotation", annotation_data, expected_status=201
        )
        success = (
            status == 201
            and response.get("name") == annotation_name
            and response.get("user_id") == self.created_user_id
        )
        self.log_test_result("Create Annotation", success)

        if success:
            self.created_annotation_id = response["id"]
            print(f"Annotation created successfully with ID: {response['id']}")
        else:
            return False

        # 2.2 Get Annotation API Test
        print("Testing Annotation Retrieval")
        status, response = make_request(
            "GET", f"/annotation/{self.created_annotation_id}", expected_status=200
        )
        success = (
            status == 200
            and response.get("id") == self.created_annotation_id
            and response.get("name") == annotation_name
        )
        self.log_test_result("Get Annotation", success)

        # 2.3 List Annotations by User API Test
        print("Testing Annotation Listing by User")
        status, response = make_request(
            "GET", f"/annotation?user_id={self.created_user_id}", expected_status=200
        )
        success = status == 200 and isinstance(response, list) and len(response) >= 1
        self.log_test_result("List Annotations by User", success)

        # 2.4 Update Annotation API Test (Known to have issues)
        print("Testing Annotation Update")
        updated_name = f"updated_{annotation_name}"
        updated_description = "Updated test annotation description"

        updated_structure = sample_form_structure.copy()
        updated_structure["elements"].append(
            {
                "title": "Phone Number",
                "description": "User's phone number",
                "bbox": [{"x": None, "y": None}, {"x": None, "y": None}],
                "element_name": "PhoneField",
                "value": None,
            }
        )

        update_data = {
            "id": self.created_annotation_id,
            "name": updated_name,
            "description": updated_description,
            "structure": json.dumps(updated_structure),
        }

        status, response = make_request(
            "PUT",
            f"/annotation/{self.created_annotation_id}",
            update_data,
            expected_status=200,
        )
        # Note: This is known to fail with 500 error due to service method signature issue
        success = status == 200
        self.log_test_result(
            "Update Annotation",
            success,
            "Known issue: Service method signature mismatch causes 500 error",
        )

        return True

    def test_fastformbuild_apis(self):
        """Test FastFormBuild APIs"""
        print("\nTesting FastFormBuild APIs")

        if not self.created_user_id:
            print("Skipping FastFormBuild tests - no user created")
            return False

        # 3.1 FastFormBuild Chat API Test (with form image)
        print("Testing FastFormBuild Chat with Form Image")

        try:
            # Load and process the form image
            doc = pymupdf.open("../sample/multiple-listing.pdf")
            page = doc[0]
            page_bytes = page.get_pixmap().tobytes()
            page_b64 = base64.b64encode(page_bytes).decode("utf-8")
            doc.close()
        except Exception as e:
            print(f"Warning: Could not load PDF file: {e}")
            # Use a dummy base64 string for testing
            page_b64 = "dummy_base64_string_for_testing"

        self.fastformbuild_thread_id = f"test_thread_{uuid.uuid4().hex[:8]}"
        fastformbuild_data = {
            "message_data": {
                "thread_id": self.fastformbuild_thread_id,
                "user_id": self.created_user_id,
                "content": "Convert this form to a structured schema with all visible fields",
            },
            "form_pages": [page_b64],
        }

        status, response = make_request(
            "POST", "/fastformbuild/chat", fastformbuild_data, expected_status=200
        )
        success = (
            status == 200
            and "id" in response
            and "content" in response
            and response.get("thread_id") == self.fastformbuild_thread_id
            and response.get("user_id") == self.created_user_id
        )
        self.log_test_result("FastFormBuild Chat with Image", success)

        if success:
            print(
                f"FastFormBuild chat successful, thread: {self.fastformbuild_thread_id}"
            )
            print(f"Message ID: {response['id']}")

        # 3.2 FastFormBuild Follow-up Chat (without image)
        print("Testing FastFormBuild Follow-up Chat")
        followup_data = {
            "message_data": {
                "thread_id": self.fastformbuild_thread_id,
                "user_id": self.created_user_id,
                "content": "Please add validation rules and make the date fields more specific",
            }
        }

        status, response = make_request(
            "POST", "/fastformbuild/chat", followup_data, expected_status=200
        )
        success = (
            status == 200
            and response.get("thread_id") == self.fastformbuild_thread_id
            and response.get("user_id") == self.created_user_id
        )
        self.log_test_result("FastFormBuild Follow-up Chat", success)

        # 3.3 Get FastFormBuild Threads by User
        print("Testing FastFormBuild Thread Listing")
        status, response = make_request(
            "GET", f"/fastformbuild/threads/{self.created_user_id}", expected_status=200
        )
        success = status == 200 and isinstance(response, list)
        self.log_test_result("Get FastFormBuild Threads", success)

        if success:
            print(f"Found {len(response)} thread(s) for user {self.created_user_id}")

        # 3.4 Get FastFormBuild Thread History
        print("Testing FastFormBuild Thread History")
        if self.fastformbuild_thread_id:
            status, response = make_request(
                "GET",
                f"/fastformbuild/threads/{self.fastformbuild_thread_id}/history",
                expected_status=200,
            )
            success = status == 200 and isinstance(response, list)
            self.log_test_result("Get FastFormBuild Thread History", success)

            if success:
                print(
                    f"Found {len(response)} message(s) in thread {self.fastformbuild_thread_id}"
                )

        return True

    def test_fastfill_apis(self):
        """Test FastFill APIs"""
        print("\nTesting FastFill APIs")

        if not self.created_user_id or not self.created_annotation_id:
            print("Skipping FastFill tests - missing user or annotation")
            return False

        # 4.1 FastFill Chat API Test
        print("Testing FastFill Chat")
        self.fastfill_thread_id = f"fastfill_thread_{uuid.uuid4().hex[:8]}"
        fastfill_data = {
            "content": "Please fill this form with sample data: Name: John Doe, Email: john.doe@example.com, Message: Hello, this is a test message for the contact form.",
            "thread_id": self.fastfill_thread_id,
            "user_id": self.created_user_id,
            "load_annotation_id": self.created_annotation_id,
        }

        status, response = make_request(
            "POST", "/fastfill/chat", fastfill_data, expected_status=200
        )
        success = (
            status == 200
            and "id" in response
            and "content" in response
            and response.get("thread_id") == self.fastfill_thread_id
            and response.get("user_id") == self.created_user_id
        )
        self.log_test_result("FastFill Chat", success)

        if success:
            print(f"FastFill chat successful, thread: {self.fastfill_thread_id}")
            print(f"Message ID: {response['id']}")

        # 4.2 Get FastFill Threads by User
        print("Testing FastFill Thread Listing")
        status, response = make_request(
            "GET", f"/fastfill/threads/{self.created_user_id}", expected_status=200
        )
        success = status == 200 and isinstance(response, list)
        self.log_test_result("Get FastFill Threads", success)

        if success:
            print(
                f"Found {len(response)} FastFill thread(s) for user {self.created_user_id}"
            )

        # 4.3 Get FastFill Thread History
        print("Testing FastFill Thread History")
        if self.fastfill_thread_id:
            status, response = make_request(
                "GET",
                f"/fastfill/threads/{self.fastfill_thread_id}/history",
                expected_status=200,
            )
            success = status == 200 and isinstance(response, list)
            self.log_test_result("Get FastFill Thread History", success)

            if success:
                print(
                    f"Found {len(response)} message(s) in FastFill thread {self.fastfill_thread_id}"
                )

        return True

    def test_error_handling(self):
        """Test Error Handling & Edge Cases"""
        print("\nTesting Error Handling & Edge Cases")

        # 5.1 Test Non-existent User Retrieval
        print("Testing Non-existent User Retrieval")
        non_existent_user_id = "non_existent_user_12345"
        status, response = make_request(
            "GET", f"/user/{non_existent_user_id}", expected_status=404
        )
        success = status == 404
        self.log_test_result("Non-existent User Retrieval", success)

        # 5.2 Test Non-existent Annotation Retrieval
        print("Testing Non-existent Annotation Retrieval")
        non_existent_annotation_id = 99999
        status, response = make_request(
            "GET", f"/annotation/{non_existent_annotation_id}", expected_status=404
        )
        success = status == 404
        self.log_test_result("Non-existent Annotation Retrieval", success)

        # 5.3 Test Invalid User Creation (missing required fields)
        print("Testing Invalid User Creation")
        invalid_user_data = {"email": "invalid@example.com"}  # Missing 'id' field
        status, response = make_request(
            "POST", "/user", invalid_user_data, expected_status=422
        )
        success = status == 422
        self.log_test_result("Invalid User Creation", success)

        # 5.4 Test Duplicate User Creation
        print("Testing Duplicate User Creation")
        if self.created_user_id:
            duplicate_user_data = {
                "id": self.created_user_id,  # This user already exists
                "email": "duplicate@example.com",
            }
            status, response = make_request(
                "POST", "/user", duplicate_user_data, expected_status=400
            )
            success = status in [400, 409]
            self.log_test_result("Duplicate User Creation", success)

        return True

    def cleanup(self):
        """Cleanup created resources"""
        print("\nCleanup - Deleting Created Resources")

        # Delete Annotation
        if self.created_annotation_id:
            print("Testing Annotation Deletion")
            status, response = make_request(
                "DELETE",
                f"/annotation/{self.created_annotation_id}",
                expected_status=204,
            )
            success = status == 204
            self.log_test_result("Delete Annotation", success)

            # Verify annotation is deleted
            if success:
                status, response = make_request(
                    "GET",
                    f"/annotation/{self.created_annotation_id}",
                    expected_status=404,
                )
                success = status == 404
                self.log_test_result("Verify Annotation Deletion", success)

        # Delete User (Known to have issues)
        if self.created_user_id:
            print("Testing User Deletion")
            status, response = make_request(
                "DELETE", f"/user/{self.created_user_id}", expected_status=204
            )
            # Note: This is known to fail with 500 error due to foreign key constraints
            success = status == 204
            self.log_test_result(
                "Delete User",
                success,
                "Known issue: Foreign key constraint violation causes 500 error",
            )

            # Verify user is deleted
            if success:
                status, response = make_request(
                    "GET", f"/user/{self.created_user_id}", expected_status=404
                )
                success = status == 404
                self.log_test_result("Verify User Deletion", success)

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("FASTFORM API TEST SUMMARY")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests / total_tests) * 100:.1f}%")

        print("\nDetailed Results:")
        for result in self.test_results:
            status = "PASS" if result["success"] else "FAIL"
            print(f"  {status}: {result['test_name']}")
            if result["details"]:
                print(f"    Note: {result['details']}")

        print("\nKnown Issues:")
        print(
            "  1. Annotation Update API (PUT /v1/annotation/{id}) - 500 Internal Server Error"
        )
        print("     Cause: Service method signature mismatch")
        print(
            "  2. User Deletion API (DELETE /v1/user/{id}) - 500 Internal Server Error"
        )
        print("     Cause: Foreign key constraint violation when user has messages")

        print("\nOverall Assessment:")
        if passed_tests >= total_tests * 0.8:
            print("  EXCELLENT: Most APIs working correctly")
        elif passed_tests >= total_tests * 0.6:
            print("  GOOD: Core functionality working, some issues to address")
        else:
            print("  NEEDS ATTENTION: Multiple critical issues found")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("Starting FastForm API Test Suite")
        print(f"Testing against: {BASE_URL}")

        # Run tests in logical order
        self.test_api_root()
        self.test_user_management()
        self.test_annotation_management()
        self.test_fastformbuild_apis()
        self.test_fastfill_apis()
        self.test_error_handling()
        self.cleanup()
        self.print_summary()


def main():
    """Main function to run the test suite"""
    tester = FastFormAPITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
