from typing import List

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.Core.logger import logger


class OutfitRecommendation(BaseModel):
    clothe_ids: List[int] = Field(
        description="Only the IDs of the clothing items selected from the wardrobe."
    )


async def generate_response(
    api_key: str,
    clothes: List[str],
    prompt: str,
) -> OutfitRecommendation | None:

    try:
        client = genai.Client(api_key=api_key)

        formatted_clothes = "\n".join(clothes)

        custom_prompt = f"""
        You are a professional fashion consultant.

        Here is the user's available wardrobe:
        {formatted_clothes}

        User request:
        {prompt}

        Choose ONE complete, cohesive outfit from the available wardrobe.

        OUTFIT RULES:
        - Select exactly ONE top.
        - Select exactly ONE bottom.
        - Select exactly ONE pair of shoes.
        - If the wardrobe contains a suitable one-piece outfit
          (such as a dress or jumpsuit), select that instead of a top and bottom.
        - Never select two tops.
        - Never select two bottoms.
        - Never select two pairs of shoes.
        - Do not combine a one-piece outfit with a separate top or bottom.
        - Only select items that actually exist in the provided wardrobe.
        - Prefer the most appropriate outfit for the user's occasion,
          weather, season, and formality.
        - If a category is unavailable, choose the best complete outfit
          possible from the available items.
        - Do not select extra items just because they match.

        IMPORTANT OUTPUT RULES:
        - Return ONLY the IDs of the selected clothing items.
        - Return each selected ID only once.
        - Do not return clothing names.
        - Do not return explanations or reasoning.
        - Do not invent IDs.
        """

        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=custom_prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                response_mime_type="application/json",
                response_schema=OutfitRecommendation,
            ),
        )

        if not response.parsed:
            logger.warning("Gemini returned an empty or invalid outfit response.")
            return None

        return response.parsed

    except Exception as exc:
        logger.exception(
            "Failed to generate outfit recommendation: %s",
            exc,
        )
        return None