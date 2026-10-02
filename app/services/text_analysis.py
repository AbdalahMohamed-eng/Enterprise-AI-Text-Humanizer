import numpy as np
import textstat
import spacy
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
                import spacy.cli

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

        nlp = cls.get_nlp()
        doc = nlp(text)

        sentences = list(doc.sents)
        sentence_count = len(sentences)

        word_count = textstat.lexicon_count(text, removepunct=True)
        fre = textstat.flesch_reading_ease(text)
        fkg = textstat.flesch_kincaid_grade(text)

        sentence_lengths = [
            len([t for t in sent if not t.is_punct]) for sent in sentences
        ]

        if len(sentence_lengths) > 1:
            mean_len = np.mean(sentence_lengths)
            std_dev = np.std(sentence_lengths)
            burstiness_cv = (std_dev / mean_len) if mean_len > 0 else 0.0
        else:
            burstiness_cv = 0.0

        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "flesch_reading_ease": fre,
            "flesch_kincaid_grade": fkg,
            "burstiness_cv": round(float(burstiness_cv), 4),
        }
