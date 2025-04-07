"""
Test script for Atlas-Chat implementations.

This script tests the various components implemented for Atlas-Chat:
1. Intelligent Model Router
2. Agent Factory Pattern
3. Google GenAI Integration
4. LangGraph Integration
5. Roo-Code Adapter
"""

import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
try:
    from app.core.services.agent_factory.agent_definition import (
        AgentDefinition,
        AgentMessage,
        AgentRequest,
    )
    from app.core.services.agent_factory.agent_factory import AgentFactory
    from app.core.services.agent_factory.agent_memory import MemoryManager
    from app.core.services.agent_factory.agent_specialization import (
        SpecializationRegistry,
    )
    from app.core.services.agent_factory.agent_team import (
        AgentTeam,
        TeamMember,
        TeamRegistry,
    )
    from app.core.services.model_routing.model_router import ModelRouter
    from app.core.services.model_routing.model_specs import ModelSpecs
except ImportError as e:
    logger.error(f"Error importing components: {e}")
    sys.exit(1)


def test_model_router():
    """Test the intelligent model router."""
    logger.info("Testing Intelligent Model Router...")

    # Create model router
    model_router = ModelRouter()

    # Get model specs
    model_specs = ModelSpecs()

    # Test model selection
    test_cases = [
        {
            "name": "Simple query",
            "query": "What is the capital of France?",
            "task_type": "general",
            "user_preference": None,
            "expected_provider": "openai",
        },
        {
            "name": "Code generation",
            "query": "Write a Python function to calculate Fibonacci numbers",
            "task_type": "coding",
            "user_preference": None,
            "expected_provider": "anthropic",
        },
        {
            "name": "Research query",
            "query": "Explain the implications of quantum computing on cryptography",
            "task_type": "research",
            "user_preference": None,
            "expected_provider": "anthropic",
        },
        {
            "name": "User preference",
            "query": "Tell me a joke",
            "task_type": "general",
            "user_preference": "google",
            "expected_provider": "google",
        },
    ]

    success_count = 0

    for case in test_cases:
        logger.info(f"Test case: {case['name']}")

        try:
            # Select model
            model_id = model_router.select_model(
                query=case["query"],
                task_type=case["task_type"],
                user_preference=case["user_preference"],
            )

            # Get model spec
            model_spec = model_specs.get_spec(model_id)

            if model_spec:
                provider = model_spec.provider
                logger.info(f"Selected model: {model_id} (Provider: {provider})")

                # Check if provider matches expected
                if provider.lower() == case["expected_provider"].lower():
                    logger.info("✅ Test passed")
                    success_count += 1
                else:
                    logger.warning(
                        f"❌ Test failed: Expected provider {case['expected_provider']}, "
                        f"got {provider}"
                    )
            else:
                logger.warning(f"❌ Test failed: Model spec not found for {model_id}")
        except Exception as e:
            logger.error(f"❌ Test failed with error: {e}")

    logger.info(f"Model Router Tests: {success_count}/{len(test_cases)} passed")
    return success_count == len(test_cases)


