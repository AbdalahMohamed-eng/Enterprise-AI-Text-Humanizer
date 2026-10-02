import spacy
import numpy as np
import logging
from .lexical_rules import LexicalRules
from .passive_to_active import PassiveToActive
from .burstiness import BurstinessModulator
from .entropy_booster import EntropyBooster

logger = logging.getLogger(__name__)


class HumanizerPipeline:
    """
    Orchestrator that chains all humanization rule engines.
    """

    def __init__(self, contraction_rate: float = 0.75, swap_rate: float = 0.12):
        """
        Initialize all rule engines and the spaCy model.

        Args:
            contraction_rate: Rate for contraction injection.
            swap_rate: Rate for synonym swapping.
        """
        self.lexical_rules = LexicalRules(contraction_rate=contraction_rate)
        self.passive_to_active = PassiveToActive()
        self.burstiness_modulator = BurstinessModulator()
        self.entropy_booster = EntropyBooster(swap_rate=swap_rate)

        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("en_core_web_sm not found in HumanizerPipeline.")
            self.nlp = spacy.blank("en")

    def preprocess(self, text: str, strength: str = "medium") -> str:
        """
        Run transforms based on strength level.

        Args:
            text: The original text.
            strength: 'light', 'medium', or 'aggressive'.

        Returns:
            The humanized text.
        """
        if not text:
            return text

        try:
            # Level 1: Light (always applies)
            # Cliché strip + contractions
            text = self.lexical_rules.process(text)

            if strength in ("medium", "aggressive"):
                # Level 2: Medium
                # Passive to active voice + Burstiness
                text = self.passive_to_active.process(text)
                text = self.burstiness_modulator.process(text)

            if strength == "aggressive":
                # Level 3: Aggressive
                # Entropy boost
                text = self.entropy_booster.process(text)

            return text

        except Exception as e:
            logger.error(f"Error in HumanizerPipeline.preprocess: {e}")
            # Fallback to returning original text if pipeline fails
            return text

    def get_stats(self, text: str) -> dict:
        """
        Return text statistics: sentence count, mean length, and coefficient of variation (burstiness).

        Args:
            text: The text to analyze.

        Returns:
            Dictionary with statistics.
        """
        if not text or self.nlp.pipeline == []:
            return {"sentence_count": 0, "mean_length": 0.0, "cv_burstiness": 0.0}

        doc = self.nlp(text)
        sentences = list(doc.sents)

        if not sentences:
            return {"sentence_count": 0, "mean_length": 0.0, "cv_burstiness": 0.0}

        lengths = [len([t for t in sent if not t.is_punct]) for sent in sentences]
        lengths = [l for l in lengths if l > 0]

        if not lengths:
            return {
                "sentence_count": len(sentences),
                "mean_length": 0.0,
                "cv_burstiness": 0.0,
            }

        mean_length = float(np.mean(lengths))
        std_dev = float(np.std(lengths))

        # Coefficient of variation = std_dev / mean
        cv_burstiness = std_dev / mean_length if mean_length > 0 else 0.0

        return {
            "sentence_count": len(sentences),
            "mean_length": round(mean_length, 2),
            "cv_burstiness": round(cv_burstiness, 3),
        }
