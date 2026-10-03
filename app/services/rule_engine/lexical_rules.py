import re
import random
from typing import Dict, List

# Dictionary of AI overused words/phrases mapped to natural alternatives
CLICHES: Dict[str, List[str]] = {
    # Verbs & Verb Phrases
    "delve into": ["examine", "explore", "look into", "investigate", "dig into"],
    "delve": ["explore", "examine", "investigate"],
    "leverage": ["use", "make use of", "utilize", "take advantage of"],
    "foster": ["encourage", "promote", "help grow", "build"],
    "navigate": ["handle", "deal with", "work through", "manage"],
    "underscore": ["highlight", "show", "point out", "emphasize"],
    "harness": ["use", "put to work", "apply"],
    "illuminate": ["explain", "clarify", "shed light on"],
    "demystify": ["explain", "simplify", "make clear"],
    "embark": ["start", "begin", "set out"],
    "encapsulate": ["sum up", "summarize", "capture"],
    # Nouns & Noun Phrases
    "a tapestry of": ["a blend of", "a collection of", "a mix of"],
    "tapestry": ["mix", "collection", "blend"],
    "a testament to": ["proof of", "clear evidence of", "a reflection of"],
    "testament": ["proof", "evidence", "sign"],
    "a plethora of": ["plenty of", "a wealth of", "an abundance of", "many"],
    "plethora": ["abundance", "wealth", "wide range"],
    "a myriad of": ["countless", "a wide range of", "many", "numerous"],
    "myriad": ["countless", "numerous", "diverse"],
    "paradigm": ["model", "pattern", "example"],
    "interplay": ["interaction", "relationship", "connection"],
    "cornerstone": ["foundation", "basis", "key part"],
    "beacon": ["guide", "symbol", "sign"],
    "facet": ["side", "aspect", "part"],
    # Adjectives
    "pivotal": ["key", "important", "main", "crucial"],
    "crucial": ["important", "key", "essential"],
    "vibrant": ["lively", "active", "bright"],
    "transformative": ["life-changing", "major", "game-changing"],
    "multifaceted": ["complex", "varied", "many-sided"],
    "meticulous": ["careful", "detailed", "thorough"],
    "seamless": ["smooth", "flawless", "easy"],
    "profound": ["deep", "major", "significant"],
    "comprehensive": ["complete", "full", "thorough", "detailed"],
    # Phrases
    "in today's fast-paced world": [
        "these days",
        "nowadays",
        "today",
        "in our modern world",
    ],
    "it is important to remember that": [
        "remember that",
        "keep in mind that",
        "importantly,",
    ],
    "it is worth noting that": ["note that", "also,", "worth mentioning:"],
    "plays a pivotal role": ["is key", "is very important", "matters a lot"],
    "in the realm of": ["in", "when it comes to", "regarding"],
    "a testament to": ["proof of", "showing", "evidence of"],
    # Transitions
    "furthermore": ["also", "plus", "in addition"],
    "moreover": ["also", "besides", "what's more"],
    "additionally": ["also", "on top of that"],
    "in conclusion": ["to sum up", "finally", "overall"],
    "to summarize": ["in short", "briefly", "to sum up"],
    "ultimately": ["in the end", "finally", "at last"],
}

# Contractions for injection
CONTRACTIONS: Dict[str, str] = {
    "do not": "don't",
    "does not": "doesn't",
    "cannot": "can't",
    "could not": "couldn't",
    "will not": "won't",
    "would not": "wouldn't",
    "should not": "shouldn't",
    "is not": "isn't",
    "are not": "aren't",
    "was not": "wasn't",
    "were not": "weren't",
    "have not": "haven't",
    "has not": "hasn't",
    "had not": "hadn't",
    "i am": "i'm",
    "it is": "it's",
    "he is": "he's",
    "she is": "she's",
    "that is": "that's",
    "there is": "there's",
    "they are": "they're",
    "we are": "we're",
    "you are": "you're",
    "i have": "i've",
    "you have": "you've",
    "we have": "we've",
    "they have": "they've",
    "i would": "i'd",
    "you would": "you'd",
    "he would": "he'd",
    "she would": "she'd",
    "we would": "we'd",
    "they would": "they'd",
    "would have": "would've",
    "could have": "could've",
    "should have": "should've",
}


class LexicalRules:
    """
    Rule engine for stripping AI clichés and injecting contractions.
    """

    def __init__(self, contraction_rate: float = 0.75):
        """
        Initialize the LexicalRules engine.

        Args:
            contraction_rate: Probability of injecting a contraction when a match is found.
        """
        self.contraction_rate = contraction_rate

    def process(self, text: str) -> str:
        """
        Run cliché stripping and contraction injection on the given text.

        Args:
            text: The input text.

        Returns:
            The processed text with more natural phrasing.
        """
        if not text:
            return text

        # 1. Replace clichés
        # Sort keys by length descending to replace longer phrases first
        sorted_cliches = sorted(CLICHES.keys(), key=len, reverse=True)

        for cliche in sorted_cliches:
            # Case-insensitive word boundary match
            pattern = re.compile(rf"\b{re.escape(cliche)}\b", flags=re.IGNORECASE)

            def repl_cliche(match):
                original = match.group(0)
                replacement = random.choice(CLICHES[cliche])
                # Preserve capitalization
                if original.istitle():
                    return replacement.capitalize()
                elif original.isupper():
                    return replacement.upper()
                return replacement

            text = pattern.sub(repl_cliche, text)

        # 2. Inject contractions
        sorted_contractions = sorted(CONTRACTIONS.keys(), key=len, reverse=True)

        for full_form in sorted_contractions:
            pattern = re.compile(rf"\b{re.escape(full_form)}\b", flags=re.IGNORECASE)

            def repl_contraction(match):
                if random.random() <= self.contraction_rate:
                    original = match.group(0)
                    replacement = CONTRACTIONS[full_form]
                    if original.istitle() or original[0].isupper():
                        # Capitalize first letter (e.g., "It is" -> "It's")
                        return replacement[0].upper() + replacement[1:]
                    elif original.isupper():
                        return replacement.upper()
                    return replacement
                return match.group(0)

            text = pattern.sub(repl_contraction, text)

        return text
