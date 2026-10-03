import numpy as np
import textstat
import spacy
import spacy.cli
from typing import Dict, Any

_nlp = None


class TextAnalyzer:
    @staticmethod
    def get_nlp():
        global _nlp
        if _nlp is None:
            try:
                _nlp = spacy.load("en_core_web_sm")
            except OSError:
                spacy.cli.download("en_core_web_sm")
                _nlp = spacy.load("en_core_web_sm")
        return _nlp

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        """Analyzes text statistics."""
        if not text or not text.strip():
            return {
                "word_count": 0,
                "sentence_count": 0,
                "flesch_reading_ease": 0.0,
                "flesch_kincaid_grade": 0.0,
                "burstiness_cv": 0.0,
            }

        words = text.strip().split()
        word_count = len(words)

        nlp = cls.get_nlp()
        doc = nlp(text)
        sentences = list(doc.sents)
        sentence_count = len(sentences)

        # Readability stats
        try:
            fre = textstat.flesch_reading_ease(text)
            fkg = textstat.flesch_kincaid_grade(text)
        except Exception:
            fre = 0.0
            fkg = 0.0

        # Burstiness (Coefficient of Variation of sentence length)
        if sentence_count > 1:
            sent_lengths = [len([t for t in sent if not t.is_punct]) for sent in sentences]
            sent_lengths = [sl for sl in sent_lengths if sl > 0]
            if sent_lengths:
                mean_len = np.mean(sent_lengths)
                std_len = np.std(sent_lengths)
                burstiness = float(std_len / mean_len) if mean_len > 0 else 0.0
            else:
                burstiness = 0.0
        else:
            burstiness = 0.0

        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "flesch_reading_ease": float(fre),
            "flesch_kincaid_grade": float(fkg),
            "burstiness_cv": round(burstiness, 3),
        }
