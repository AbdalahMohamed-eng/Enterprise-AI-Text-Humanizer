import spacy
import lemminflect
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PassiveToActive:
    """
    Rule engine for converting passive voice to active voice using spaCy and lemminflect.
    """

    def __init__(self):
        """
        Initialize the PassiveToActive engine and load the spaCy model.
        """
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning(
                "en_core_web_sm not found. Fallback to en_core_web_sm may fail."
            )
            # For production, we assume en_core_web_sm is installed
            self.nlp = spacy.blank("en")

    def process(self, text: str) -> str:
        """
        Process text and convert identified passive constructions to active voice.

        Args:
            text: The input text.

        Returns:
            The text converted to active voice where possible.
        """
        if not text or self.nlp.pipeline == []:
            return text

        doc = self.nlp(text)
        sentences = list(doc.sents)
        processed_sentences = []

        for sent in sentences:
            converted = self._convert_sentence(sent)
            if converted:
                processed_sentences.append(converted)
            else:
                processed_sentences.append(sent.text_with_ws)

        return "".join(processed_sentences)

    def _convert_sentence(self, sent) -> Optional[str]:
        """
        Convert a single sentence from passive to active if matched.
        """
        passive_subj = None
        passive_verb = None
        agent = None
        aux_verb = None

        for token in sent:
            if token.dep_ == "nsubjpass":
                passive_subj = token
            elif token.dep_ == "ROOT" and token.tag_ == "VBN":
                passive_verb = token
            elif token.dep_ == "auxpass":
                aux_verb = token
            elif token.dep_ == "agent" and token.head == passive_verb:
                for child in token.children:
                    if child.dep_ == "pobj":
                        agent = child
                        break

        # Basic check for \"[subject] [aux] [verb] by [agent]\"
        if passive_subj and passive_verb and agent and aux_verb:
            # Determine tense from the aux verb
            # was/were -> past (VBD), is/are/am -> present (VBZ/VBP)
            tag = (
                "VBD"
                if aux_verb.lemma_ == "be" and aux_verb.tag_ in ("VBD", "VBN")
                else "VBZ"
            )

            # Use lemminflect to get the active verb form
            active_verb_form = passive_verb._.inflect(tag) or passive_verb.text

            # Basic reconstruction: Agent + active_verb + passive_subj
            # This is a naive reconstruction and might need refined ordering for complex clauses
            reconstructed = []

            # Get words before the passive structure
            prefix = sent[: passive_subj.left_edge.i - sent.start].text_with_ws

            # Construct the new core
            core = f"{agent.text} {active_verb_form} {passive_subj.text}"

            # Get words after the agent
            postfix = sent[agent.right_edge.i + 1 - sent.start :].text_with_ws

            new_sent = prefix + core + postfix

            # Fix up capitalization if it was at the start
            if passive_subj.i == sent.start:
                new_sent = new_sent.capitalize()

            return new_sent

        return None
