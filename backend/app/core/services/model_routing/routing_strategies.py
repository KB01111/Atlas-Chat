"""
Routing strategies for model selection.
"""

from typing import Dict, Any, List, Optional, Protocol
from abc import ABC, abstractmethod
import re

from .model_specs import ModelSpecs, ModelSpecification
from .performance_metrics import PerformanceMetrics


class RoutingStrategy(ABC):
    """Abstract base class for routing strategies."""

    @abstractmethod
    def score_model(self, 
                  model_id: str,
                  message: str,
                  history: List[Dict[str, str]],
                  context: Dict[str, Any]) -> float:
        """
        Score a model based on the strategy.

        Args:
            model_id: Model ID
            message: User message
            history: Conversation history
            context: Additional context

        Returns:
            Score for the model (higher is better)
        """
        pass


class TaskBasedStrategy(RoutingStrategy):
    """Strategy that scores models based on task type."""

    def __init__(self, model_specs: ModelSpecs):
        """
        Initialize task-based strategy.

        Args:
            model_specs: Model specifications
        """
        self.model_specs = model_specs
        self.task_keywords = {
            "coding": [
                "code", "function", "programming", "algorithm", "bug", "error",
                "javascript", "python", "java", "c++", "typescript", "html", "css",
                "api", "database", "sql", "debug", "compiler", "runtime", "syntax",
                "library", "framework", "git", "github", "repository", "commit"
            ],
            "writing": [
                "write", "story", "creative", "poem", "essay", "blog", "article",
                "content", "draft", "edit", "proofread", "grammar", "spelling",
                "narrative", "character", "plot", "setting", "theme", "tone",
                "style", "voice", "audience", "paragraph", "sentence", "word"
            ],
            "research": [
                "research", "information", "data", "analysis", "find", "search",
                "investigate", "explore", "discover", "learn", "study", "examine",
                "review", "evaluate", "assess", "compare", "contrast", "synthesize",
                "summarize", "report", "paper", "source", "citation", "reference"
            ],
            "math": [
                "math", "calculation", "equation", "formula", "solve", "compute",
                "algebra", "calculus", "geometry", "statistics", "probability",
                "number", "variable", "function", "graph", "plot", "chart",
                "dataset", "regression", "correlation", "distribution", "average"
            ],
            "general": [
                "help", "question", "answer", "explain", "describe", "define",
                "summarize", "list", "example", "suggestion", "recommendation",
                "opinion", "thought", "idea", "concept", "understand", "clarify",
                "elaborate", "detail", "overview", "summary", "introduction"
            ]
        }

    def score_model(self, 
                  model_id: str,
                  message: str,
                  history: List[Dict[str, str]],
                  context: Dict[str, Any]) -> float:
        """
        Score a model based on task type.

        Args:
            model_id: Model ID
            message: User message
            history: Conversation history
            context: Additional context

        Returns:
            Score for the model (higher is better)
        """
        # Get model spec
        spec = self.model_specs.get_spec(model_id)
        if not spec:
            return 0.0

        # Determine task type
        task_type = self._analyze_task_type(message, history)

        # Base score
        score = 0.0

        # Adjust score based on task type
        if task_type in spec.strengths:
            score += 2.0

        return score

    def _analyze_task_type(self, 
                         message: str, 
                         history: List[Dict[str, str]]) -> str:
        """
        Analyze message to determine task type.

        Args:
            message: User message
            history: Conversation history

        Returns:
            Task type
        """
        # Convert message to lowercase for case-insensitive matching
        message_lower = message.lower()

        # Count keyword matches for each task type
        task_scores = {}
        for task_type, keywords in self.task_keywords.items():
            count = sum(1 for keyword in keywords if keyword in message_lower)
            task_scores[task_type] = count

        # Get task type with highest score
        max_score = 0
        max_task = "general"

        for task_type, score in task_scores.items():
            if score > max_score:
                max_score = score
                max_task = task_type

        return max_task


