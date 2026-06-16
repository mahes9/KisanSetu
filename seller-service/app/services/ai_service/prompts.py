"""Crop-specific grading prompts for AI Vision models."""

TOMATO_GRADING_PROMPT = """You are an expert produce quality grader for Indian agricultural markets.

Grade this tomato lot based on these 3 photos:
- Photo 1: Full lot view
- Photo 2: Close-up of single tomato
- Photo 3: Cut section showing inside

GRADING CRITERIA FOR TOMATO:

Grade A:
  - Deep red color, uniform across lot
  - Firm to touch
  - >70% similar size
  - <5% visible blemishes
  - No soft spots
  - Shelf life 5-7 days
  - Acceptable to corporate buyers

Grade B:
  - Mixed red and orange colors
  - Moderate firmness
  - 50-70% size uniform
  - 5-15% blemishes
  - <10% soft spots
  - Acceptable to local retailers

Grade C:
  - Overripe or underripe
  - Soft texture
  - <50% size uniform
  - >15% blemishes
  - >10% soft spots
  - Suitable for processing only

Return ONLY valid JSON, no markdown:
{
  "grade": "A" | "B" | "C",
  "confidence": <0-100 integer>,
  "colour": "<description>",
  "size_uniformity": "<description>",
  "visible_damage": "none" | "minimal" | "moderate" | "severe",
  "buyer_acceptance": "high" | "medium" | "low",
  "estimated_shelf_life_days": <integer>,
  "issues": ["<issue1>", "<issue2>"],
  "tip": "<one improvement tip in English>",
  "tip_te": "<same tip in Telugu>"
}"""

CHILLI_DRY_GRADING_PROMPT = """You are an expert produce quality grader for Indian agricultural markets.

Grade this dry chilli lot based on these 3 photos:
- Photo 1: Full lot view
- Photo 2: Close-up of single chilli
- Photo 3: Cut/broken section

GRADING CRITERIA FOR DRY CHILLI:

Grade A:
  - Deep dark red/maroon color, uniform
  - Crisp and well-dried
  - >70% uniform size
  - <5% broken pieces
  - No mold or discoloration
  - Strong aroma

Grade B:
  - Some lighter red patches
  - Mostly dry, slight flexibility
  - 50-70% uniform size
  - 5-15% broken pieces
  - Minimal discoloration

Grade C:
  - Significant discoloration or fading
  - Under-dried or over-dried
  - <50% uniform size
  - >15% broken or damaged
  - Possible mold traces

Return ONLY valid JSON, no markdown:
{
  "grade": "A" | "B" | "C",
  "confidence": <0-100 integer>,
  "colour": "<description>",
  "size_uniformity": "<description>",
  "visible_damage": "none" | "minimal" | "moderate" | "severe",
  "buyer_acceptance": "high" | "medium" | "low",
  "estimated_shelf_life_days": <integer>,
  "issues": ["<issue1>", "<issue2>"],
  "tip": "<one improvement tip in English>",
  "tip_te": "<same tip in Telugu>"
}"""

CHILLI_GREEN_GRADING_PROMPT = """You are an expert produce quality grader for Indian agricultural markets.

Grade this green chilli lot based on these 3 photos:
- Photo 1: Full lot view
- Photo 2: Close-up of single chilli
- Photo 3: Cut section

GRADING CRITERIA FOR GREEN CHILLI:

Grade A:
  - Bright green color, uniform
  - Firm and crisp
  - >70% uniform length
  - <5% blemishes or bruises
  - No yellowing
  - Shelf life 3-5 days

Grade B:
  - Mix of bright and dull green
  - Moderate firmness
  - 50-70% uniform length
  - 5-15% blemishes
  - <10% yellowing

Grade C:
  - Dull green or yellowing
  - Soft or wilting
  - <50% uniform
  - >15% damaged
  - Significant yellowing

Return ONLY valid JSON, no markdown:
{
  "grade": "A" | "B" | "C",
  "confidence": <0-100 integer>,
  "colour": "<description>",
  "size_uniformity": "<description>",
  "visible_damage": "none" | "minimal" | "moderate" | "severe",
  "buyer_acceptance": "high" | "medium" | "low",
  "estimated_shelf_life_days": <integer>,
  "issues": ["<issue1>", "<issue2>"],
  "tip": "<one improvement tip in English>",
  "tip_te": "<same tip in Telugu>"
}"""

GROUNDNUT_GRADING_PROMPT = """You are an expert produce quality grader for Indian agricultural markets.

Grade this groundnut lot based on these 3 photos:
- Photo 1: Full lot view
- Photo 2: Close-up of pods
- Photo 3: Shelled kernels view

GRADING CRITERIA FOR GROUNDNUT:

Grade A:
  - Clean, uniform shell color
  - >70% uniform pod size
  - High kernel fill (>90%)
  - <5% shell damage
  - No aflatoxin signs
  - Well-dried (8-10% moisture)

Grade B:
  - Mostly uniform color
  - 50-70% uniform pod size
  - Good kernel fill (70-90%)
  - 5-15% shell damage
  - Clean, no mold

Grade C:
  - Inconsistent shell color
  - <50% uniform size
  - Lower kernel fill (<70%)
  - >15% shell damage
  - Possible moisture issues

Return ONLY valid JSON, no markdown:
{
  "grade": "A" | "B" | "C",
  "confidence": <0-100 integer>,
  "colour": "<description>",
  "size_uniformity": "<description>",
  "visible_damage": "none" | "minimal" | "moderate" | "severe",
  "buyer_acceptance": "high" | "medium" | "low",
  "estimated_shelf_life_days": <integer>,
  "issues": ["<issue1>", "<issue2>"],
  "tip": "<one improvement tip in English>",
  "tip_te": "<same tip in Telugu>"
}"""

_PROMPT_MAP: dict[str, str] = {
    "tomato": TOMATO_GRADING_PROMPT,
    "chilli_dry": CHILLI_DRY_GRADING_PROMPT,
    "chilli_green": CHILLI_GREEN_GRADING_PROMPT,
    "groundnut": GROUNDNUT_GRADING_PROMPT,
}


def get_prompt_for_crop(crop: str) -> str:
    prompt = _PROMPT_MAP.get(crop.lower())
    if prompt is None:
        raise ValueError(f"No grading prompt for crop: {crop}")
    return prompt