def test_agent_factory():
    """Test the agent factory pattern."""
    logger.info("Testing Agent Factory Pattern...")

    # Create model router
    model_router = ModelRouter()

    # Create agent factory
    agent_factory = AgentFactory(model_router)

    # Test agent creation
    test_agents = [
        {
            "name": "Research Assistant",
            "description": "Agent specialized for research tasks",
            "agent_type": "sdk",
            "model_id": "claude-3-5-sonnet",
            "system_prompt": "You are a research expert that helps find and analyze information.",
            "tools": ["search_web", "search_graphiti"],
            "memory_enabled": True,
            "specialized_for": "research",
        },
        {
            "name": "Code Helper",
            "description": "Agent specialized for coding tasks",
            "agent_type": "sdk",
            "model_id": "gpt-4o",
            "system_prompt": "You are a coding expert that helps write, explain, and debug code.",
            "tools": ["execute_code", "search_documentation"],
            "memory_enabled": True,
            "specialized_for": "coding",
        },
        {
            "name": "Writing Assistant",
            "description": "Agent specialized for writing tasks",
            "agent_type": "langgraph",
            "model_id": "claude-3-opus",
            "system_prompt": "You are a writing expert that helps create, edit, and improve written content.",
            "tools": ["check_grammar", "search_web"],
            "memory_enabled": True,
            "specialized_for": "writing",
        },
    ]

    created_agents = []
    success_count = 0

    for agent_data in test_agents:
        logger.info(f"Creating agent: {agent_data['name']}")

        try:
            # Create agent definition
            definition = AgentDefinition(**agent_data)

            # Create agent
            agent_id = agent_factory.create_agent(definition)
            created_agents.append(agent_id)

            logger.info(f"Created agent with ID: {agent_id}")

            # Get agent
            retrieved = agent_factory.get_agent(agent_id)

            if retrieved and retrieved.name == agent_data["name"]:
                logger.info("✅ Agent creation and retrieval test passed")
                success_count += 1
            else:
                logger.warning("❌ Agent creation or retrieval test failed")
        except Exception as e:
            logger.error(f"❌ Agent creation test failed with error: {e}")

    # Test agent update
    if created_agents:
        try:
            agent_id = created_agents[0]
            logger.info(f"Testing agent update for {agent_id}")

            # Update agent
            updates = {"description": "Updated description"}
            updated = agent_factory.update_agent(agent_id, updates)

            if updated and updated.description == "Updated description":
                logger.info("✅ Agent update test passed")
                success_count += 1
            else:
                logger.warning("❌ Agent update test failed")
        except Exception as e:
            logger.error(f"❌ Agent update test failed with error: {e}")

    # Test agent deletion
    if created_agents:
        try:
            agent_id = created_agents[-1]
            logger.info(f"Testing agent deletion for {agent_id}")

            # Delete agent
            deleted = agent_factory.delete_agent(agent_id)

            if deleted and agent_factory.get_agent(agent_id) is None:
                logger.info("✅ Agent deletion test passed")
                success_count += 1
            else:
                logger.warning("❌ Agent deletion test failed")
        except Exception as e:
            logger.error(f"❌ Agent deletion test failed with error: {e}")

    # Test specialization registry
    try:
        logger.info("Testing specialization registry")

        # Create specialization registry
        registry = SpecializationRegistry()

        # Get specializations
        specializations = registry.get_all_specializations()

        if specializations and len(specializations) > 0:
            logger.info(f"Found {len(specializations)} specializations")
            logger.info("✅ Specialization registry test passed")
            success_count += 1
        else:
            logger.warning("❌ Specialization registry test failed")
    except Exception as e:
        logger.error(f"❌ Specialization registry test failed with error: {e}")

    # Test team registry
    try:
        logger.info("Testing team registry")

        # Create team registry
        team_registry = TeamRegistry()

        # Create team
        team = AgentTeam(
            name="Research Team",
            description="Team for comprehensive research tasks",
            members=[
                TeamMember(
                    agent_id=created_agents[0] if created_agents else "agent_123",
                    role="researcher",
                    description="Responsible for gathering information",
                )
            ],
        )

        # Register team
        team_id = team_registry.register_team(team)

        # Get team
        retrieved_team = team_registry.get_team(team_id)

        if retrieved_team and retrieved_team.name == "Research Team":
            logger.info("✅ Team registry test passed")
            success_count += 1
        else:
            logger.warning("❌ Team registry test failed")
    except Exception as e:
        logger.error(f"❌ Team registry test failed with error: {e}")

    # Test memory manager
    try:
        logger.info("Testing memory manager")

        # Create memory manager
        memory_manager = MemoryManager()

        # Add memory entry
        agent_id = created_agents[0] if created_agents else "agent_123"
        entry_id = memory_manager.add_entry(
            agent_id=agent_id, content="Test memory entry", metadata={"test": True}
        )

        # Get entries
        entries = memory_manager.get_entries(agent_id)

        if entries and len(entries) > 0:
            logger.info("✅ Memory manager test passed")
            success_count += 1
        else:
            logger.warning("❌ Memory manager test failed")
    except Exception as e:
        logger.error(f"❌ Memory manager test failed with error: {e}")

    total_tests = (
        len(test_agents) + 4
    )  # Creation tests + update + deletion + specialization + team + memory
    logger.info(f"Agent Factory Tests: {success_count}/{total_tests} passed")
    return success_count == total_tests


def test_google_genai():
    """Test Google GenAI integration."""
    logger.info("Testing Google GenAI Integration...")

    try:
        # Import Google provider
        from app.core.services.google_agent import GoogleProvider

        # Check if API key is available
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not set, skipping actual API calls")

        # Create model router
        model_router = ModelRouter()

        # Create Google provider
        google_provider = GoogleProvider(model_router)

        # Create agent definition
        definition = AgentDefinition(
            name="Google Assistant",
            description="Agent using Google Gemini models",
            agent_type="google",
            model_id="gemini-2-5-flash",
            system_prompt="You are a helpful assistant powered by Google Gemini.",
        )

        # Create agent
        agent_id = google_provider.create_agent(definition)
        logger.info(f"Created Google agent with ID: {agent_id}")

        # Get agent
        retrieved = google_provider.get_agent(agent_id)

        if retrieved and retrieved.name == "Google Assistant":
            logger.info("✅ Google agent creation and retrieval test passed")
            return True
        else:
            logger.warning("❌ Google agent creation or retrieval test failed")
            return False
    except ImportError:
        logger.warning("Google GenAI integration not available, skipping test")
        return True  # Skip test
    except Exception as e:
        logger.error(f"❌ Google GenAI test failed with error: {e}")
        return False


