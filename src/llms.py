from langchain_anthropic import ChatAnthropic

from src.settings import settings


def get_vision_model() -> ChatAnthropic:
    """Get configured Anthropic model for image analysis."""
    return ChatAnthropic(
        temperature=0,
        model=settings.anthropic_model,
        api_key=settings.anthropic_api_key,
        max_retries=5,
    )


def get_text_model() -> ChatAnthropic:
    """Get configured Anthropic model for text generation."""
    return ChatAnthropic(
        temperature=0,
        model=settings.anthropic_model,
        api_key=settings.anthropic_api_key,
        max_retries=5,
    )
