import nltk
from nltk.corpus import wordnet
import random
import spacy
import logging

logger = logging.getLogger(__name__)


class EntropyBooster:
    """
    Rule engine for POS-aware WordNet synonym substitution.
    """

    def __init__(self, swap_rate: float = 0.12):
        """
        Initialize the EntropyBooster.

        Args:
            swap_rate: Probability of swapping an eligible word.
        """
        self.swap_rate = swap_rate

        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("en_core_web_sm not found.")
            self.nlp = spacy.blank("en")

        # Ensure wordnet is downloaded
        try:
            nltk.data.find("corpora/wordnet")
        except LookupError:
            logger.info("Downloading NLTK wordnet...")
            nltk.download("wordnet", quiet=True)

        # Protected stopword list to avoid swapping common structural words
        self.protected_words = {
            "very",
            "really",
            "too",
            "so",
            "not",
            "just",
            "now",
            "then",
            "more",
            "most",
            "less",
            "least",
            "well",
            "only",
        }

    def process(self, text: str) -> str:
        """
        Process text and swap adjectives and adverbs with synonyms.

        Args:
            text: Input text

        Returns:
            Text with varied vocabulary.
        """
        if not text or self.nlp.pipeline == []:
            return text

        doc = self.nlp(text)
        tokens = []

        for token in doc:
            if (
                token.pos_ in ("ADJ", "ADV")
                and token.text.lower() not in self.protected_words
            ):
                if random.random() <= self.swap_rate:
                    synonym = self._get_synonym(token.text.lower(), token.pos_)
                    if synonym:
                        # Match original casing
                        if token.istitle():
                            synonym = synonym.capitalize()
                        elif token.isupper():
                            synonym = synonym.upper()

                        tokens.append(synonym + token.whitespace_)
                        continue

            tokens.append(token.text_with_ws)

        return "".join(tokens)

    def _get_synonym(self, word: str, pos: str) -> str:
        """
        Get a synonym for the given word and POS tag.
        """
        # Map spaCy POS to WordNet POS
        wn_pos = wordnet.ADJ if pos == "ADJ" else wordnet.ADV

        synsets = wordnet.synsets(word, pos=wn_pos)
        if not synsets:
            return None

        lemmas = set()
        for synset in synsets:
            for lemma in synset.lemmas():
                name = lemma.name().replace("_", " ")
                if name.lower() != word.lower():
                    lemmas.add(name)

        if lemmas:
            return random.choice(list(lemmas))

        return None
