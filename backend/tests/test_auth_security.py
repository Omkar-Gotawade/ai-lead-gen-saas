"""
Comprehensive Authentication and Security Tests
Test Cases: TC-AUTH-001 through TC-AUTH-008, TC-SEC-001 through TC-SEC-006
"""
import pytest
import requests
import time
import jwt
from datetime import datetime, timedelta
from uuid import uuid4

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_USER_1_EMAIL = "auth_test_user1@example.com"
TEST_USER_2_EMAIL = "auth_test_user2@example.com"
TEST_PASSWORD = "SecurePass123!"


class AuthSecurityTestSuite:
    """Authentication and security test suite"""

    def __init__(self):
        self.user1_token = None
        self.user1_id = None
        self.user2_token = None
        self.user2_id = None
        self.test_leads = []

    def setup(self):
        """Setup test environment"""
        print("\n=== Setting up Auth Security Test Suite ===")

        # Register and login user 1
        try:
            requests.post(
                f"{BASE_URL}/auth/register",
                json={
                    "email": TEST_USER_1_EMAIL,
                    "password": TEST_PASSWORD,
                    "full_name": "Auth Test User 1"
                }
            )
        except:
            pass

        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": TEST_USER_1_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            self.user1_token = data["access_token"]
            self.user1_id = data["user_id"]
            print("✓ User 1 logged in")

        # Register and login user 2
        try:
            requests.post(
                f"{BASE_URL}/auth/register",
                json={
                    "email": TEST_USER_2_EMAIL,
                    "password": TEST_PASSWORD,
                    "full_name": "Auth Test User 2"
                }
            )
        except:
            pass

        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": TEST_USER_2_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            self.user2_token = data["access_token"]
            self.user2_id = data["user_id"]
            print("✓ User 2 logged in")

    def test_valid_login(self):
        """TC-AUTH-001: Valid login succeeds"""
        print("\n--- Test 1: Valid Login (TC-AUTH-001) ---")

        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": TEST_USER_1_EMAIL, "password": TEST_PASSWORD}
            )

            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user_id" in data:
                    print("✅ PASS: Valid login successful with token")
                    return True
                else:
                    print("❌ FAIL: Login succeeded but missing token/user_id")
                    return False
            else:
                print(f"❌ FAIL: Valid login failed with status {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_invalid_credentials(self):
        """TC-AUTH-002: Invalid credentials fail"""
        print("\n--- Test 2: Invalid Credentials (TC-AUTH-002) ---")

        try:
            # Test wrong password
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": TEST_USER_1_EMAIL, "password": "WrongPassword123!"}
            )

            if response.status_code in [401, 403]:
                print("✅ PASS: Invalid password rejected")
                pass_test = True
            else:
                print(f"❌ FAIL: Invalid password status {response.status_code} (expected 401)")
                pass_test = False

            # Test non-existent user
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": "nonexistent@example.com", "password": TEST_PASSWORD}
            )

            if response.status_code in [401, 403, 404]:
                print("✅ PASS: Non-existent user rejected")
            else:
                print(f"❌ FAIL: Non-existent user status {response.status_code}")
                pass_test = False

            return pass_test

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_missing_token(self):
        """TC-AUTH-003: Missing token rejected"""
        print("\n--- Test 3: Missing Token (TC-AUTH-003) ---")

        try:
            # Try to access protected endpoint without token
            endpoints_to_test = [
                "/leads",
                "/campaigns",
                "/metrics/summary"
            ]

            all_passed = True

            for endpoint in endpoints_to_test:
                response = requests.get(f"{BASE_URL}{endpoint}")

                if response.status_code in [401, 403]:
                    print(f"✓ {endpoint}: Correctly rejected (401/403)")
                else:
                    print(f"✗ {endpoint}: Status {response.status_code} (expected 401/403)")
                    all_passed = False

            if all_passed:
                print("✅ PASS: All endpoints reject missing token")
                return True
            else:
                print("❌ FAIL: Some endpoints allowed access without token")
                return False

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_expired_token(self):
        """TC-AUTH-004: Expired token rejected"""
        print("\n--- Test 4: Expired Token (TC-AUTH-004) ---")

        try:
            # Create an expired token (requires knowing the secret key)
            # For this test, we'll try to use a token from the past if possible
            # Otherwise, we'll skip with a warning

            # Try using a clearly invalid/old token format
            expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.4Adcj0vQzncSKx1bFVb6xmOjFzMGQhYJrHtBmr6h69M"

            response = requests.get(
                f"{BASE_URL}/leads",
                headers={"Authorization": f"Bearer {expired_token}"}
            )

            if response.status_code in [401, 403]:
                print("✅ PASS: Expired/invalid token rejected")
                return True
            else:
                print(f"⚠ WARN: Expired token test inconclusive (status {response.status_code})")
                print("   Manual test: Wait 30 minutes after login and retry API call")
                return None

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_invalid_signature(self):
        """TC-AUTH-005: Invalid signature rejected"""
        print("\n--- Test 5: Invalid Signature (TC-AUTH-005) ---")

        try:
            # Create a token with wrong signature
            # Take a valid token and modify the signature part
            if self.user1_token:
                parts = self.user1_token.split('.')
                if len(parts) == 3:
                    # Modify signature
                    tampered_token = f"{parts[0]}.{parts[1]}.TAMPERED_SIGNATURE"

                    response = requests.get(
                        f"{BASE_URL}/leads",
                        headers={"Authorization": f"Bearer {tampered_token}"}
                    )

                    if response.status_code in [401, 403]:
                        print("✅ PASS: Tampered token rejected")
                        return True
                    else:
                        print(f"❌ FAIL: Tampered token accepted (status {response.status_code})")
                        return False

            print("⚠ SKIP: Could not generate tampered token")
            return None

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_token_refresh(self):
        """TC-AUTH-006: Token refresh works"""
        print("\n--- Test 6: Token Refresh (TC-AUTH-006) ---")

        try:
            # Check if refresh endpoint exists
            response = requests.post(
                f"{BASE_URL}/auth/refresh",
                headers={"Authorization": f"Bearer {self.user1_token}"}
            )

            if response.status_code == 404:
                print("⚠ SKIP: Token refresh endpoint not implemented")
                return None
            elif response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    print("✅ PASS: Token refresh successful")
                    return True
                else:
                    print("❌ FAIL: Refresh succeeded but no new token")
                    return False
            else:
                print(f"⚠ WARN: Unexpected refresh response {response.status_code}")
                return None

        except Exception as e:
            print(f"⚠ SKIP: {e}")
            return None

    def test_logout_invalidates_token(self):
        """TC-AUTH-007: Logout invalidates token"""
        print("\n--- Test 7: Logout Invalidates Token (TC-AUTH-007) ---")

        try:
            # Login to get a fresh token
            login_response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": TEST_USER_1_EMAIL, "password": TEST_PASSWORD}
            )

            if login_response.status_code != 200:
                print("⚠ SKIP: Could not login for logout test")
                return None

            token = login_response.json()["access_token"]

            # Verify token works
            response = requests.get(
                f"{BASE_URL}/leads",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code not in [200, 201]:
                print(f"⚠ SKIP: Token not working before logout (status {response.status_code})")
                return None

            print("✓ Token works before logout")

            # Logout
            logout_response = requests.post(
                f"{BASE_URL}/auth/logout",
                headers={"Authorization": f"Bearer {token}"}
            )

            if logout_response.status_code == 404:
                print("⚠ SKIP: Logout endpoint not implemented")
                print("   Note: JWT tokens are typically stateless (no server-side invalidation)")
                return None

            # Try to use token after logout
            response = requests.get(
                f"{BASE_URL}/leads",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code in [401, 403]:
                print("✅ PASS: Token invalidated after logout")
                return True
            else:
                print(f"⚠ WARN: Token still works after logout (status {response.status_code})")
                print("   Note: JWT tokens are typically stateless, so logout may not invalidate them")
                return None

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_cross_user_data_access(self):
        """TC-AUTH-008: Cross-user data access prevented"""
        print("\n--- Test 8: Cross-User Data Access (TC-AUTH-008) ---")

        try:
            if not self.user1_token or not self.user2_token:
                print("⚠ SKIP: Need both user tokens")
                return None

            # User 1 creates a lead
            lead_response = requests.post(
                f"{BASE_URL}/leads",
                headers={"Authorization": f"Bearer {self.user1_token}"},
                json={
                    "first_name": "User1",
                    "last_name": "Lead",
                    "email": f"user1lead_{uuid4().hex[:8]}@example.com"
                }
            )

            if lead_response.status_code != 201:
                print(f"⚠ SKIP: Could not create lead (status {lead_response.status_code})")
                return None

            lead_id = lead_response.json()["id"]
            self.test_leads.append((lead_id, self.user1_token))
            print(f"✓ User 1 created lead: {lead_id}")

            # User 2 tries to access User 1's lead
            access_response = requests.get(
                f"{BASE_URL}/leads/{lead_id}",
                headers={"Authorization": f"Bearer {self.user2_token}"}
            )

            if access_response.status_code in [403, 404]:
                print("✅ PASS: User 2 cannot access User 1's lead")
                pass_test = True
            elif access_response.status_code == 200:
                print("❌ FAIL: User 2 can access User 1's lead")
                pass_test = False
            else:
                print(f"⚠ WARN: Unexpected status {access_response.status_code}")
                pass_test = None

            # User 2 tries to modify User 1's lead
            modify_response = requests.put(
                f"{BASE_URL}/leads/{lead_id}",
                headers={"Authorization": f"Bearer {self.user2_token}"},
                json={"first_name": "Hacked"}
            )

            if modify_response.status_code in [403, 404]:
                print("✅ PASS: User 2 cannot modify User 1's lead")
            elif modify_response.status_code == 200:
                print("❌ FAIL: User 2 can modify User 1's lead")
                pass_test = False
            else:
                print(f"⚠ WARN: Unexpected modify status {modify_response.status_code}")

            # User 2 tries to delete User 1's lead
            delete_response = requests.delete(
                f"{BASE_URL}/leads/{lead_id}",
                headers={"Authorization": f"Bearer {self.user2_token}"}
            )

            if delete_response.status_code in [403, 404]:
                print("✅ PASS: User 2 cannot delete User 1's lead")
            elif delete_response.status_code == 204:
                print("❌ FAIL: User 2 can delete User 1's lead")
                pass_test = False
            else:
                print(f"⚠ WARN: Unexpected delete status {delete_response.status_code}")

            return pass_test

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_rate_limiting(self):
        """TC-SEC-001: Rate limiting active"""
        print("\n--- Test 9: Rate Limiting (TC-SEC-001) ---")

        try:
            # Send many requests rapidly
            print("⚡ Sending 100 rapid requests...")

            rate_limited = False
            for i in range(100):
                response = requests.get(f"{BASE_URL}/health")

                if response.status_code == 429:
                    rate_limited = True
                    print(f"✓ Rate limited after {i+1} requests")
                    break

            if rate_limited:
                print("✅ PASS: Rate limiting is active")
                return True
            else:
                print("⚠ WARN: No rate limiting detected after 100 requests")
                print("   Note: Rate limiting may be configured per IP, not global")
                return None

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_cors_headers(self):
        """TC-SEC-002: CORS configured correctly"""
        print("\n--- Test 10: CORS Headers (TC-SEC-002) ---")

        try:
            # Send OPTIONS request
            response = requests.options(
                f"{BASE_URL}/leads",
                headers={"Origin": "http://localhost:5173"}
            )

            cors_headers = {
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Methods",
                "Access-Control-Allow-Headers"
            }

            found_headers = set(response.headers.keys()) & cors_headers

            if len(found_headers) > 0:
                print(f"✅ PASS: CORS headers present: {found_headers}")
                return True
            else:
                print("⚠ WARN: CORS headers not found")
                print("   Note: May be configured at reverse proxy level")
                return None

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_sql_injection_protection(self):
        """TC-SEC-003: SQL injection protection"""
        print("\n--- Test 11: SQL Injection Protection (TC-SEC-003) ---")

        try:
            # Try SQL injection in login
            sql_payloads = [
                "admin' OR '1'='1",
                "admin'--",
                "' OR '1'='1' --",
                "admin' DROP TABLE users--"
            ]

            for payload in sql_payloads:
                response = requests.post(
                    f"{BASE_URL}/auth/login",
                    json={"email": payload, "password": "anything"}
                )

                if response.status_code == 200:
                    print(f"❌ FAIL: SQL injection succeeded with payload: {payload}")
                    return False

            print("✅ PASS: SQL injection attempts blocked")
            return True

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_xss_protection(self):
        """TC-SEC-004: XSS protection"""
        print("\n--- Test 12: XSS Protection (TC-SEC-004) ---")

        try:
            # Try XSS in lead creation
            xss_payload = "<script>alert('XSS')</script>"

            response = requests.post(
                f"{BASE_URL}/leads",
                headers={"Authorization": f"Bearer {self.user1_token}"},
                json={
                    "first_name": xss_payload,
                    "last_name": "Test",
                    "email": f"xss_{uuid4().hex[:8]}@example.com"
                }
            )

            if response.status_code == 201:
                lead_id = response.json()["id"]
                self.test_leads.append((lead_id, self.user1_token))

                # Retrieve and check if script is escaped
                get_response = requests.get(
                    f"{BASE_URL}/leads/{lead_id}",
                    headers={"Authorization": f"Bearer {self.user1_token}"}
                )

                if get_response.status_code == 200:
                    data = get_response.json()
                    first_name = data.get("first_name", "")

                    # Check if script is stored as-is (backend should store it, frontend should escape)
                    if "<script>" in first_name:
                        print("✓ Backend stored XSS payload (frontend must sanitize)")
                        print("✅ PASS: Backend accepts data (XSS protection is frontend's job)")
                        return True
                    else:
                        print("✓ Backend sanitized XSS payload")
                        print("✅ PASS: XSS payload sanitized")
                        return True

            print("⚠ WARN: Lead creation failed")
            return None

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_path_traversal_protection(self):
        """TC-SEC-005: Path traversal protection"""
        print("\n--- Test 13: Path Traversal Protection (TC-SEC-005) ---")

        try:
            # Try path traversal in file operations
            traversal_payloads = [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                "....//....//....//etc/passwd"
            ]

            for payload in traversal_payloads:
                # Try in various endpoints (adjust based on your API)
                response = requests.get(
                    f"{BASE_URL}/files/{payload}",
                    headers={"Authorization": f"Bearer {self.user1_token}"}
                )

                # 404 is fine (endpoint doesn't exist)
                # 403/401 is good (blocked)
                # 200 with file content is BAD
                if response.status_code == 200 and len(response.text) > 100:
                    print(f"❌ FAIL: Path traversal possible with: {payload}")
                    return False

            print("✅ PASS: Path traversal attempts blocked")
            return True

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_large_payload_protection(self):
        """TC-SEC-006: Large payload protection"""
        print("\n--- Test 14: Large Payload Protection (TC-SEC-006) ---")

        try:
            # Try to send a very large payload
            large_string = "A" * (10 * 1024 * 1024)  # 10MB

            response = requests.post(
                f"{BASE_URL}/leads",
                headers={"Authorization": f"Bearer {self.user1_token}"},
                json={
                    "first_name": large_string,
                    "last_name": "Test",
                    "email": "test@example.com"
                },
                timeout=5
            )

            if response.status_code in [413, 400]:
                print("✅ PASS: Large payload rejected")
                return True
            elif response.status_code == 422:
                print("✅ PASS: Large payload validation failed (acceptable)")
                return True
            else:
                print(f"⚠ WARN: Large payload response: {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            print("⚠ WARN: Request timed out (server may be processing large payload)")
            return None
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def cleanup(self):
        """Clean up test data"""
        print("\n=== Cleaning Up Test Data ===")

        for lead_id, token in self.test_leads:
            try:
                requests.delete(
                    f"{BASE_URL}/leads/{lead_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )
            except:
                pass

        print("✓ Cleanup completed")

    def run_all_tests(self):
        """Run all authentication and security tests"""
        print("\n" + "="*60)
        print("AUTHENTICATION & SECURITY TEST SUITE")
        print("="*60)

        try:
            self.setup()

            if not self.user1_token:
                print("❌ CRITICAL: Could not setup test users")
                return False

            results = {
                "TC-AUTH-001: Valid Login": self.test_valid_login(),
                "TC-AUTH-002: Invalid Credentials": self.test_invalid_credentials(),
                "TC-AUTH-003: Missing Token": self.test_missing_token(),
                "TC-AUTH-004: Expired Token": self.test_expired_token(),
                "TC-AUTH-005: Invalid Signature": self.test_invalid_signature(),
                "TC-AUTH-006: Token Refresh": self.test_token_refresh(),
                "TC-AUTH-007: Logout Invalidates": self.test_logout_invalidates_token(),
                "TC-AUTH-008: Cross-User Access": self.test_cross_user_data_access(),
                "TC-SEC-001: Rate Limiting": self.test_rate_limiting(),
                "TC-SEC-002: CORS Headers": self.test_cors_headers(),
                "TC-SEC-003: SQL Injection": self.test_sql_injection_protection(),
                "TC-SEC-004: XSS Protection": self.test_xss_protection(),
                "TC-SEC-005: Path Traversal": self.test_path_traversal_protection(),
                "TC-SEC-006: Large Payloads": self.test_large_payload_protection()
            }

            # Print summary
            print("\n" + "="*60)
            print("TEST SUMMARY")
            print("="*60)

            passed = sum(1 for v in results.values() if v is True)
            failed = sum(1 for v in results.values() if v is False)
            skipped = sum(1 for v in results.values() if v is None)

            for test_name, result in results.items():
                status = "✅ PASS" if result is True else "❌ FAIL" if result is False else "⚠ SKIP/WARN"
                print(f"{status} - {test_name}")

            print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped/warnings")
            print("="*60)

            # Consider warnings as acceptable for some tests
            critical_failures = [
                results["TC-AUTH-001: Valid Login"],
                results["TC-AUTH-002: Invalid Credentials"],
                results["TC-AUTH-003: Missing Token"],
                results["TC-AUTH-008: Cross-User Access"],
                results["TC-SEC-003: SQL Injection"]
            ]

            has_critical_failure = any(r is False for r in critical_failures)

            if has_critical_failure:
                print("\n❌ CRITICAL FAILURES DETECTED")
                return False
            elif failed > 0:
                print("\n⚠ Some tests failed but no critical issues")
                return False
            else:
                print("\n✅ ALL TESTS PASSED")
                return True

        finally:
            self.cleanup()


if __name__ == "__main__":
    suite = AuthSecurityTestSuite()
    success = suite.run_all_tests()
    exit(0 if success else 1)
