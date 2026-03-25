"""English language pack with AI pattern detection rules.

This module implements the LanguagePack interface for English text,
using patterns from references/vocabulary-banlist.md.
"""

from __future__ import annotations

import re
from typing import ClassVar

from anti_slop_writer.language_packs.base import LanguagePack, Pattern


class EnglishPack(LanguagePack):
    """English language pack for detecting AI-sounding patterns.

    Tier 1 patterns (hard ban):
    - Significance Puffers
    - Poetic Nouns
    - Promotional Adjectives
    - Opening/Closing Crutches
    - Fake Authenticity Signals
    - Chat Artifacts
    - Vague Attribution Phrases

    Tier 2 patterns (soft guidance):
    - Analytical Verbs
    - Puffery Adverbs
    - Formal Connectives
    """

    language_code: ClassVar[str] = "en"

    # Tier 1 patterns - hard ban (must not appear in output)
    tier1_patterns: ClassVar[list[Pattern]] = [
        # Significance Puffers
        Pattern(
            regex=re.compile(
                r"\b(pivotal|crucial|vital|groundbreaking|remarkable|"
                r"transformative|indelible|profound|testament|enduring|"
                r"lasting|paramount|indispensable|invaluable|quintessential)\b",
                re.IGNORECASE,
            ),
            category="significance_puffers",
        ),
        Pattern(
            regex=re.compile(r"\bkey\s+(?:factor|element|component|aspect|feature)\b", re.IGNORECASE),
            category="significance_puffers",
        ),
        Pattern(
            regex=re.compile(r"\b(deeply\s+rooted|significant\s+(?:impact|role|step))\b", re.IGNORECASE),
            category="significance_puffers",
        ),
        # Poetic Nouns
        Pattern(
            regex=re.compile(
                r"\b(tapestry|realm|paradigm|nexus|interplay|mosaic|"
                r"cornerstone|beacon|pillar|catalyst|crucible|linchpin|"
                r"hallmark|confluence|odyssey|trajectory|underpinning)\b",
                re.IGNORECASE,
            ),
            category="poetic_nouns",
        ),
        Pattern(
            regex=re.compile(r"\b(landscape|ecosystem|journey|fabric)\s+of\b", re.IGNORECASE),
            category="poetic_nouns",
        ),
        # Promotional Adjectives
        Pattern(
            regex=re.compile(
                r"\b(vibrant|comprehensive|robust|seamless|innovative|"
                r"dynamic|cutting-edge|meticulous|intricate|nuanced|"
                r"nestled|breathtaking|renowned|bustling|stunning|"
                r"multifaceted|holistic|overarching|compelling)\b",
                re.IGNORECASE,
            ),
            category="promotional_adjectives",
        ),
        Pattern(
            regex=re.compile(r"\bdiverse\s+array\b", re.IGNORECASE),
            category="promotional_adjectives",
        ),
        Pattern(
            regex=re.compile(r"\brich\s+(?:history|culture|tradition|tapestry|fabric)\b", re.IGNORECASE),
            category="promotional_adjectives",
        ),
        # Opening/Closing Crutches
        Pattern(
            regex=re.compile(
                r"\bIn\s+today's\s+(?:fast-paced\s+)?world\b",
                re.IGNORECASE,
            ),
            category="opening_crutches",
        ),
        Pattern(
            regex=re.compile(
                r"\bIn\s+the\s+ever-evolving\s+landscape\s+of\b",
                re.IGNORECASE,
            ),
            category="opening_crutches",
        ),
        Pattern(
            regex=re.compile(r"\bIn\s+an\s+era\s+(?:of|where)\b", re.IGNORECASE),
            category="opening_crutches",
        ),
        Pattern(
            regex=re.compile(r"\bAs\s+we\s+navigate\s+the\s+complexities\s+of\b", re.IGNORECASE),
            category="opening_crutches",
        ),
        Pattern(
            regex=re.compile(
                r"\b(In\s+conclusion|In\s+summary|Overall)\b",
                re.IGNORECASE,
            ),
            category="closing_crutches",
        ),
        Pattern(
            regex=re.compile(r"\bIt\s+is\s+important\s+to\s+note\s+that\b", re.IGNORECASE),
            category="closing_crutches",
        ),
        Pattern(
            regex=re.compile(r"\bIt's\s+worth\s+noting\s+that\b", re.IGNORECASE),
            category="closing_crutches",
        ),
        Pattern(
            regex=re.compile(
                r"\b(At\s+the\s+end\s+of\s+the\s+day|Without\s+further\s+ado|"
                r"In\s+a\s+nutshell|The\s+bottom\s+line\s+is|Last\s+but\s+not\s+least)\b",
                re.IGNORECASE,
            ),
            category="closing_crutches",
        ),
        # Fake Authenticity Signals
        Pattern(
            regex=re.compile(r"\bBut\s+honestly[,.]?\b", re.IGNORECASE),
            category="fake_authenticity",
        ),
        Pattern(
            regex=re.compile(r"\bHere's\s+the\s+(?:truth|thing)\s*:\b", re.IGNORECASE),
            category="fake_authenticity",
        ),
        Pattern(
            regex=re.compile(r"\bLet\s+me\s+be\s+clear\s*:\b", re.IGNORECASE),
            category="fake_authenticity",
        ),
        Pattern(
            regex=re.compile(
                r"\bBut\s+here's\s+where\s+it\s+gets\s+interesting\b",
                re.IGNORECASE,
            ),
            category="fake_authenticity",
        ),
        Pattern(
            regex=re.compile(r"\bThink\s+about\s+it\s+this\s+way\b", re.IGNORECASE),
            category="fake_authenticity",
        ),
        Pattern(
            regex=re.compile(r"\bLet\s+me\s+break\s+this\s+down\b", re.IGNORECASE),
            category="fake_authenticity",
        ),
        # Chat Artifacts
        Pattern(
            regex=re.compile(
                r"\b(I\s+hope\s+this\s+helps!|Of\s+course!|Certainly!|"
                r"You're\s+absolutely\s+right!|Would\s+you\s+like\s+me\s+to|"
                r"Is\s+there\s+anything\s+else|Let\s+me\s+know\s+if|"
                r"As\s+an\s+AI\s+language\s+model|I'd\s+be\s+happy\s+to|"
                r"Great\s+question!)\b",
                re.IGNORECASE,
            ),
            category="chat_artifacts",
        ),
        # Vague Attribution Phrases
        Pattern(
            regex=re.compile(
                r"\b(Experts\s+argue|Observers\s+note|Industry\s+reports\s+suggest|"
                r"According\s+to\s+some|Many\s+believe|It\s+is\s+widely\s+regarded|"
                r"Studies\s+show|Research\s+suggests)\b",
                re.IGNORECASE,
            ),
            category="vague_attribution",
        ),
    ]

    # Tier 2 patterns - soft guidance (should be reduced)
    tier2_patterns: ClassVar[list[Pattern]] = [
        # Analytical Verbs
        Pattern(
            regex=re.compile(r"\bunderscore\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="show or prove",
        ),
        Pattern(
            regex=re.compile(r"\bhighlight\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="show or point out",
        ),
        Pattern(
            regex=re.compile(r"\bshowcase\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="show or display",
        ),
        Pattern(
            regex=re.compile(r"\bfoster\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="help or build",
        ),
        Pattern(
            regex=re.compile(r"\bgarner\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="get or receive",
        ),
        Pattern(
            regex=re.compile(r"\bbolster\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="strengthen or support",
        ),
        Pattern(
            regex=re.compile(r"\bdelve\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="dig into or explore",
        ),
        Pattern(
            regex=re.compile(r"\bembark\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="start or begin",
        ),
        Pattern(
            regex=re.compile(r"\bleverage\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="use",
        ),
        Pattern(
            regex=re.compile(r"\bfacilitate\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="help or enable",
        ),
        Pattern(
            regex=re.compile(r"\butilize\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="use",
        ),
        Pattern(
            regex=re.compile(r"\bencompass\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="include",
        ),
        Pattern(
            regex=re.compile(r"\bcultivate\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="grow or build",
        ),
        Pattern(
            regex=re.compile(r"\belucidate\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="explain",
        ),
        Pattern(
            regex=re.compile(r"\billuminate\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="explain or show",
        ),
        Pattern(
            regex=re.compile(r"\bnavigate\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="handle or manage",
        ),
        Pattern(
            regex=re.compile(r"\bexemplify\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="show or illustrate",
        ),
        Pattern(
            regex=re.compile(r"\bembody\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="represent",
        ),
        Pattern(
            regex=re.compile(r"\btranscend\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="go beyond",
        ),
        Pattern(
            regex=re.compile(r"\bharness\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="use",
        ),
        Pattern(
            regex=re.compile(r"\bspearhead\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="lead",
        ),
        Pattern(
            regex=re.compile(r"\bstreamline\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="simplify",
        ),
        Pattern(
            regex=re.compile(r"\bgalvanize\b", re.IGNORECASE),
            category="analytical_verbs",
            replacement="motivate",
        ),
        # Puffery Adverbs
        Pattern(
            regex=re.compile(
                r"\b(seamlessly|meticulously|profoundly|intrinsically|"
                r"fundamentally|remarkably|notably|crucially|"
                r"undeniably|inherently|poignantly|relentlessly|"
                r"tirelessly|vividly)\b",
                re.IGNORECASE,
            ),
            category="puffery_adverbs",
        ),
        # Formal Connectives
        Pattern(
            regex=re.compile(r"\bfurthermore\b", re.IGNORECASE),
            category="formal_connectives",
            replacement="also",
        ),
        Pattern(
            regex=re.compile(r"\bmoreover\b", re.IGNORECASE),
            category="formal_connectives",
            replacement="also",
        ),
        Pattern(
            regex=re.compile(r"\bconsequently\b", re.IGNORECASE),
            category="formal_connectives",
            replacement="so",
        ),
        Pattern(
            regex=re.compile(r"\baccordingly\b", re.IGNORECASE),
            category="formal_connectives",
            replacement="so",
        ),
        Pattern(
            regex=re.compile(r"\bnonetheless\b", re.IGNORECASE),
            category="formal_connectives",
            replacement="still",
        ),
        Pattern(
            regex=re.compile(r"\bnevertheless\b", re.IGNORECASE),
            category="formal_connectives",
            replacement="still",
        ),
        Pattern(
            regex=re.compile(r"\badditionally\b", re.IGNORECASE),
            category="formal_connectives",
            replacement="also",
        ),
        Pattern(
            regex=re.compile(r"\bthus\b", re.IGNORECASE),
            category="formal_connectives",
            replacement="so",
        ),
        Pattern(
            regex=re.compile(r"\bhence\b", re.IGNORECASE),
            category="formal_connectives",
            replacement="so",
        ),
    ]

    style_prompts: ClassVar[dict[str, str]] = {
        "formal": (
            "Use complete sentences and avoid contractions. "
            "Prefer precise, professional vocabulary. "
            "Maintain an objective, third-person tone where appropriate."
        ),
        "casual": (
            "Use contractions freely (e.g., it's, don't, we're). "
            "Keep sentences short and conversational. "
            "Write as if speaking directly to the reader."
        ),
        "neutral": "",  # No additional instruction
    }

    @classmethod
    def get_system_prompt(cls, style: str = "neutral") -> str:
        """Generate the system prompt for the LLM.

        Args:
            style: Output style - "neutral", "formal", or "casual".

        Returns:
            System prompt string for the LLM.
        """
        # Extract tier 1 phrases for the prompt
        tier1_phrases = [
            "pivotal, crucial, vital, groundbreaking, remarkable",
            "transformative, profound, testament, paramount",
            "tapestry, realm, paradigm, nexus, cornerstone",
            "vibrant, comprehensive, robust, seamless, innovative",
            "In today's world, In conclusion, It's worth noting",
            "Experts argue, Studies show (without citation)",
        ]

        tier2_guidance = [
            "underscore → show/prove",
            "leverage → use",
            "delve → explore",
            "furthermore → also",
            "seamlessly, meticulously, profoundly (avoid these adverbs)",
        ]

        style_instruction = cls.style_prompts.get(style, "")
        style_section = f"\n\nStyle: {style_instruction}" if style_instruction else ""

        return (
            "You are a text editor that removes AI-sounding language to make text sound "
            "more natural and human-written.\n\n"
            "**NEVER use these phrases** (they are AI tells):\n"
            + "\n".join(f"- {p}" for p in tier1_phrases)
            + "\n\n**Replace these with simpler alternatives**:\n"
            + "\n".join(f"- {p}" for p in tier2_guidance)
            + "\n\n**Guidelines**:\n"
            "- Preserve all original meaning and information\n"
            "- Keep the same paragraph structure\n"
            "- Use natural, conversational language\n"
            "- Avoid over-explaining or hedging\n"
            "- Be direct and clear"
            + style_section
        )

    @classmethod
    def count_patterns(cls, text: str, tier: int = 1) -> int:
        """Count the number of pattern matches in text.

        Args:
            text: Text to analyze.
            tier: Which tier to count (1 or 2).

        Returns:
            Number of pattern matches found.
        """
        patterns = cls.tier1_patterns if tier == 1 else cls.tier2_patterns
        count = 0
        for pattern in patterns:
            count += len(pattern.regex.findall(text))
        return count