class ComplexityBasedStrategy(RoutingStrategy):
    """Strategy that scores models based on message complexity."""

    def __init__(self, model_specs: ModelSpecs):
        """
        Initialize complexity-based strategy.

        Args:
            model_specs: Model specifications
        """
        self.model_specs = model_specs

    def score_model(self, 
                  model_id: str,
                  message: str,
                  history: List[Dict[str, str]],
                  context: Dict[str, Any]) -> float:
        """
        Score a model based on message complexity.

        Args:
            model_id: Model ID
            message: User message
            history: Conversation history
            context: Additional context

        Returns:
            Score for the model (higher is better)
        """
        # Get model spec
        spec = self.model_specs.get_spec(model_id)
        if not spec:
            return 0.0

        # Determine message complexity
        complexity = self._estimate_complexity(message, history)

        # Base score
        score = 0.0

        # Adjust score based on complexity
        if complexity == "high" and spec.handles_complexity:
            score += 2.0
        elif complexity == "medium" and spec.handles_complexity:
            score += 1.0
        elif complexity == "low" and spec.efficient_for_simple:
            score += 1.5

        return score

    def _estimate_complexity(self, 
                           message: str, 
                           history: List[Dict[str, str]]) -> str:
        """
        Estimate message complexity.

        Args:
            message: User message
            history: Conversation history

        Returns:
            Complexity level: "low", "medium", or "high"
        """
        # Calculate complexity based on multiple factors

        # 1. Message length
        length_score = 0
        if len(message) > 500:
            length_score = 2  # high
        elif len(message) > 100:
            length_score = 1  # medium
        else:
            length_score = 0  # low

        # 2. Sentence complexity
        sentences = re.split(r'[.!?]+', message)
        avg_words_per_sentence = sum(len(s.split()) for s in sentences if s) / max(len(sentences), 1)

        sentence_score = 0
        if avg_words_per_sentence > 20:
            sentence_score = 2  # high
        elif avg_words_per_sentence > 10:
            sentence_score = 1  # medium
        else:
            sentence_score = 0  # low

        # 3. Vocabulary complexity
        complex_word_patterns = [
            r'\b\w{10,}\b',  # Words with 10+ characters
            r'\b(?:therefore|consequently|furthermore|nevertheless|accordingly)\b',  # Complex conjunctions
            r'\b(?:analyze|synthesize|evaluate|hypothesize|theorize)\b'  # Complex verbs
        ]

        complex_word_count = sum(len(re.findall(pattern, message, re.IGNORECASE)) for pattern in complex_word_patterns)

        vocabulary_score = 0
        if complex_word_count > 5:
            vocabulary_score = 2  # high
        elif complex_word_count > 2:
            vocabulary_score = 1  # medium
        else:
            vocabulary_score = 0  # low

        # 4. Conversation history complexity
        history_score = 0
        if len(history) > 10:
            history_score = 2  # high
        elif len(history) > 5:
            history_score = 1  # medium
        else:
            history_score = 0  # low

        # Calculate overall complexity score
        total_score = length_score + sentence_score + vocabulary_score + history_score

        if total_score >= 5:
            return "high"
        elif total_score >= 2:
            return "medium"
        else:
            return "low"


class CostAwareStrategy(RoutingStrategy):
    """Strategy that scores models based on cost efficiency."""

    def __init__(self, model_specs: ModelSpecs):
        """
        Initialize cost-aware strategy.

        Args:
            model_specs: Model specifications
        """
        self.model_specs = model_specs

    def score_model(self, 
                  model_id: str,
                  message: str,
                  history: List[Dict[str, str]],
                  context: Dict[str, Any]) -> float:
        """
        Score a model based on cost efficiency.

        Args:
            model_id: Model ID
            message: User message
            history: Conversation history
            context: Additional context

        Returns:
            Score for the model (higher is better)
        """
        # Get model spec
        spec = self.model_specs.get_spec(model_id)
        if not spec:
            return 0.0

        # Base score (inverse of cost, so lower cost = higher score)
        if spec.cost_per_token > 0:
            # Normalize to 0-2 range (assuming max cost is 0.02 per token)
            score = 2.0 * (1.0 - min(spec.cost_per_token / 0.02, 1.0))
        else:
            score = 0.0

        return score


