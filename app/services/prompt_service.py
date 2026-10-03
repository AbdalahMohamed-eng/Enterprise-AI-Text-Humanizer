from typing import Tuple


def build_humanizer_prompt(text: str, mode: str, strength: str) -> Tuple[str, str]:
    """
    Builds the system and user prompts for the humanizer based on mode and strength.
    """
    base_system = (
        "You are an expert human editor and writer. Your task is to rewrite the provided text so that it reads "
        "as naturally as possible, mimicking human writing patterns, tone, and sentence structure.\n"
        "1. Preserve core meaning and facts.\n"
        "2. Restructure phrasing and sentence rhythm.\n"
        "3. Vary vocabulary (especially avoid top-probability tokens).\n"
    )

    mode_instructions = {
        "casual": "Use a conversational, engaging tone. Incorporate contractions, colloquialisms, and organic transitions.",
        "formal": "Use a professional, concise tone suitable for business. Avoid corporate clichés and keep it business-ready.",
        "academic": "Use a scholarly, rigorous tone. Ensure natural phrasing and avoid robotic, formulaic transitions.",
        "anti_ai": "Maximize burstiness and perplexity. Eliminate ALL AI markers (e.g., 'delve', 'testament', 'tapestry'). "
        "Vary sentence structure dramatically and use colloquial hedges appropriately.",
    }

    strength_instructions = {
        "light": "Make minor adjustments to improve flow and naturalness without drastically changing the original structure.",
        "medium": "Rewrite significantly to ensure human-like flow, varying sentence length and structure.",
        "aggressive": "Completely overhaul the text. Be creative with vocabulary and structure to ensure it passes all AI detection while retaining the core message.",
    }

    mode_instruction = mode_instructions.get(mode, mode_instructions["anti_ai"])
    strength_instruction = strength_instructions.get(strength, strength_instructions["medium"])

    system_prompt = f"{base_system}\n\n4. Mode Instructions: {mode_instruction}\n\n5. Strength Instructions: {strength_instruction}"

    user_prompt = f"Please humanize the following text:\n\n{text}"

    return system_prompt, user_prompt
