"""Tests for configuration loading.

The user's .env file is loaded at module import time and dataclass
defaults are resolved from os.environ. Tests verify that config values
are present and that overrides work when env vars are set before
config is reloaded.
"""

import os


class TestConfigValues:
    """Verify the user's actual configuration is loaded and coherent."""

    def test_config_loads(self):
        from contract_analyzer.config import config
        assert config is not None

    def test_essential_values_are_set(self):
        from contract_analyzer.config import config
        assert config.llm_model
        assert config.llm_api_key, "LLM API key must be set"
        assert config.risk_agent_max_iterations > 0
        assert config.max_upload_size_mb > 0
        assert 0 <= config.llm_temperature <= 2.0

    def test_weights_sum_reasonably(self):
        from contract_analyzer.config import config
        total = config.vector_weight + config.bm25_weight
        assert 0.9 <= total <= 1.1, f"Weights should sum to ~1.0, got {total}"

    def test_verification_threshold_reasonable(self):
        from contract_analyzer.config import config
        assert 1 <= config.verification_flag_threshold <= 10

    def test_agent_iterations_reasonable(self):
        from contract_analyzer.config import config
        assert 5 <= config.risk_agent_max_iterations <= 50


class TestConfigReload:
    """Test that config respects env var changes when module is reloaded.

    load_dotenv() is called at module level with override=False, so
    setting os.environ values before reload takes precedence over
    the .env file.
    """

    def test_env_var_override_works(self):
        """Setting env vars before reload overrides .env values."""
        os.environ["LLM_MODEL"] = "test-model-override"
        os.environ["LLM_TEMPERATURE"] = "0.7"

        import importlib
        import contract_analyzer.config
        importlib.reload(contract_analyzer.config)

        c = contract_analyzer.config.Config()
        assert c.llm_model == "test-model-override"
        assert c.llm_temperature == 0.7

        # Clean up
        importlib.reload(contract_analyzer.config)

    def test_boolean_env_false(self):
        os.environ["VERIFICATION_ENABLED"] = "false"

        import importlib
        import contract_analyzer.config
        importlib.reload(contract_analyzer.config)

        c = contract_analyzer.config.Config()
        assert c.verification_enabled is False

        importlib.reload(contract_analyzer.config)

    def test_numeric_env_override(self):
        os.environ["RISK_AGENT_MAX_ITERATIONS"] = "25"

        import importlib
        import contract_analyzer.config
        importlib.reload(contract_analyzer.config)

        c = contract_analyzer.config.Config()
        assert c.risk_agent_max_iterations == 25

        importlib.reload(contract_analyzer.config)
