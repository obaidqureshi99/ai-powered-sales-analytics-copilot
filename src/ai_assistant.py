
import os
import json
import time
from functools import lru_cache

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.insights import get_business_metrics
from src.prompts import SYSTEM_PROMPT

load_dotenv()

PRIMARY_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)

BACKUP_MODEL = os.getenv(
    "GEMINI_BACKUP_MODEL",
    "gemini-2.5-flash"
)


@lru_cache(maxsize=1)
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Check your .env file."
        )

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=60000)
    )


def get_business_context(metrics):
    return json.dumps(metrics, indent=2, default=str)


def stream_business_question(question, metrics=None):

    question = str(question).strip()

    if not question:
        yield "Please enter a business question."
        return

    # Retrieve database metrics
    try:
        if metrics is None:
            metrics = get_business_metrics()

        if metrics is None:
            yield "No business metrics were returned."
            return

        context = get_business_context(metrics)

    except Exception as e:
        yield f"Database error: {type(e).__name__}: {e}"
        return

    # Initialize Gemini
    try:
        client = get_gemini_client()

    except Exception as e:
        yield f"Gemini configuration error: {e}"
        return

    prompt = f"""
VERIFIED BUSINESS DATA:
{context}

USER QUESTION:
{question}

INSTRUCTIONS:
- Answer directly and clearly.
- Use the supplied business data.
- Include exact figures when available.
- Explain business insights.
- Never invent numbers.
- If information is unavailable, say so.
"""

    # Try primary and backup models
    models = [PRIMARY_MODEL]

    if BACKUP_MODEL != PRIMARY_MODEL:
        models.append(BACKUP_MODEL)

    for model in models:

        for attempt in range(2):

            try:
                response_stream = client.models.generate_content_stream(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.2,
                        max_output_tokens=700
                    )
                )

                received_text = False

                for chunk in response_stream:

                    chunk_text = chunk.text

                    if chunk_text:
                        received_text = True
                        yield chunk_text

                if received_text:
                    return

                yield f"{model} returned an empty response."
                break

            except Exception as e:

                error_name = type(e).__name__
                error_message = str(e).lower()

                temporary_error = (
                    "503" in error_message
                    or "429" in error_message
                    or "500" in error_message
                    or "unavailable" in error_message
                    or "resource_exhausted" in error_message
                )

                # Do not retry invalid model/key errors
                if not temporary_error:
                    yield (
                        f"Gemini error using {model}: "
                        f"{error_name}: {e}"
                    )
                    return

                if attempt == 0:
                    time.sleep(2)
                else:
                    break

        # Move to backup model if primary failed
        if model != models[-1]:
            yield f"Primary model busy. Trying backup model: {BACKUP_MODEL}..."

    yield (
        "Both Gemini models are currently unavailable. "
        "Please try again in a few minutes."
    )


def ask_business_question(question):
    return "".join(stream_business_question(question))
