"""Language packs module for language-specific rules."""

from anti_slop_writer.language_packs.base import LanguagePack, Pattern
from anti_slop_writer.language_packs.english import EnglishPack

__all__ = [
    "LanguagePack",
    "Pattern",
    "EnglishPack",
]
