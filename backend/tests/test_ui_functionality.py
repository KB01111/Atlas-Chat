"""
UI Functionality Test for Atlas-Chat.

This script tests the UI functionality using Selenium WebDriver.
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


class AtlasChatUITester:
    """UI Tester for Atlas-Chat application."""

    def __init__(self):
        """Initialize UI tester."""
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

    def test_login_page(self):
        """Test login page functionality."""
        logger.info("Testing login page...")

        try:
            # Navigate to login page
            self.driver.get(f"{BASE_URL}/login")

            # Check page title
            if "Atlas Chat" not in self.driver.title:
                logger.warning(f"❌ Unexpected page title: {self.driver.title}")
                return False

            logger.info(f"✅ Page title: {self.driver.title}")

            # Check login form elements
            email_input = self.driver.find_element(By.ID, "email")
            password_input = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Login')]"
            )

            if not all([email_input, password_input, login_button]):
                logger.warning("❌ Login form elements not found")
                return False

            logger.info("✅ Login form elements found")

            # Test form validation
            login_button.click()

            # Wait for validation messages
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
                )
                logger.info("✅ Form validation working")
            except TimeoutException:
                logger.warning("❌ Form validation not working")
                return False

            # Test login with test credentials
            email_input.clear()
            email_input.send_keys("test@example.com")
            password_input.clear()
            password_input.send_keys("password123")
            login_button.click()

            # Check if redirected to dashboard or error message shown
            try:
                WebDriverWait(self.driver, 5).until(
                    lambda driver: "/dashboard" in driver.current_url
                    or len(driver.find_elements(By.CLASS_NAME, "error-message")) > 0
                )
                logger.info("✅ Login form submission working")
            except TimeoutException:
                logger.warning("❌ Login form submission not working")
                return False

            logger.info("Login page test completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error testing login page: {e}")
            return False

    def test_agent_selector(self):
        """Test agent selector functionality."""
        logger.info("Testing agent selector...")

        try:
            # Navigate to dashboard
            self.driver.get(f"{BASE_URL}/dashboard")

            # Check if agent selector is present
            try:
                agent_selector = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "agent-select"))
                )
                logger.info("✅ Agent selector found")
            except TimeoutException:
                logger.warning("❌ Agent selector not found")
                return False

            # Check if agent selector has options
            options = agent_selector.find_elements(By.TAG_NAME, "option")
            if not options:
                logger.warning("❌ No agent options found")
                return False

            logger.info(f"✅ Found {len(options)} agent options")

            # Test selecting different agents
            for i, option in enumerate(options[:2]):  # Test first two options
                option.click()
                time.sleep(1)  # Wait for selection to take effect

                # Check if agent info is updated
                try:
                    agent_info = self.driver.find_element(By.CLASS_NAME, "agent-info")
                    logger.info(f"✅ Agent info updated for option {i+1}")
                except NoSuchElementException:
                    logger.warning(f"❌ Agent info not updated for option {i+1}")
                    return False

            logger.info("Agent selector test completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error testing agent selector: {e}")
            return False

    def test_chat_interface(self):
        """Test chat interface functionality."""
        logger.info("Testing chat interface...")

        try:
            # Navigate to chat page
            self.driver.get(f"{BASE_URL}/chat")

            # Check if chat container is present
            try:
                chat_container = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "chat-container"))
                )
                logger.info("✅ Chat container found")
            except TimeoutException:
                logger.warning("❌ Chat container not found")
                return False

            # Check if message input is present
            try:
                message_input = self.driver.find_element(By.ID, "message-input")
                send_button = self.driver.find_element(By.ID, "send-button")
                logger.info("✅ Message input and send button found")
            except NoSuchElementException:
                logger.warning("❌ Message input or send button not found")
                return False

            # Test sending a message
            test_message = "Hello, Atlas Chat!"
            message_input.clear()
            message_input.send_keys(test_message)
            send_button.click()

            # Check if message appears in chat
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.text_to_be_present_in_element(
                        (By.CLASS_NAME, "user-message"), test_message
                    )
                )
                logger.info("✅ User message appears in chat")
            except TimeoutException:
                logger.warning("❌ User message does not appear in chat")
                return False

            # Check if agent responds
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "agent-message"))
                )
                logger.info("✅ Agent response received")
            except TimeoutException:
                logger.warning("❌ No agent response received")
                return False

            logger.info("Chat interface test completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error testing chat interface: {e}")
            return False

    def test_code_execution(self):
        """Test code execution functionality."""
        logger.info("Testing code execution...")

        try:
            # Navigate to code execution page
            self.driver.get(f"{BASE_URL}/code")

            # Check if code editor is present
            try:
                code_editor = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "monaco-editor"))
                )
                logger.info("✅ Code editor found")
            except TimeoutException:
                logger.warning("❌ Code editor not found")
                return False

            # Check if language selector is present
            try:
                language_selector = self.driver.find_element(By.ID, "language-select")
                run_button = self.driver.find_element(By.CLASS_NAME, "run-button")
                logger.info("✅ Language selector and run button found")
            except NoSuchElementException:
                logger.warning("❌ Language selector or run button not found")
                return False

            # Test executing code
            # Note: We can't directly type into Monaco editor with Selenium
            # This is a simplified test that just clicks the run button
            run_button.click()

            # Check if output is updated
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.find_element(
                        By.CLASS_NAME, "output-content"
                    ).text
                    != "Run your code to see output here..."
                )
                logger.info("✅ Code execution output updated")
            except TimeoutException:
                logger.warning("❌ Code execution output not updated")
                return False

            logger.info("Code execution test completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error testing code execution: {e}")
            return False

    def test_model_switching(self):
        """Test model switching functionality."""
        logger.info("Testing model switching...")

        try:
            # Navigate to settings page
            self.driver.get(f"{BASE_URL}/settings")

            # Check if model selector is present
            try:
                model_selector = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "model-select"))
                )
                logger.info("✅ Model selector found")
            except TimeoutException:
                logger.warning("❌ Model selector not found")
                return False

            # Check if model selector has options
            options = model_selector.find_elements(By.TAG_NAME, "option")
            if not options:
                logger.warning("❌ No model options found")
                return False

            logger.info(f"✅ Found {len(options)} model options")

            # Test selecting different models
            for i, option in enumerate(options[:2]):  # Test first two options
                option.click()
                time.sleep(1)  # Wait for selection to take effect

                # Check if model info is updated
                try:
                    model_info = self.driver.find_element(By.CLASS_NAME, "model-info")
                    logger.info(f"✅ Model info updated for option {i+1}")
                except NoSuchElementException:
                    logger.warning(f"❌ Model info not updated for option {i+1}")
                    return False

            # Navigate to chat page to test model in action
            self.driver.get(f"{BASE_URL}/chat")

            # Check if selected model is displayed
            try:
                model_display = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "selected-model"))
                )
                logger.info(f"✅ Selected model displayed: {model_display.text}")
            except TimeoutException:
                logger.warning("❌ Selected model not displayed")
                return False

            logger.info("Model switching test completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error testing model switching: {e}")
            return False

    def run_all_tests(self):
        """Run all UI tests."""
        logger.info("Running all UI tests...")

        try:
            self.setup()

            tests = [
                ("Login Page", self.test_login_page),
                ("Agent Selector", self.test_agent_selector),
                ("Chat Interface", self.test_chat_interface),
                ("Code Execution", self.test_code_execution),
                ("Model Switching", self.test_model_switching),
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
            logger.info("UI TEST RESULTS SUMMARY")
            logger.info("=" * 50)

            for name, result in results.items():
                status = "✅" if result == "PASSED" else "❌"
                logger.info(f"{status} {name}: {result}")

            logger.info("=" * 50)
            logger.info(f"Overall result: {'PASSED' if all_passed else 'FAILED'}")
            logger.info("=" * 50)

            return all_passed

        except Exception as e:
            logger.error(f"Error running UI tests: {e}")
            return False

        finally:
            self.teardown()


if __name__ == "__main__":
    tester = AtlasChatUITester()
    tester.run_all_tests()