class PerformanceBasedStrategy(RoutingStrategy):
    """Strategy that scores models based on performance metrics."""

    def __init__(self, 
               model_specs: ModelSpecs,
               performance_metrics: PerformanceMetrics):
        """
        Initialize performance-based strategy.

        Args:
            model_specs: Model specifications
            performance_metrics: Performance metrics
        """
        self.model_specs = model_specs
        self.performance_metrics = performance_metrics

    def score_model(self, 
                  model_id: str,
                  message: str,
                  history: List[Dict[str, str]],
                  context: Dict[str, Any]) -> float:
        """
        Score a model based on performance metrics.

        Args:
            model_id: Model ID
            message: User message
            history: Conversation history
            context: Additional context

        Returns:
            Score for the model (higher is better)
        """
        # Get model metrics
        metrics = self.performance_metrics.get_metrics(model_id)
        if not metrics:
            return 0.0

        # Base score
        score = 0.0

        # Adjust score based on success rate (0-1 range)
        score += metrics.success_rate

        # Adjust score based on latency (lower is better)
        # Normalize to 0-1 range (assuming max acceptable latency is 5 seconds)
        latency_score = 1.0 - min(metrics.avg_latency / 5.0, 1.0)
        score += latency_score

        return score


class UserPreferenceStrategy(RoutingStrategy):
    """Strategy that scores models based on user preferences."""

    def __init__(self, model_specs: ModelSpecs):
        """
        Initialize user preference strategy.

        Args:
            model_specs: Model specifications
        """
        self.model_specs = model_specs
        self.user_preferences = {}

    def score_model(self, 
                  model_id: str,
                  message: str,
                  history: List[Dict[str, str]],
                  context: Dict[str, Any]) -> float:
        """
        Score a model based on user preferences.

        Args:
            model_id: Model ID
            message: User message
            history: Conversation history
            context: Additional context

        Returns:
            Score for the model (higher is better)
        """
        # Get user ID from context
        user_id = context.get("user_id") if context else None

        if not user_id or user_id not in self.user_preferences:
            return 0.0

        # Get user preferences
        preferences = self.user_preferences[user_id]

        # Base score
        score = 0.0

        # Check if model is preferred
        if preferences.get("preferred_model") == model_id:
            # High score for preferred model
            score += 3.0

            # Even higher if strict preference
            if preferences.get("strict_preference", False):
                score += 7.0  # Effectively guarantees selection

        return score

    def set_user_preference(self, 
                          user_id: str,
                          preferred_model: str,
                          strict_preference: bool = False) -> None:
        """
        Set user preference for model selection.

        Args:
            user_id: User ID
            preferred_model: Preferred model ID
            strict_preference: Whether to strictly use the preferred model
        """
        self.user_preferences[user_id] = {
            "preferred_model": preferred_model,
            "strict_preference": strict_preference
        }

    def get_user_preference(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user preference for model selection.

        Args:
            user_id: User ID

        Returns:
            User preference or None if not found
        """
        return self.user_preferences.get(user_id)

    def clear_user_preference(self, user_id: str) -> None:
        """
        Clear user preference for model selection.

        Args:
            user_id: User ID
        """
        if user_id in self.user_preferences:
            del self.user_preferences[user_id]


class CompositeStrategy(RoutingStrategy):
    """Strategy that combines multiple strategies with weights."""

    def __init__(self, strategies: List[RoutingStrategy], weights: List[float] = None):
        """
        Initialize composite strategy.

        Args:
            strategies: List of strategies
            weights: Optional list of weights (must match strategies length)
        """
        self.strategies = strategies

        # Default to equal weights if not provided
        if weights is None:
            self.weights = [1.0] * len(strategies)
        else:
            if len(weights) != len(strategies):
                raise ValueError("Weights must match strategies length")
            self.weights = weights

    def score_model(self, 
                  model_id: str,
                  message: str,
                  history: List[Dict[str, str]],
                  context: Dict[str, Any]) -> float:
        """
        Score a model based on combined strategies.

        Args:
            model_id: Model ID
            message: User message
            history: Conversation history
            context: Additional context

        Returns:
            Score for the model (higher is better)
        """
        # Get scores from all strategies
        scores = [
            strategy.score_model(model_id, message, history, context)
            for strategy in self.strategies
        ]

        # Calculate weighted sum
        weighted_sum = sum(score * weight for score, weight in zip(scores, self.weights))

        return weighted_sum
