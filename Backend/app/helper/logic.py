import json
from typing import List
from google import genai

client = genai.Client()

async def generate_response(
    clothe_descriptions: List[str],
    prompt: str
) -> dict:

    formatted_clothes = "\n- ".join(clothe_descriptions)

    custom_prompt = f"""
    You are a professional fashion consultant.

    Here is the user's available wardrobe:
    - {formatted_clothes}

    User request:
    {prompt}

    Create a complete, cohesive top-to-bottom outfit (e.g., top, bottoms, shoes, and optional outerwear/accessories) from the available wardrobe matching the user's request.

    Return an array of the selected item IDs and a detailed reason why they look great together.
    """

    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=custom_prompt,
        config={
            "temperature": 0.7,
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "OBJECT",
                "properties": {
                    "clothe_ids": {
                        "type": "ARRAY",
                        "items": {"type": "INTEGER"},
                        "description": "List of clothing IDs that make up the full outfit."
                    },
                },
                "required": ["clothe_ids"]
            }
        }
    )

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {
            "clothe_ids": [],
        }