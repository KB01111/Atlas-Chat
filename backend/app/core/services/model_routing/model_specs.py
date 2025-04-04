"""
Model specifications for different AI models.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ModelSpecification(BaseModel):
    """Specification for an AI model."""
    
    model_id: str
    provider: str
    capability_score: float = Field(ge=0, le=10)
    strengths: List[str] = []
    handles_complexity: bool = False
    efficient_for_simple: bool = False
    cost_per_token: float = 0.0
    max_tokens: int = 8192
    supports_tools: bool = False
    supports_vision: bool = False
    supports_streaming: bool = True
    supports_function_calling: bool = False
    context_window: int = 8192
    description: str = ""


class ModelSpecs:
    """Repository of model specifications."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize model specifications.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.specs = self._load_model_specs()
        
    def get_spec(self, model_id: str) -> Optional[ModelSpecification]:
        """
        Get specification for a model.
        
        Args:
            model_id: Model ID
            
        Returns:
            Model specification or None if not found
        """
        return self.specs.get(model_id)
        
    def get_all_specs(self) -> Dict[str, ModelSpecification]:
        """
        Get all model specifications.
        
        Returns:
            Dictionary of model specifications
        """
        return self.specs
        
    def get_models_by_provider(self, provider: str) -> List[ModelSpecification]:
        """
        Get models by provider.
        
        Args:
            provider: Provider name
            
        Returns:
            List of model specifications
        """
        return [
            spec for spec in self.specs.values()
            if spec.provider.lower() == provider.lower()
        ]
        
    def get_models_by_strength(self, strength: str) -> List[ModelSpecification]:
        """
        Get models by strength.
        
        Args:
            strength: Strength category
            
        Returns:
            List of model specifications
        """
        return [
            spec for spec in self.specs.values()
            if strength in spec.strengths
        ]
        
    def get_models_by_capability(self, min_score: float = 0.0) -> List[ModelSpecification]:
        """
        Get models by capability score.
        
        Args:
            min_score: Minimum capability score
            
        Returns:
            List of model specifications
        """
        return [
            spec for spec in self.specs.values()
            if spec.capability_score >= min_score
        ]
        
    def add_spec(self, spec: ModelSpecification) -> None:
        """
        Add a model specification.
        
        Args:
            spec: Model specification
        """
        self.specs[spec.model_id] = spec
        
    def update_spec(self, model_id: str, updates: Dict[str, Any]) -> Optional[ModelSpecification]:
        """
        Update a model specification.
        
        Args:
            model_id: Model ID
            updates: Updates to apply
            
        Returns:
            Updated model specification or None if not found
        """
        if model_id not in self.specs:
            return None
            
        # Get current spec
        current = self.specs[model_id]
        
        # Apply updates
        updated_dict = current.dict()
        updated_dict.update(updates)
        
        # Create new spec
        updated = ModelSpecification(**updated_dict)
        
        # Update specs
        self.specs[model_id] = updated
        
        return updated
        
    def _load_model_specs(self) -> Dict[str, ModelSpecification]:
        """
        Load model specifications.
        
        Returns:
            Dictionary of model specifications
        """
        # Default specifications
        default_specs = {
            # OpenAI Models
            "gpt-4-5-preview": ModelSpecification(
                model_id="gpt-4-5-preview",
                provider="openai",
                capability_score=9.5,
                strengths=["coding", "writing", "research", "general", "math"],
                handles_complexity=True,
                efficient_for_simple=False,
                cost_per_token=0.01,
                max_tokens=16384,
                supports_tools=True,
                supports_vision=True,
                supports_function_calling=True,
                context_window=128000,
                description="OpenAI's largest and most capable GPT model"
            ),
            "gpt-4o": ModelSpecification(
                model_id="gpt-4o",
                provider="openai",
                capability_score=9.0,
                strengths=["coding", "writing", "research", "general"],
                handles_complexity=True,
                efficient_for_simple=False,
                cost_per_token=0.005,
                max_tokens=8192,
                supports_tools=True,
                supports_vision=True,
                supports_function_calling=True,
                context_window=128000,
                description="OpenAI's fast, intelligent, flexible GPT model"
            ),
            "gpt-4o-mini": ModelSpecification(
                model_id="gpt-4o-mini",
                provider="openai",
                capability_score=8.0,
                strengths=["coding", "writing", "general"],
                handles_complexity=True,
                efficient_for_simple=True,
                cost_per_token=0.0015,
                max_tokens=8192,
                supports_tools=True,
                supports_vision=True,
                supports_function_calling=True,
                context_window=128000,
                description="Smaller, faster version of GPT-4o"
            ),
            "gpt-4-turbo": ModelSpecification(
                model_id="gpt-4-turbo",
                provider="openai",
                capability_score=8.5,
                strengths=["coding", "writing", "research", "general"],
                handles_complexity=True,
                efficient_for_simple=False,
                cost_per_token=0.003,
                max_tokens=4096,
                supports_tools=True,
                supports_vision=True,
                supports_function_calling=True,
                context_window=128000,
                description="OpenAI's GPT-4 Turbo model"
            ),
            "gpt-3.5-turbo": ModelSpecification(
                model_id="gpt-3.5-turbo",
                provider="openai",
                capability_score=7.0,
                strengths=["general", "writing"],
                handles_complexity=False,
                efficient_for_simple=True,
                cost_per_token=0.0005,
                max_tokens=4096,
                supports_tools=True,
                supports_vision=False,
                supports_function_calling=True,
                context_window=16385,
                description="OpenAI's GPT-3.5 Turbo model"
            ),
            "o3-mini": ModelSpecification(
                model_id="o3-mini",
                provider="openai",
                capability_score=7.5,
                strengths=["general", "coding"],
                handles_complexity=False,
                efficient_for_simple=True,
                cost_per_token=0.0005,
                max_tokens=4096,
                supports_tools=True,
                supports_vision=False,
                supports_function_calling=True,
                context_window=16385,
                description="Fast, flexible, intelligent reasoning model"
            ),
            
            # Anthropic Models
            "claude-3-7-sonnet": ModelSpecification(
                model_id="claude-3-7-sonnet",
                provider="anthropic",
                capability_score=9.0,
                strengths=["writing", "research", "general", "coding"],
                handles_complexity=True,
                efficient_for_simple=False,
                cost_per_token=0.003,
                max_tokens=128000,  # Extended output capability
                supports_tools=True,
                supports_vision=True,
                supports_function_calling=True,
                context_window=200000,
                description="Anthropic's Claude 3.7 Sonnet model with hybrid reasoning and state-of-the-art coding skills"
            ),
            "claude-3-5-sonnet": ModelSpecification(
                model_id="claude-3-5-sonnet",
                provider="anthropic",
                capability_score=8.5,
                strengths=["writing", "research", "general"],
                handles_complexity=True,
                efficient_for_simple=False,
                cost_per_token=0.003,
                max_tokens=4096,
                supports_tools=True,
                supports_vision=True,
                supports_function_calling=True,
                context_window=200000,
                description="Anthropic's Claude 3.5 Sonnet model"
            ),
            "claude-3-opus": ModelSpecification(
                model_id="claude-3-opus",
                provider="anthropic",
                capability_score=9.0,
                strengths=["writing", "research", "general"],
                handles_complexity=True,
                efficient_for_simple=False,
                cost_per_token=0.015,
                max_tokens=4096,
                supports_tools=True,
                supports_vision=True,
                supports_function_calling=True,
                context_window=200000,
                description="Anthropic's Claude 3 Opus model"
            ),
            "claude-3-sonnet": ModelSpecification(
                model_id="claude-3-sonnet",
                provider="anthropic",
                capability_score=8.0,
                strengths=["writing", "research", "general"],
                handles_complexity=True,
                efficient_for_simple=False,
                cost_per_token=0.003,
                max_tokens=4096,
                supports_tools=True,
                supports_vision=True,
                supports_function_calling=True,
                context_window=200000,
                description="Anthropic's Claude 3 Sonnet model"
            ),
            "claude-3-haiku": ModelSpecification(
                model_id="claude-3-haiku",
                provider="anthropic",
                capability_score=7.5,
                strengths=["general", "writing"],
                handles_complexity=False,
                efficient_for_simple=True,
                cost_per_token=0.00025,
                max_tokens=4096,
                supports_tools=True,
                supports_vision=True,
                supports_function_calling=True,
                context_window=200000,
                description="Anthropic's Claude 3 Haiku model"
            ),
            
            # Google Models
            "gemini-2-5-pro": ModelSpecification(
                model_id="gemini-2-5-pro",
                provider="google",
                capability_score=9.0,
                strengths=["coding", "research", "general", "math"],
                handles_complexity=True,
                efficient_for_simple=False,
                cost_per_token=0.0025,
                max_tokens=8192,
                supports_tools=True,
                supports_vision=True,
                supports_function_calling=True,
                context_window=1000000,  # 1M token context window
                description="Google's Gemini 2.5 Pro model with reasoning capabilities"
            ),
            "gemini-2-5-flash": ModelSpecification(
                model_id="gemini-2-5-flash",
                provider="google",
                capability_score=7.5,
                strengths=["general", "coding"],
                handles_complexity=False,
                efficient_for_simple=True,
                cost_per_token=0.0005,
                max_tokens=8192,
                supports_tools=True,
                supports_vision=True,
                supports_function_calling=True,
                context_window=1000000,  # 1M token context window
                description="Google's Gemini 2.5 Flash model"
            ),
            "gemini-1-5-pro": ModelSpecification(
                model_id="gemini-1-5-pro",
                provider="google",
                capability_score=8.5,
                strengths=["coding", "research", "general"],
                handles_complexity=True,
                efficient_for_simple=False,
                cost_per_token=0.0020,
                max_tokens=8192,
                supports_tools=True,
                supports_vision=True,
                supports_function_calling=True,
                context_window=2000000,  # 2M token context window
                description="Google's Gemini 1.5 Pro model with extended context window"
            ),
            "gemini-1-5-flash": ModelSpecification(
                model_id="gemini-1-5-flash",
                provider="google",
                capability_score=7.0,
                strengths=["general", "coding"],
                handles_complexity=False,
                efficient_for_simple=True,
                cost_per_token=0.0003,
                max_tokens=8192,
                supports_tools=True,
                supports_vision=True,
                supports_function_calling=True,
                context_window=1000000,  # 1M token context window
                description="Google's Gemini 1.5 Flash model"
            ),
            
            # OpenRouter Models
            "deepseek-v3": ModelSpecification(
                model_id="deepseek-v3",
                provider="openrouter",
                capability_score=8.5,
                strengths=["coding", "research"],
                handles_complexity=True,
                efficient_for_simple=False,
                cost_per_token=0.004,
                max_tokens=8192,
                supports_tools=True,
                supports_vision=False,
                supports_function_calling=True,
                context_window=32768,
                description="DeepSeek v3 model via OpenRouter"
            ),
            "deepseek-coder": ModelSpecification(
                model_id="deepseek-coder",
                provider="openrouter",
                capability_score=8.0,
                strengths=["coding"],
                handles_complexity=True,
                efficient_for_simple=False,
                cost_per_token=0.002,
                max_tokens=8192,
                supports_tools=True,
                supports_vision=False,
                supports_function_calling=True,
                context_window=32768,
                description="DeepSeek Coder model via OpenRouter"
            ),
            "mistral-large": ModelSpecification(
                model_id="mistral-large",
                provider="openrouter",
                capability_score=8.0,
                strengths=["coding", "general", "writing"],
                handles_complexity=True,
                efficient_for_simple=False,
                cost_per_token=0.002,
                max_tokens=8192,
                supports_tools=True,
                supports_vision=False,
                supports_function_calling=True,
                context_window=32768,
                description="Mistral Large model via OpenRouter"
            ),
            "llama-3-70b": ModelSpecification(
                model_id="llama-3-70b",
                provider="openrouter",
                capability_score=8.0,
                strengths=["coding", "general", "research"],
                handles_complexity=True,
                efficient_for_simple=False,
                cost_per_token=0.0015,
                max_tokens=8192,
                supports_tools=True,
                supports_vision=False,
                supports_function_calling=True,
                context_window=8192,
                description="Meta's Llama 3 70B model via OpenRouter"
            )
        }
        
        # Override with config if provided
        if "model_specs" in self.config:
            for model_id, spec_dict in self.config["model_specs"].items():
                if model_id in default_specs:
                    # Update existing spec
                    updated_dict = default_specs[model_id].dict()
                    updated_dict.update(spec_dict)
                    default_specs[model_id] = ModelSpecification(**updated_dict)
                else:
                    # Add new spec
                    default_specs[model_id] = ModelSpecification(model_id=model_id, **spec_dict)
                    
        return default_specs
