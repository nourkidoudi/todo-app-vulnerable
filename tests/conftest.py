"""Configuration pytest"""
import pytest


def pytest_configure(config):
    """Configuration globale des tests."""
    config.addinivalue_line(
        "markers",
        "security: Tests de sécurité (Phase 3)"
    )
    config.addinivalue_line(
        "markers",
        "functional: Tests fonctionnels"
    )
