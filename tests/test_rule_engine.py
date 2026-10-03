from app.services.rule_engine.lexical_rules import LexicalRules
from app.services.rule_engine.passive_to_active import PassiveToActive
from app.services.rule_engine.burstiness import BurstinessModulator
from app.services.rule_engine.entropy_booster import EntropyBooster


def test_lexical_rules_cliche_stripper():
    """Test that the cliche stripper removes words like 'delve' and 'testament'."""
    engine = LexicalRules(contraction_rate=0.0)

    # Text containing clichés
    text = "Let us delve into this testament of time."
    processed = engine.process(text)

    # Assert clichés were removed/replaced
    assert "delve" not in processed.lower()
    assert "testament" not in processed.lower()
    assert processed != text


def test_lexical_rules_contractions():
    """Test contraction injection."""
    engine = LexicalRules(contraction_rate=1.0)
    text = "I do not know if it is going to work."
    processed = engine.process(text)

    assert "don't" in processed.lower()
    assert "it's" in processed.lower()


def test_passive_to_active():
    """Test that PassiveToActive doesn't crash on simple text."""
    engine = PassiveToActive()
    text = "The ball was thrown by the boy."
    processed = engine.process(text)
    assert isinstance(processed, str)
    assert len(processed) > 0


def test_burstiness_modulator():
    """Test that BurstinessModulator works without crashing."""
    engine = BurstinessModulator()
    text = "This is a short sentence. This is another short sentence."
    processed = engine.process(text)
    assert isinstance(processed, str)
    assert len(processed) > 0


def test_entropy_booster():
    """Test that EntropyBooster works without crashing."""
    # Using swap_rate=0.0 to avoid need for spacy/nltk full functioning in simple test
    engine = EntropyBooster(swap_rate=0.0)
    text = "The very quick brown fox jumps over the lazy dog."
    processed = engine.process(text)
    assert isinstance(processed, str)
    assert len(processed) > 0
