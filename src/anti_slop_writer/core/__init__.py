"""Core module for text rewriting functionality."""

from anti_slop_writer.core.config import (
    get_provider_config,
    get_settings,
    load_config_file,
)
from anti_slop_writer.core.models import (
    RewriteContext,
    RewriteRequest,
    RewriteResult,
)
from anti_slop_writer.core.processor import TextProcessor
from anti_slop_writer.core.rewriter import Rewriter
from anti_slop_writer.core.rule_engine import RuleEngine

__all__ = [
    "RewriteRequest",
    "RewriteResult",
    "RewriteContext",
    "Rewriter",
    "RuleEngine",
    "TextProcessor",
    "get_settings",
    "get_provider_config",
    "load_config_file",
]
