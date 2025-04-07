"""
Performance metrics for model routing.
"""

import json
import os
import time
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ModelMetrics(BaseModel):
    """Metrics for a specific model."""

    model_id: str
    avg_latency: float = 0.0
    success_rate: float = 0.0
    avg_tokens_per_request: float = 0.0
    total_requests: int = 0
    success_count: int = 0
    error_count: int = 0
    total_tokens: int = 0
    total_duration: float = 0.0
    last_updated: float = 0.0


class PerformanceMetrics:
    """Repository of performance metrics for models."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize performance metrics.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.metrics_file = self.config.get("metrics_file", "model_metrics.json")
        self.metrics = self._load_metrics()

    def get_metrics(self, model_id: str) -> Optional[ModelMetrics]:
        """
        Get metrics for a model.

        Args:
            model_id: Model ID

        Returns:
            Model metrics or None if not found
        """
        return self.metrics.get(model_id)

    def get_all_metrics(self) -> Dict[str, ModelMetrics]:
        """
        Get all model metrics.

        Returns:
            Dictionary of model metrics
        """
        return self.metrics

    def record_request(
        self, model_id: str, success: bool, duration: float, tokens: int = 0
    ) -> None:
        """
        Record a request to a model.

        Args:
            model_id: Model ID
            success: Whether the request was successful
            duration: Request duration in seconds
            tokens: Number of tokens used
        """
        # Create metrics if not exists
        if model_id not in self.metrics:
            self.metrics[model_id] = ModelMetrics(model_id=model_id)

        # Update metrics
        metrics = self.metrics[model_id]
        metrics.total_requests += 1

        if success:
            metrics.success_count += 1
        else:
            metrics.error_count += 1

        metrics.total_duration += duration
        metrics.avg_latency = metrics.total_duration / metrics.total_requests
        metrics.success_rate = metrics.success_count / metrics.total_requests

        if tokens > 0:
            metrics.total_tokens += tokens
            metrics.avg_tokens_per_request = (
                metrics.total_tokens / metrics.total_requests
            )

        metrics.last_updated = time.time()

        # Save metrics
        self._save_metrics()

    def reset_metrics(self, model_id: Optional[str] = None) -> None:
        """
        Reset metrics for a model or all models.

        Args:
            model_id: Optional model ID to reset, or None to reset all
        """
        if model_id:
            if model_id in self.metrics:
                self.metrics[model_id] = ModelMetrics(model_id=model_id)
        else:
            self.metrics = {}

        # Save metrics
        self._save_metrics()

    def _load_metrics(self) -> Dict[str, ModelMetrics]:
        """
        Load metrics from file.

        Returns:
            Dictionary of model metrics
        """
        metrics = {}

        # Try to load from file
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file) as f:
                    data = json.load(f)

                for model_id, metrics_dict in data.items():
                    metrics[model_id] = ModelMetrics(**metrics_dict)
            except Exception as e:
                print(f"Error loading metrics: {e}")

        # Load default metrics if no file or error
        if not metrics:
            metrics = self._load_default_metrics()

        return metrics

    def _save_metrics(self) -> None:
        """Save metrics to file."""
        try:
            with open(self.metrics_file, "w") as f:
                data = {
                    model_id: metrics.dict()
                    for model_id, metrics in self.metrics.items()
                }
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving metrics: {e}")

    def _load_default_metrics(self) -> Dict[str, ModelMetrics]:
        """
        Load default metrics.

        Returns:
            Dictionary of default model metrics
        """
        # Default metrics based on estimated performance
        return {
            "gpt-4o": ModelMetrics(
                model_id="gpt-4o",
                avg_latency=2.5,
                success_rate=0.95,
                avg_tokens_per_request=800,
                total_requests=100,
                success_count=95,
                error_count=5,
                total_tokens=80000,
                total_duration=250.0,
                last_updated=time.time(),
            ),
            "gpt-3.5-turbo": ModelMetrics(
                model_id="gpt-3.5-turbo",
                avg_latency=1.2,
                success_rate=0.9,
                avg_tokens_per_request=600,
                total_requests=200,
                success_count=180,
                error_count=20,
                total_tokens=120000,
                total_duration=240.0,
                last_updated=time.time(),
            ),
            "claude-3-5-sonnet": ModelMetrics(
                model_id="claude-3-5-sonnet",
                avg_latency=2.8,
                success_rate=0.93,
                avg_tokens_per_request=850,
                total_requests=100,
                success_count=93,
                error_count=7,
                total_tokens=85000,
                total_duration=280.0,
                last_updated=time.time(),
            ),
            "claude-3-opus": ModelMetrics(
                model_id="claude-3-opus",
                avg_latency=3.5,
                success_rate=0.96,
                avg_tokens_per_request=900,
                total_requests=50,
                success_count=48,
                error_count=2,
                total_tokens=45000,
                total_duration=175.0,
                last_updated=time.time(),
            ),
            "gemini-2-5-pro": ModelMetrics(
                model_id="gemini-2-5-pro",
                avg_latency=2.2,
                success_rate=0.92,
                avg_tokens_per_request=750,
                total_requests=100,
                success_count=92,
                error_count=8,
                total_tokens=75000,
                total_duration=220.0,
                last_updated=time.time(),
            ),
            "deepseek-v3": ModelMetrics(
                model_id="deepseek-v3",
                avg_latency=2.6,
                success_rate=0.91,
                avg_tokens_per_request=820,
                total_requests=50,
                success_count=45,
                error_count=5,
                total_tokens=41000,
                total_duration=130.0,
                last_updated=time.time(),
            ),
        }
