import spacy
import random
import logging

logger = logging.getLogger(__name__)


class BurstinessModulator:
    """
    Rule engine for modulating sentence length burstiness (varying short and long sentences).
    """

    def __init__(self):
        """
        Initialize the BurstinessModulator and load spaCy.
        """
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("en_core_web_sm not found.")
            self.nlp = spacy.blank("en")

    def process(self, text: str) -> str:
        """
        Run burstiness modulation: splitting long compound sentences and merging short ones.

        Args:
            text: Input text

        Returns:
            Text with varied sentence lengths.
        """
        if not text or self.nlp.pipeline == []:
            return text

        doc = self.nlp(text)
        sentences = [sent.text for sent in doc.sents]

        # 1. Split compound sentences
        split_sentences = []
        for sent in sentences:
            split_sentences.extend(self.split_compound_sentences(sent))

        # 2. Merge short sentences
        merged_sentences = self.merge_short_sentences(split_sentences)

        return " ".join(merged_sentences)

    def split_compound_sentences(self, sentence: str) -> list[str]:
        """
        Splits sentences >22 words at coordinating conjunctions if both clauses have subjects.
        """
        doc = self.nlp(sentence)
        if len(doc) <= 22:
            return [sentence]

        # Look for coordinating conjunctions
        cc_tokens = [
            t
            for t in doc
            if t.pos_ == "CCONJ" and t.text.lower() in ("and", "but", "so", "yet")
        ]

        for cc in cc_tokens:
            # Check if there are independent subjects on both sides
            left_subj = any(t.dep_ in ("nsubj", "nsubjpass") for t in doc[: cc.i])
            right_subj = any(t.dep_ in ("nsubj", "nsubjpass") for t in doc[cc.i + 1 :])

            if left_subj and right_subj:
                # Split here
                left_part = doc[: cc.i].text.strip().rstrip(",")
                right_part = doc[cc.i + 1 :].text.strip()

                # Capitalize right part
                if right_part:
                    right_part = right_part[0].upper() + right_part[1:]

                # Add punctuation if needed
                if not left_part.endswith((".", "!", "?")):
                    left_part += "."

                return [left_part, right_part]

        return [sentence]

    def merge_short_sentences(self, sentences: list[str]) -> list[str]:
        """
        Merges adjacent short sentences (<10 words) with em dashes or semicolons (60% probability).
        """
        if len(sentences) < 2:
            return sentences

        merged = []
        i = 0
        while i < len(sentences):
            sent = sentences[i]

            # Check if this and next sentence are short
            if i < len(sentences) - 1:
                next_sent = sentences[i + 1]

                # Rough word count
                words1 = len(sent.split())
                words2 = len(next_sent.split())

                if words1 < 10 and words2 < 10 and random.random() < 0.60:
                    # Merge them
                    separator = random.choice([" ; ", " — "])
                    clean_sent1 = sent.rstrip(".!?")
                    clean_sent2 = (
                        next_sent[0].lower() + next_sent[1:] if next_sent else ""
                    )

                    merged.append(f"{clean_sent1}{separator}{clean_sent2}")
                    i += 2
                    continue

            merged.append(sent)
            i += 1

        return merged
