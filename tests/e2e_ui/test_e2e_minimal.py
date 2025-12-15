"""
Minimal E2E tests that actually call the backend
Only includes tests that make real API calls to verify end-to-end functionality
"""
import pytest
import os
import time
from playwright.sync_api import Page, expect


# Configuration
RAG_UI_ENDPOINT = os.getenv("RAG_UI_ENDPOINT", "http://localhost:8501")
TEST_TIMEOUT = 30000  # 30 seconds


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context"""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
    }


@pytest.fixture(autouse=True)
def wait_for_app(page: Page):
    """Wait for the Streamlit app to be ready before each test"""
    page.goto(RAG_UI_ENDPOINT)
    # Wait for Streamlit to finish loading
    page.wait_for_load_state("networkidle")
    # Give Streamlit additional time to initialize
    time.sleep(2)


class TestMaaSIntegration:
    """E2E tests for MaaS (Model-as-a-Service) integration through the UI
    
    These tests verify that MaaS works end-to-end through the browser UI.
    They send actual messages and verify MaaS responses - these are the only
    tests that actually call the backend.
    """
    
    @pytest.mark.skipif(
        os.getenv("SKIP_MODEL_TESTS", "false").lower() == "true",
        reason="Model inference tests disabled via SKIP_MODEL_TESTS"
    )
    def test_maas_chat_completion_direct_mode(self, page: Page):
        """Test that MaaS responds to chat messages in direct mode - E2E test with backend call"""
        # Verify the chat input is visible
        chat_input = page.get_by_placeholder("Ask a question...", exact=False)
        expect(chat_input).to_be_visible(timeout=TEST_TIMEOUT)
        
        # Send a simple test message
        test_message = "Say 'Hello from RAG e2e test!' in one short sentence."
        chat_input.fill(test_message)
        chat_input.press("Enter")
        
        # Wait for Streamlit to process the input and rerun
        page.wait_for_load_state("networkidle")
        time.sleep(3)  # Give Streamlit time to send request and start receiving response
        
        # Wait for the user message to appear in chat
        user_msg = page.get_by_text(test_message, exact=False)
        expect(user_msg).to_be_visible(timeout=TEST_TIMEOUT)
        
        # Wait for assistant response (MaaS should respond)
        # Streamlit chat messages have structure: stChatMessage with role
        max_wait = 90  # seconds - MaaS can be slow
        wait_time = 0
        while wait_time < max_wait:
            time.sleep(3)
            wait_time += 3
            
            # Check for new assistant message content
            assistant_containers = page.locator('[data-testid="stChatMessage"]').all()
            
            for container in assistant_containers:
                if container.is_visible():
                    text_content = container.inner_text().strip()
                    # Check if it's a new assistant message (not greeting, not user message)
                    if (text_content and 
                        text_content != "How can I help you?" and 
                        test_message not in text_content and
                        len(text_content) > 15):  # Real response should be substantial
                        # Found a real MaaS response!
                        print(f"✅ MaaS responded: {text_content[:150]}...")
                        assert len(text_content) > 10, "MaaS response too short"
                        return  # Success!
            
            # Also check for any new text that appeared after user message
            all_visible_text = page.locator('body').inner_text()
            if test_message in all_visible_text:
                # Check if there's additional text that looks like a response
                lines = all_visible_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if (line and 
                        test_message not in line and
                        "How can I help you?" not in line and
                        len(line) > 20 and  # Substantial response
                        any(word in line.lower() for word in ['hello', 'test', 'rag', 'e2e', 'from'])):  # Should mention something from our test
                        print(f"✅ MaaS responded (found in text): {line[:150]}...")
                        return  # Success!
        
        # If we get here, no response was received
        pytest.fail(f"MaaS did not respond within {max_wait} seconds")

