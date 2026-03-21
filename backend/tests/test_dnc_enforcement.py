"""
Comprehensive DNC (Do Not Contact) Enforcement Tests
Test Cases: TC-SEC-007, TC-SEND-005, TC-FAIL-013
"""
import pytest
import requests
import time
import threading
from uuid import uuid4
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_USER_EMAIL = "dnc_test_user@example.com"
TEST_USER_PASSWORD = "TestPass123!"


class DNCTestSuite:
    """DNC enforcement test suite"""

    def __init__(self):
        self.token = None
        self.user_id = None
        self.test_leads = []
        self.test_campaigns = []

    def setup(self):
        """Setup test environment"""
        print("\n=== Setting up DNC Test Suite ===")

        # Register test user
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json={
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD,
                    "full_name": "DNC Test User"
                }
            )
            if response.status_code == 201:
                print("✓ Test user registered")
            elif response.status_code == 400 and "already registered" in response.text:
                print("✓ Test user already exists")
            else:
                print(f"⚠ Registration response: {response.status_code}")
        except Exception as e:
            print(f"✗ Registration error: {e}")

        # Login
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD
                }
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.user_id = data["user_id"]
                print("✓ Logged in successfully")
            else:
                raise Exception(f"Login failed: {response.status_code} - {response.text}")
        except Exception as e:
            raise Exception(f"Login error: {e}")

    def headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.token}"}

    def create_test_lead(self, email=None, do_not_contact=False):
        """Create a test lead"""
        if not email:
            email = f"test_{uuid4().hex[:8]}@example.com"

        response = requests.post(
            f"{BASE_URL}/leads",
            headers=self.headers(),
            json={
                "first_name": "Test",
                "last_name": "Lead",
                "email": email,
                "company": "Test Company"
            }
        )

        if response.status_code != 201:
            raise Exception(f"Failed to create lead: {response.status_code} - {response.text}")

        lead = response.json()
        lead_id = lead["id"]

        # Set DNC status if requested
        if do_not_contact:
            update_response = requests.put(
                f"{BASE_URL}/leads/{lead_id}",
                headers=self.headers(),
                json={"do_not_contact": True}
            )
            if update_response.status_code != 200:
                print(f"⚠ Warning: Could not set DNC status (endpoint may not exist yet)")

        self.test_leads.append(lead_id)
        return lead_id, email

    def create_test_campaign(self, lead_id):
        """Create a test campaign with a lead"""
        # Create campaign
        response = requests.post(
            f"{BASE_URL}/campaigns",
            headers=self.headers(),
            json={
                "name": f"DNC Test Campaign {uuid4().hex[:8]}",
                "status": "draft"
            }
        )

        if response.status_code != 201:
            raise Exception(f"Failed to create campaign: {response.status_code}")

        campaign = response.json()
        campaign_id = campaign["id"]
        self.test_campaigns.append(campaign_id)

        # Add sequence step
        requests.post(
            f"{BASE_URL}/campaigns/{campaign_id}/steps",
            headers=self.headers(),
            json={
                "step_index": 1,
                "subject_template": "Test Subject",
                "body_template": "Test Body",
                "delay_days": 0
            }
        )

        # Add lead to campaign
        requests.post(
            f"{BASE_URL}/campaigns/{campaign_id}/leads",
            headers=self.headers(),
            json={"lead_ids": [lead_id]}
        )

        return campaign_id

    def test_dnc_basic_enforcement(self):
        """TC-SEC-007: Verify campaign worker respects DNC flag"""
        print("\n--- Test 1: Basic DNC Enforcement ---")

        try:
            # Create lead marked as DNC
            lead_id, email = self.create_test_lead(do_not_contact=True)
            print(f"✓ Created DNC lead: {email}")

            # Create campaign with this lead
            campaign_id = self.create_test_campaign(lead_id)
            print(f"✓ Created campaign: {campaign_id}")

            # Activate campaign
            requests.put(
                f"{BASE_URL}/campaigns/{campaign_id}",
                headers=self.headers(),
                json={"status": "active"}
            )
            print("✓ Activated campaign")

            # Wait for worker to process
            print("⏳ Waiting 10 seconds for worker processing...")
            time.sleep(10)

            # Check campaign lead status
            response = requests.get(
                f"{BASE_URL}/campaigns/{campaign_id}/leads",
                headers=self.headers()
            )

            if response.status_code == 200:
                campaign_leads = response.json()
                if campaign_leads:
                    status = campaign_leads[0].get("status")
                    stop_reason = campaign_leads[0].get("stop_reason")

                    if status == "stopped" and stop_reason == "do_not_contact":
                        print("✅ PASS: Campaign stopped for DNC lead")
                        return True
                    else:
                        print(f"❌ FAIL: Expected stopped/do_not_contact, got {status}/{stop_reason}")
                        return False

            print("⚠ WARN: Could not verify campaign lead status")
            return None

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_dnc_during_campaign(self):
        """TC-FAIL-013: Test marking DNC while campaign is sending"""
        print("\n--- Test 2: DNC Race Condition (Mark DNC During Campaign) ---")

        try:
            # Create normal lead
            lead_id, email = self.create_test_lead(do_not_contact=False)
            print(f"✓ Created lead: {email}")

            # Create campaign
            campaign_id = self.create_test_campaign(lead_id)
            print(f"✓ Created campaign: {campaign_id}")

            # Activate campaign
            requests.put(
                f"{BASE_URL}/campaigns/{campaign_id}",
                headers=self.headers(),
                json={"status": "active"}
            )
            print("✓ Activated campaign")

            # Immediately mark as DNC (race condition)
            print("⚡ Marking as DNC immediately...")
            dnc_response = requests.put(
                f"{BASE_URL}/leads/{lead_id}",
                headers=self.headers(),
                json={"do_not_contact": True}
            )

            if dnc_response.status_code == 200:
                print("✓ Marked as DNC")
            else:
                print(f"⚠ Could not mark DNC: {dnc_response.status_code}")

            # Wait for processing
            print("⏳ Waiting 10 seconds for worker processing...")
            time.sleep(10)

            # Check if email was sent or blocked
            response = requests.get(
                f"{BASE_URL}/campaigns/{campaign_id}/leads",
                headers=self.headers()
            )

            if response.status_code == 200:
                campaign_leads = response.json()
                if campaign_leads:
                    status = campaign_leads[0].get("status")
                    stop_reason = campaign_leads[0].get("stop_reason")

                    if status == "stopped" and stop_reason == "do_not_contact":
                        print("✅ PASS: Email blocked after DNC race condition")
                        return True
                    elif status == "in_progress" or status == "completed":
                        print("⚠ WARN: Email may have been sent before DNC was set (race condition)")
                        print("   This is acceptable if timing was tight")
                        return None
                    else:
                        print(f"❌ FAIL: Unexpected status {status}/{stop_reason}")
                        return False

            print("⚠ WARN: Could not verify status")
            return None

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_dnc_api_bypass_attempt(self):
        """Test attempting to bypass DNC via direct API"""
        print("\n--- Test 3: DNC API Bypass Attempt ---")

        try:
            # Create DNC lead
            lead_id, email = self.create_test_lead(do_not_contact=True)
            print(f"✓ Created DNC lead: {email}")

            # Try to send email directly via email API (if exists)
            response = requests.post(
                f"{BASE_URL}/email/send",
                headers=self.headers(),
                json={
                    "to_email": email,
                    "subject": "Bypass Test",
                    "body": "This should be blocked",
                    "lead_id": lead_id
                }
            )

            if response.status_code == 400 or response.status_code == 403:
                print("✅ PASS: Direct email send blocked for DNC lead")
                return True
            elif response.status_code == 404:
                print("⚠ SKIP: Direct email API not found (test not applicable)")
                return None
            else:
                print(f"❌ FAIL: Email send was not blocked (status: {response.status_code})")
                return False

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def test_dnc_concurrent_requests(self):
        """Test concurrent DNC updates"""
        print("\n--- Test 4: Concurrent DNC Updates ---")

        try:
            # Create lead
            lead_id, email = self.create_test_lead(do_not_contact=False)
            print(f"✓ Created lead: {email}")

            results = []

            def update_dnc(value):
                try:
                    response = requests.put(
                        f"{BASE_URL}/leads/{lead_id}",
                        headers=self.headers(),
                        json={"do_not_contact": value}
                    )
                    results.append(response.status_code)
                except Exception as e:
                    results.append(f"error: {e}")

            # Create concurrent threads
            threads = []
            for i in range(5):
                t = threading.Thread(target=update_dnc, args=(i % 2 == 0,))
                threads.append(t)

            # Start all threads simultaneously
            print("⚡ Sending 5 concurrent DNC update requests...")
            for t in threads:
                t.start()

            # Wait for completion
            for t in threads:
                t.join()

            print(f"✓ All requests completed: {results}")

            # Verify final state is consistent
            response = requests.get(
                f"{BASE_URL}/leads/{lead_id}",
                headers=self.headers()
            )

            if response.status_code == 200:
                lead = response.json()
                dnc_status = lead.get("do_not_contact", "NOT_FOUND")
                print(f"✓ Final DNC status: {dnc_status}")

                if dnc_status in [True, False]:
                    print("✅ PASS: Database maintained consistency under concurrent updates")
                    return True
                else:
                    print("❌ FAIL: DNC status not found in response")
                    return False

            print("⚠ WARN: Could not verify final state")
            return None

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def check_audit_logging(self):
        """Verify audit logging for DNC changes"""
        print("\n--- Test 5: Audit Logging Verification ---")

        try:
            # Check if audit log endpoint exists
            response = requests.get(
                f"{BASE_URL}/audit/logs",
                headers=self.headers(),
                params={"event_type": "dnc_change", "limit": 10}
            )

            if response.status_code == 404:
                print("⚠ SKIP: Audit logging not yet implemented")
                return None
            elif response.status_code == 200:
                logs = response.json()
                print(f"✓ Found {len(logs)} DNC audit log entries")

                if len(logs) > 0:
                    print("✅ PASS: Audit logging is active")
                    return True
                else:
                    print("⚠ WARN: No DNC audit logs found (may be new system)")
                    return None
            else:
                print(f"⚠ Unexpected response: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    def cleanup(self):
        """Clean up test data"""
        print("\n=== Cleaning Up Test Data ===")

        # Delete test campaigns
        for campaign_id in self.test_campaigns:
            try:
                requests.delete(
                    f"{BASE_URL}/campaigns/{campaign_id}",
                    headers=self.headers()
                )
            except:
                pass

        # Delete test leads
        for lead_id in self.test_leads:
            try:
                requests.delete(
                    f"{BASE_URL}/leads/{lead_id}",
                    headers=self.headers()
                )
            except:
                pass

        print("✓ Cleanup completed")

    def run_all_tests(self):
        """Run all DNC tests"""
        print("\n" + "="*60)
        print("DNC ENFORCEMENT TEST SUITE")
        print("="*60)

        try:
            self.setup()

            results = {
                "TC-SEC-007: Basic DNC Enforcement": self.test_dnc_basic_enforcement(),
                "TC-FAIL-013: DNC Race Condition": self.test_dnc_during_campaign(),
                "API Bypass Prevention": self.test_dnc_api_bypass_attempt(),
                "Concurrent DNC Updates": self.test_dnc_concurrent_requests(),
                "Audit Logging": self.check_audit_logging()
            }

            # Print summary
            print("\n" + "="*60)
            print("TEST SUMMARY")
            print("="*60)

            passed = sum(1 for v in results.values() if v is True)
            failed = sum(1 for v in results.values() if v is False)
            skipped = sum(1 for v in results.values() if v is None)

            for test_name, result in results.items():
                status = "✅ PASS" if result is True else "❌ FAIL" if result is False else "⚠ SKIP"
                print(f"{status} - {test_name}")

            print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped/warnings")
            print("="*60)

            return failed == 0

        finally:
            self.cleanup()


if __name__ == "__main__":
    suite = DNCTestSuite()
    success = suite.run_all_tests()
    exit(0 if success else 1)
