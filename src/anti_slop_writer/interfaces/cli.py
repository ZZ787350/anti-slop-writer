"""CLI interface for anti-slop-writer.

This module provides the command-line interface using typer,
with proper error handling and exit codes per contracts/cli.md.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

import typer

from anti_slop_writer import __version__
from anti_slop_writer.core.config import get_settings
from anti_slop_writer.core.processor import TextProcessor
from anti_slop_writer.core.rewriter import Rewriter
from anti_slop_writer.language_packs.english import EnglishPack
from anti_slop_writer.providers import (
    AuthenticationError,
    MalformedResponseError,
    NetworkError,
    OpenAICompatibleProvider,
    ProviderError,
    RateLimitError,
)

# Configure logging - metadata only, no text content (FR-014)
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Exit codes per contracts/cli.md
EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 1
EXIT_CONFIG_ERROR = 2
EXIT_PROVIDER_ERROR = 3
EXIT_NETWORK_ERROR = 4
EXIT_PROCESSING_ERROR = 5

app = typer.Typer(
    name="anti-slop-writer",
    help="Rewrite text to reduce AI-sounding patterns.",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        typer.echo(f"anti-slop-writer {__version__}")
        raise typer.Exit(code=EXIT_SUCCESS)


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """anti-slop-writer - Reduce AI-sounding patterns in text."""
    pass


@app.command()
def rewrite(
    text: str | None = typer.Argument(
        None,
        help="Text to rewrite (mutually exclusive with --input).",
    ),
    input_file: Path | None = typer.Option(
        None,
        "--input",
        "-i",
        help="Read text from file.",
    ),
    output_file: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Write output to file (default: stdout).",
    ),
    style: str = typer.Option(
        "neutral",
        "--style",
        "-s",
        help="Output style: neutral, formal, casual.",
    ),
    provider_name: str = typer.Option(
        "default",
        "--provider",
        "-p",
        help="Provider config name (future feature).",
    ),
) -> None:
    """Rewrite text to reduce AI-sounding patterns.

    Takes input text and rewrites it to sound more natural and human-like
    by reducing AI-typical vocabulary patterns.
    """
    exit_code = asyncio.run(
        _rewrite_async(text, input_file, output_file, style, provider_name)
    )
    raise typer.Exit(code=exit_code)


async def _rewrite_async(
    text: str | None,
    input_file: Path | None,
    output_file: Path | None,
    style: str,
    provider_name: str,  # noqa: ARG001 - Reserved for future use
) -> int:
    """Async implementation of the rewrite command.

    Args:
        text: Direct text input.
        input_file: Path to input file.
        output_file: Path to output file.
        style: Output style.
        provider_name: Provider config name.

    Returns:
        Exit code.
    """
    processor = TextProcessor()

    # Validate style
    valid_styles = {"neutral", "formal", "casual"}
    if style not in valid_styles:
        typer.echo(
            f"Error: Invalid style '{style}'. Must be: {', '.join(sorted(valid_styles))}",
            err=True,
        )
        return EXIT_INPUT_ERROR

    # Get input text
    input_text: str | None = None

    if text is not None and input_file is not None:
        typer.echo(
            "Error: Cannot use both text argument and --input option.",
            err=True,
        )
        return EXIT_INPUT_ERROR

    if text is not None:
        # Check for stdin indicator
        if text == "-":
            # Read from stdin
            try:
                import sys
                input_text = sys.stdin.read()
            except Exception as e:
                typer.echo(f"Error: Failed to read from stdin: {e}", err=True)
                return EXIT_INPUT_ERROR
        else:
            input_text = text
    elif input_file is not None:
        if not input_file.exists():
            typer.echo(
                f"Error: File not found: {input_file}",
                err=True,
            )
            return EXIT_INPUT_ERROR
        try:
            input_text = processor.read_file(input_file)
        except Exception as e:
            typer.echo(f"Error: {e}", err=True)
            return EXIT_INPUT_ERROR
    else:
        # No input provided - show help
        typer.echo(
            "Error: Please provide text or specify --input file.",
            err=True,
        )
        return EXIT_INPUT_ERROR

    # Validate input text
    is_valid, error_msg = processor.validate_text(input_text)
    if not is_valid:
        typer.echo(f"Error: {error_msg}", err=True)
        return EXIT_INPUT_ERROR

    # Check word count warning (FR-017)
    processor.check_word_count_warning(input_text)

    # Load configuration
    try:
        settings = get_settings()
        provider_config = settings.to_provider_config()
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        return EXIT_CONFIG_ERROR

    # Create provider and rewriter
    provider = OpenAICompatibleProvider(provider_config)
    rewriter = Rewriter(provider, EnglishPack, default_style=settings.default_style)

    # Execute rewrite
    try:
        async with rewriter:
            logger.info("Starting rewrite...")
            result = await rewriter.rewrite(input_text, style=style)

            output_text = result.rewritten_text

            # Output result
            if output_file is not None:
                try:
                    processor.write_file(output_file, output_text)
                    logger.info(f"Output written to: {output_file}")
                except Exception as e:
                    typer.echo(f"Error: {e}", err=True)
                    return EXIT_PROCESSING_ERROR
            else:
                # Write to stdout
                typer.echo(output_text)

            logger.info(
                f"Rewrite complete. "
                f"Patterns: {result.pattern_count_before} → {result.pattern_count_after} "
                f"({result.processing_time_ms}ms)"
            )

            return EXIT_SUCCESS

    except AuthenticationError as e:
        typer.echo(f"Error: {e}", err=True)
        return EXIT_PROVIDER_ERROR

    except RateLimitError as e:
        typer.echo(f"Error: {e}", err=True)
        return EXIT_PROVIDER_ERROR

    except NetworkError as e:
        typer.echo(f"Error: {e}", err=True)
        return EXIT_NETWORK_ERROR

    except MalformedResponseError as e:
        typer.echo(f"Error: {e}", err=True)
        return EXIT_PROCESSING_ERROR

    except ProviderError as e:
        typer.echo(f"Error: {e}", err=True)
        return EXIT_PROCESSING_ERROR

    except Exception as e:
        logger.exception("Unexpected error during rewrite")
        typer.echo(f"Error: {e}", err=True)
        return EXIT_PROCESSING_ERROR


if __name__ == "__main__":
    app()
