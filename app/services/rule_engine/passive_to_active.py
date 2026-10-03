import logging
from typing import Optional
import lemminflect
import spacy

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
            logger.warning("en_core_web_sm not found. Fallback to en_core_web_sm may fail.")
            self.nlp = spacy.blank("en")

    def process(self, text: str) -> str:
        """
        Identifies passive constructions and converts them to active voice where possible.

        Args:
            text: The input text.

        Returns:
            Text with converted active voice sentences.
        """
        if not text:
            return text

        doc = self.nlp(text)
        processed_sentences = []

        for sent in doc.sents:
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
        aux_verb = None
        agent = None

        for token in sent:
            # Identify the passive subject
            if token.dep_ == "nsubjpass":
                passive_subj = token
                passive_verb = token.head

                # Find the passive auxiliary (e.g., 'was', 'is', 'were', 'been')
                for child in passive_verb.children:
                    if child.dep_ == "auxpass":
                        aux_verb = child
                        break

                # Find the agent in a prepositional phrase ("by ...")
                for child in passive_verb.children:
                    if child.dep_ == "agent" or (
                        child.dep_ == "prep" and child.text.lower() == "by"
                    ):
                        for agent_child in child.children:
                            if agent_child.dep_ in ("pobj", "dobj"):
                                agent = agent_child
                                break
                        break

        # Basic check for "[subject] [aux] [verb] by [agent]"
        if passive_subj and passive_verb and agent and aux_verb:
            # Determine tense from the aux verb
            # was/were -> past (VBD), is/are/am -> present (VBZ/VBP)
            tag = "VBD" if aux_verb.lemma_ == "be" and aux_verb.tag_ in ("VBD", "VBN") else "VBZ"

            # Use lemminflect to get the active verb form
            inflections = lemminflect.getInflection(passive_verb.lemma_, tag=tag)
            active_verb_form = inflections[0] if inflections else passive_verb.text

            # Get words before the passive structure
            prefix = sent[: passive_subj.left_edge.i - sent.start].text_with_ws

            # Construct the new core
            core = f"{agent.text} {active_verb_form} {passive_subj.text}"

            # Get words after the agent
            postfix = sent[agent.right_edge.i + 1 - sent.start :].text_with_ws

            new_sent = prefix + core + postfix

            # Preserve ending whitespace from original sentence if any
            if sent.text_with_ws.endswith(" ") and not new_sent.endswith(" "):
                new_sent += " "

            return new_sent

        return None
