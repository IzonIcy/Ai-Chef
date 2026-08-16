"""Basic smoke test to verify dependencies import correctly."""


def test_imports():
    """Verify all key dependencies can be imported."""
    import dotenv
    import openai
    import rich

    assert openai is not None
    assert dotenv is not None
    assert rich is not None