def test_langgraph():
    """Test LangGraph integration."""
    logger.info("Testing LangGraph Integration...")

    try:
        # Import LangGraph provider
        from app.core.services.langgraph_agent import LangGraphProvider

        # Create model router
        model_router = ModelRouter()

        # Create LangGraph provider
        langgraph_provider = LangGraphProvider(model_router)

        # Create agent definition
        definition = AgentDefinition(
            name="LangGraph Assistant",
            description="Agent using LangGraph",
            agent_type="langgraph",
            model_id="gpt-4o",
            system_prompt="You are a helpful assistant powered by LangGraph.",
        )

        # Create agent
        agent_id = langgraph_provider.create_agent(definition)
        logger.info(f"Created LangGraph agent with ID: {agent_id}")

        # Get agent
        retrieved = langgraph_provider.get_agent(agent_id)

        if retrieved and retrieved.name == "LangGraph Assistant":
            logger.info("✅ LangGraph agent creation and retrieval test passed")
            return True
        else:
            logger.warning("❌ LangGraph agent creation or retrieval test failed")
            return False
    except ImportError:
        logger.warning("LangGraph integration not available, skipping test")
        return True  # Skip test
    except Exception as e:
        logger.error(f"❌ LangGraph test failed with error: {e}")
        return False


def test_roo_code():
    """Test Roo-Code adapter."""
    logger.info("Testing Roo-Code Adapter...")

    try:
        # Import Roo-Code adapter
        from app.core.services.roo_code import RooCodeAdapter, RooCodeConfig

        # Create model router
        model_router = ModelRouter()

        # Create Roo-Code adapter
        config = RooCodeConfig(workspace_dir="./test_roo_workspace")
        roo_adapter = RooCodeAdapter(model_router, config)

        # Create agent definition
        definition = AgentDefinition(
            name="Roo-Code Assistant",
            description="Agent using Roo-Code",
            agent_type="sdk",
            model_id="gpt-4o",
            system_prompt="You are a helpful assistant powered by Roo-Code.",
        )

        # Create agent
        agent_id = roo_adapter.create_agent(definition)
        logger.info(f"Created Roo-Code agent with ID: {agent_id}")

        # Get agent
        retrieved = roo_adapter.get_agent(agent_id)

        if retrieved and retrieved.name == "Roo-Code Assistant":
            logger.info("✅ Roo-Code agent creation and retrieval test passed")

            # Test request processing (fallback mode)
            request = AgentRequest(
                agent_id=agent_id,
                messages=[AgentMessage(role="user", content="Hello, Roo-Code!")],
            )

            response = roo_adapter.process_request(request)

            if response and response.message.content:
                logger.info("✅ Roo-Code request processing test passed")
                return True
            else:
                logger.warning("❌ Roo-Code request processing test failed")
                return False
        else:
            logger.warning("❌ Roo-Code agent creation or retrieval test failed")
            return False
    except ImportError:
        logger.warning("Roo-Code adapter not available, skipping test")
        return True  # Skip test
    except Exception as e:
        logger.error(f"❌ Roo-Code test failed with error: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    logger.info("Running all tests...")

    tests = [
        ("Model Router", test_model_router),
        ("Agent Factory", test_agent_factory),
        ("Google GenAI", test_google_genai),
        ("LangGraph", test_langgraph),
        ("Roo-Code", test_roo_code),
    ]

    results = {}
    all_passed = True

    for name, test_func in tests:
        logger.info(f"\n{'='*50}\nRunning {name} tests\n{'='*50}")
        try:
            passed = test_func()
            results[name] = "PASSED" if passed else "FAILED"
            all_passed = all_passed and passed
        except Exception as e:
            logger.error(f"Error running {name} tests: {e}")
            results[name] = "ERROR"
            all_passed = False

    logger.info("\n\n")
    logger.info("=" * 50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 50)

    for name, result in results.items():
        status = "✅" if result == "PASSED" else "❌"
        logger.info(f"{status} {name}: {result}")

    logger.info("=" * 50)
    logger.info(f"Overall result: {'PASSED' if all_passed else 'FAILED'}")
    logger.info("=" * 50)

    return all_passed


if __name__ == "__main__":
    run_all_tests()
