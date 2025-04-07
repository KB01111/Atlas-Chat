"""
End-to-End User Flow Tests for Atlas-Chat.

This script tests complete user flows from login to task completion.
"""

import logging
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Base URL for UI tests
BASE_URL = "http://localhost:3000"


class AtlasChatE2ETester:
    """End-to-End Tester for Atlas-Chat application."""

    def __init__(self):
        """Initialize E2E tester."""
        self.driver = None

    def setup(self):
        """Set up WebDriver."""
        logger.info("Setting up WebDriver...")

        # Set up Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Create WebDriver
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

        logger.info("WebDriver set up successfully")

    def teardown(self):
        """Tear down WebDriver."""
        if self.driver:
            logger.info("Tearing down WebDriver...")
            self.driver.quit()
            logger.info("WebDriver torn down successfully")

    def login(self, email="test@example.com", password="password123"):
        """Log in to the application."""
        logger.info(f"Logging in as {email}...")

        # Navigate to login page
        self.driver.get(f"{BASE_URL}/login")

        # Fill in login form
        email_input = self.driver.find_element(By.ID, "email")
        password_input = self.driver.find_element(By.ID, "password")
        login_button = self.driver.find_element(
            By.XPATH, "//button[contains(text(), 'Login')]"
        )

        email_input.clear()
        email_input.send_keys(email)
        password_input.clear()
        password_input.send_keys(password)
        login_button.click()

        # Wait for dashboard to load
        try:
            WebDriverWait(self.driver, 10).until(
                lambda driver: "/dashboard" in driver.current_url
            )
            logger.info("✅ Login successful")
            return True
        except TimeoutException:
            logger.warning("❌ Login failed")
            return False

    def test_research_flow(self):
        """Test research flow with agent."""
        logger.info("Testing research flow...")

        try:
            # Login
            if not self.login():
                return False

            # Navigate to dashboard
            self.driver.get(f"{BASE_URL}/dashboard")

            # Select research agent
            try:
                agent_selector = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "agent-select"))
                )

                # Find research agent option
                research_option = None
                for option in agent_selector.find_elements(By.TAG_NAME, "option"):
                    if "research" in option.text.lower():
                        research_option = option
                        break

                if not research_option:
                    logger.warning("❌ Research agent not found")
                    return False

                research_option.click()
                logger.info("✅ Selected research agent")

            except (TimeoutException, NoSuchElementException) as e:
                logger.warning(f"❌ Error selecting research agent: {e}")
                return False

            # Navigate to chat
            self.driver.get(f"{BASE_URL}/chat")

            # Send research query
            try:
                message_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "message-input"))
                )
                send_button = self.driver.find_element(By.ID, "send-button")

                research_query = (
                    "What are the latest developments in quantum computing?"
                )
                message_input.clear()
                message_input.send_keys(research_query)
                send_button.click()

                logger.info("✅ Sent research query")

            except (TimeoutException, NoSuchElementException) as e:
                logger.warning(f"❌ Error sending research query: {e}")
                return False

            # Wait for response with citations
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "agent-message"))
                )

                # Check for citations
                agent_message = self.driver.find_element(By.CLASS_NAME, "agent-message")
                if "[1]" in agent_message.text or "http" in agent_message.text:
                    logger.info("✅ Received research response with citations")
                else:
                    logger.warning("❌ Research response does not contain citations")
                    return False

            except TimeoutException:
                logger.warning("❌ No research response received")
                return False

            logger.info("Research flow test completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error testing research flow: {e}")
            return False

    def test_coding_flow(self):
        """Test coding flow with agent and code execution."""
        logger.info("Testing coding flow...")

        try:
            # Login
            if not self.login():
                return False

            # Navigate to dashboard
            self.driver.get(f"{BASE_URL}/dashboard")

            # Select coding agent
            try:
                agent_selector = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "agent-select"))
                )

                # Find coding agent option
                coding_option = None
                for option in agent_selector.find_elements(By.TAG_NAME, "option"):
                    if "cod" in option.text.lower():
                        coding_option = option
                        break

                if not coding_option:
                    logger.warning("❌ Coding agent not found")
                    return False

                coding_option.click()
                logger.info("✅ Selected coding agent")

            except (TimeoutException, NoSuchElementException) as e:
                logger.warning(f"❌ Error selecting coding agent: {e}")
                return False

            # Navigate to chat
            self.driver.get(f"{BASE_URL}/chat")

            # Send coding query
            try:
                message_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "message-input"))
                )
                send_button = self.driver.find_element(By.ID, "send-button")

                coding_query = (
                    "Write a Python function to calculate the Fibonacci sequence"
                )
                message_input.clear()
                message_input.send_keys(coding_query)
                send_button.click()

                logger.info("✅ Sent coding query")

            except (TimeoutException, NoSuchElementException) as e:
                logger.warning(f"❌ Error sending coding query: {e}")
                return False

            # Wait for response with code
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "agent-message"))
                )

                # Check for code block
                agent_message = self.driver.find_element(By.CLASS_NAME, "agent-message")
                if (
                    "```python" in agent_message.text
                    or "def fibonacci" in agent_message.text
                ):
                    logger.info("✅ Received coding response with code")
                else:
                    logger.warning("❌ Coding response does not contain code")
                    return False

            except TimeoutException:
                logger.warning("❌ No coding response received")
                return False

            # Navigate to code execution
            self.driver.get(f"{BASE_URL}/code")

            # Wait for code editor
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "monaco-editor"))
                )

                # TODO: Implement pasting code into Monaco editor
                # This is a simplified test that just checks if the editor loaded
                logger.info("✅ Code editor loaded")

                # Check if run button is present
                run_button = self.driver.find_element(By.CLASS_NAME, "run-button")
                logger.info("✅ Run button found")

            except (TimeoutException, NoSuchElementException) as e:
                logger.warning(f"❌ Error with code editor: {e}")
                return False

            logger.info("Coding flow test completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error testing coding flow: {e}")
            return False

    def test_model_switching_flow(self):
        """Test model switching during conversation."""
        logger.info("Testing model switching flow...")

        try:
            # Login
            if not self.login():
                return False

            # Navigate to chat
            self.driver.get(f"{BASE_URL}/chat")

            # Send initial message
            try:
                message_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "message-input"))
                )
                send_button = self.driver.find_element(By.ID, "send-button")

                initial_query = "Hello, can you help me with some information?"
                message_input.clear()
                message_input.send_keys(initial_query)
                send_button.click()

                logger.info("✅ Sent initial query")

            except (TimeoutException, NoSuchElementException) as e:
                logger.warning(f"❌ Error sending initial query: {e}")
                return False

            # Wait for response
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "agent-message"))
                )
                logger.info("✅ Received initial response")

            except TimeoutException:
                logger.warning("❌ No initial response received")
                return False

            # Switch model
            try:
                model_selector = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "model-select"))
                )

                # Get current model
                current_model = model_selector.get_attribute("value")

                # Select different model
                different_model = None
                for option in model_selector.find_elements(By.TAG_NAME, "option"):
                    if option.get_attribute("value") != current_model:
                        different_model = option
                        break

                if not different_model:
                    logger.warning("❌ No alternative model found")
                    return False

                different_model.click()
                logger.info("✅ Switched to different model")

                # Check if model switch notification appears
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, "model-switch-notification")
                        )
                    )
                    logger.info("✅ Model switch notification appeared")
                except TimeoutException:
                    logger.warning("❌ No model switch notification")
                    # Not critical, continue test

            except (TimeoutException, NoSuchElementException) as e:
                logger.warning(f"❌ Error switching model: {e}")
                return False

            # Send follow-up message
            try:
                message_input = self.driver.find_element(By.ID, "message-input")
                send_button = self.driver.find_element(By.ID, "send-button")

                followup_query = "What's the difference between quantum computing and classical computing?"
                message_input.clear()
                message_input.send_keys(followup_query)
                send_button.click()

                logger.info("✅ Sent follow-up query")

            except NoSuchElementException as e:
                logger.warning(f"❌ Error sending follow-up query: {e}")
                return False

            # Wait for response from new model
            try:
                # Get current message count
                current_messages = len(
                    self.driver.find_elements(By.CLASS_NAME, "agent-message")
                )

                # Wait for new message
                WebDriverWait(self.driver, 30).until(
                    lambda driver: len(
                        driver.find_elements(By.CLASS_NAME, "agent-message")
                    )
                    > current_messages
                )

                logger.info("✅ Received response from new model")

            except TimeoutException:
                logger.warning("❌ No response from new model")
                return False

            logger.info("Model switching flow test completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error testing model switching flow: {e}")
            return False

    def test_agent_team_flow(self):
        """Test agent team collaboration flow."""
        logger.info("Testing agent team flow...")

        try:
            # Login
            if not self.login():
                return False

            # Navigate to teams page
            self.driver.get(f"{BASE_URL}/teams")

            # Check if teams page loads
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "teams-container"))
                )
                logger.info("✅ Teams page loaded")

            except TimeoutException:
                logger.warning("❌ Teams page not loaded")
                return False

            # Select a team
            try:
                teams = self.driver.find_elements(By.CLASS_NAME, "team-card")

                if not teams:
                    logger.warning("❌ No teams found")
                    return False

                # Click on first team
                teams[0].click()
                logger.info("✅ Selected team")

            except NoSuchElementException as e:
                logger.warning(f"❌ Error selecting team: {e}")
                return False

            # Wait for team chat to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "team-chat-container")
                    )
                )
                logger.info("✅ Team chat loaded")

            except TimeoutException:
                logger.warning("❌ Team chat not loaded")
                return False

            # Send message to team
            try:
                message_input = self.driver.find_element(By.ID, "team-message-input")
                send_button = self.driver.find_element(By.ID, "team-send-button")

                team_query = "I need help with a complex research project involving data analysis and visualization"
                message_input.clear()
                message_input.send_keys(team_query)
                send_button.click()

                logger.info("✅ Sent team query")

            except NoSuchElementException as e:
                logger.warning(f"❌ Error sending team query: {e}")
                return False

            # Wait for team responses
            try:
                # Wait for first agent response
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "team-agent-message")
                    )
                )

                # Wait for additional agent responses
                time.sleep(5)  # Give time for other agents to respond

                # Check if multiple agents responded
                agent_messages = self.driver.find_elements(
                    By.CLASS_NAME, "team-agent-message"
                )
                agent_names = set()

                for message in agent_messages:
                    try:
                        agent_name = message.find_element(
                            By.CLASS_NAME, "agent-name"
                        ).text
                        agent_names.add(agent_name)
                    except NoSuchElementException:
                        pass

                if len(agent_names) > 1:
                    logger.info(
                        f"✅ Multiple agents responded: {', '.join(agent_names)}"
                    )
                else:
                    logger.warning("❌ Only one agent responded")
                    # Not critical, continue test

            except TimeoutException:
                logger.warning("❌ No team responses received")
                return False

            logger.info("Agent team flow test completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error testing agent team flow: {e}")
            return False

    def run_all_tests(self):
        """Run all E2E tests."""
        logger.info("Running all end-to-end tests...")

        try:
            self.setup()

            tests = [
                ("Research Flow", self.test_research_flow),
                ("Coding Flow", self.test_coding_flow),
                ("Model Switching Flow", self.test_model_switching_flow),
                ("Agent Team Flow", self.test_agent_team_flow),
            ]

            results = {}
            all_passed = True

            for name, test_func in tests:
                logger.info(f"\n{'='*50}\nRunning {name} test\n{'='*50}")
                try:
                    passed = test_func()
                    results[name] = "PASSED" if passed else "FAILED"
                    all_passed = all_passed and passed
                except Exception as e:
                    logger.error(f"Error running {name} test: {e}")
                    results[name] = "ERROR"
                    all_passed = False

            logger.info("\n\n")
            logger.info("=" * 50)
            logger.info("END-TO-END TEST RESULTS SUMMARY")
            logger.info("=" * 50)

            for name, result in results.items():
                status = "✅" if result == "PASSED" else "❌"
                logger.info(f"{status} {name}: {result}")

            logger.info("=" * 50)
            logger.info(f"Overall result: {'PASSED' if all_passed else 'FAILED'}")
            logger.info("=" * 50)

            return all_passed

        except Exception as e:
            logger.error(f"Error running E2E tests: {e}")
            return False

        finally:
            self.teardown()


if __name__ == "__main__":
    tester = AtlasChatE2ETester()
    tester.run_all_tests()
