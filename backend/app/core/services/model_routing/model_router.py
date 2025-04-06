"""
Intelligent model router for selecting the most appropriate AI model.
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
import time

from .model_specs import ModelSpecs, ModelSpecification
from .performance_metrics import PerformanceMetrics
from .routing_strategies import (
    RoutingStrategy,
    TaskBasedStrategy,
    ComplexityBasedStrategy,
    CostAwareStrategy,
    PerformanceBasedStrategy,
    UserPreferenceStrategy,
    CompositeStrategy,
)


class ModelRouter:
    """Intelligent model router for selecting the most appropriate AI model."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize model router.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger("model_router")

        # Initialize components
        self.model_specs = ModelSpecs(self.config.get("model_specs"))
        self.performance_metrics = PerformanceMetrics(
            self.config.get("performance_metrics")
        )

        # Initialize strategies
        self.task_strategy = TaskBasedStrategy(self.model_specs)
        self.complexity_strategy = ComplexityBasedStrategy(self.model_specs)
        self.cost_strategy = CostAwareStrategy(self.model_specs)
        self.performance_strategy = PerformanceBasedStrategy(
            self.model_specs, self.performance_metrics
        )
        self.user_preference_strategy = UserPreferenceStrategy(self.model_specs)

        # Create composite strategy with default weights
        self.strategy = self._create_composite_strategy()

        # Default model (fallback)
        self.default_model = self.config.get("default_model", "gpt-4o")

        # Fallback chain
        self.fallback_chain = self.config.get(
            "fallback_chain",
            ["gpt-4o", "claude-3-5-sonnet", "gemini-2-5-pro", "gpt-3.5-turbo"],
        )

        # Enable fallback
        self.enable_fallback = self.config.get("enable_fallback", True)

    def select_model(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        task_type: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Select the most appropriate model based on context.

        Args:
            message: User message
            history: Optional conversation history
            task_type: Optional type of task
            user_id: Optional user ID for preferences
            context: Optional additional context

        Returns:
            Selected model ID
        """
        # Initialize history if None
        if history is None:
            history = []

        # Initialize context if None
        if context is None:
            context = {}

        # Add user_id to context if provided
        if user_id:
            context["user_id"] = user_id

        # Add task_type to context if provided
        if task_type:
            context["task_type"] = task_type

        # Get available models
        available_models = self._get_available_models()

        if not available_models:
            self.logger.warning("No available models found, using default model")
            return self.default_model

        # Score models
        scored_models = self._score_models(
            models=available_models, message=message, history=history, context=context
        )

        # Select highest-scoring model
        selected_model = scored_models[0][0]

        # Log selection
        self._log_selection(
            selected_model=selected_model,
            scored_models=scored_models,
            message=message,
            context=context,
        )

        return selected_model

    def record_model_performance(
        self, model_id: str, success: bool, duration: float, tokens: int = 0
    ) -> None:
        """
        Record model performance for future routing decisions.

        Args:
            model_id: Model ID
            success: Whether the request was successful
            duration: Request duration in seconds
            tokens: Number of tokens used
        """
        self.performance_metrics.record_request(
            model_id=model_id, success=success, duration=duration, tokens=tokens
        )

    def set_user_preference(
        self, user_id: str, preferred_model: str, strict_preference: bool = False
    ) -> None:
        """
        Set user preference for model selection.

        Args:
            user_id: User ID
            preferred_model: Preferred model ID
            strict_preference: Whether to strictly use the preferred model
        """
        self.user_preference_strategy.set_user_preference(
            user_id=user_id,
            preferred_model=preferred_model,
            strict_preference=strict_preference,
        )

    def get_user_preference(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user preference for model selection.

        Args:
            user_id: User ID

        Returns:
            User preference or None if not found
        """
        return self.user_preference_strategy.get_user_preference(user_id)

    def clear_user_preference(self, user_id: str) -> None:
        """
        Clear user preference for model selection.

        Args:
            user_id: User ID
        """
        self.user_preference_strategy.clear_user_preference(user_id)

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models with metadata.

        Returns:
            List of available models with metadata
        """
        models = []

        for model_id, spec in self.model_specs.get_all_specs().items():
            # Get performance metrics if available
            metrics = self.performance_metrics.get_metrics(model_id)

            models.append(
                {
                    "model_id": model_id,
                    "provider": spec.provider,
                    "capabilities": spec.strengths,
                    "capability_score": spec.capability_score,
                    "cost_per_token": spec.cost_per_token,
                    "supports_tools": spec.supports_tools,
                    "supports_vision": spec.supports_vision,
                    "context_window": spec.context_window,
                    "description": spec.description,
                    "performance": {
                        "avg_latency": metrics.avg_latency if metrics else None,
                        "success_rate": metrics.success_rate if metrics else None,
                        "avg_tokens_per_request": metrics.avg_tokens_per_request
                        if metrics
                        else None,
                    }
                    if metrics
                    else None,
                }
            )

        return models

    def get_model_for_task(self, task_type: str) -> str:
        """
        Get the best model for a specific task type.

        Args:
            task_type: Task type (e.g., "coding", "writing", "research")

        Returns:
            Model ID
        """
        # Get models with this task type as a strength
        models = self.model_specs.get_models_by_strength(task_type)

        if not models:
            self.logger.warning(
                f"No models found for task type {task_type}, using default model"
            )
            return self.default_model

        # Sort by capability score (descending)
        models.sort(key=lambda x: x.capability_score, reverse=True)

        return models[0].model_id

    def get_fallback_model(self, current_model: str) -> Optional[str]:
        """
        Get fallback model if current model fails.

        Args:
            current_model: Current model ID

        Returns:
            Fallback model ID or None if no fallback available
        """
        if not self.enable_fallback:
            return None

        # Find current model in fallback chain
        try:
            current_index = self.fallback_chain.index(current_model)
        except ValueError:
            # If current model not in chain, use first model in chain
            return self.fallback_chain[0] if self.fallback_chain else None

        # Get next model in chain
        if current_index < len(self.fallback_chain) - 1:
            return self.fallback_chain[current_index + 1]
        else:
            return None

    def update_strategy_weights(self, weights: Dict[str, float]) -> None:
        """
        Update weights for the composite strategy.

        Args:
            weights: Dictionary of strategy names and weights
        """
        # Create new composite strategy with updated weights
        self.strategy = self._create_composite_strategy(weights)

    def _create_composite_strategy(
        self, weights: Optional[Dict[str, float]] = None
    ) -> CompositeStrategy:
        """
        Create composite strategy with specified weights.

        Args:
            weights: Optional dictionary of strategy names and weights

        Returns:
            Composite strategy
        """
        # Default weights
        default_weights = {
            "task": 1.0,
            "complexity": 1.0,
            "cost": 0.5,
            "performance": 1.0,
            "user_preference": 2.0,
        }

        # Use provided weights or defaults
        if weights is None:
            weights = default_weights
        else:
            # Merge with defaults (missing weights use defaults)
            for key, value in default_weights.items():
                if key not in weights:
                    weights[key] = value

        # Create composite strategy
        return CompositeStrategy(
            strategies=[
                self.task_strategy,
                self.complexity_strategy,
                self.cost_strategy,
                self.performance_strategy,
                self.user_preference_strategy,
            ],
            weights=[
                weights["task"],
                weights["complexity"],
                weights["cost"],
                weights["performance"],
                weights["user_preference"],
            ],
        )

    def _get_available_models(self) -> List[str]:
        """
        Get list of available model IDs.

        Returns:
            List of available model IDs
        """
        # In a real implementation, this would check model availability
        # For now, just return all models
        return list(self.model_specs.get_all_specs().keys())

    def _score_models(
        self,
        models: List[str],
        message: str,
        history: List[Dict[str, str]],
        context: Dict[str, Any],
    ) -> List[Tuple[str, float]]:
        """
        Score models based on the current strategy.

        Args:
            models: List of model IDs
            message: User message
            history: Conversation history
            context: Additional context

        Returns:
            List of (model_id, score) tuples, sorted by score (descending)
        """
        # Score each model
        scored_models = []

        for model_id in models:
            score = self.strategy.score_model(
                model_id=model_id, message=message, history=history, context=context
            )

            scored_models.append((model_id, score))

        # Sort by score (descending)
        scored_models.sort(key=lambda x: x[1], reverse=True)

        return scored_models

    def _log_selection(
        self,
        selected_model: str,
        scored_models: List[Tuple[str, float]],
        message: str,
        context: Dict[str, Any],
    ) -> None:
        """
        Log model selection for analysis.

        Args:
            selected_model: Selected model ID
            scored_models: List of (model_id, score) tuples
            message: User message
            context: Additional context
        """
        # Log selection details
        self.logger.info(f"Selected model: {selected_model}")
        self.logger.debug(f"Model scores: {scored_models}")
        self.logger.debug(f"Context: {context}")

        # In a real implementation, this would log to a database for analysis
