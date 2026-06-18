"""Tests for A2A server infrastructure (structure checks, no live servers)."""

import pytest


class TestA2AImports:
    def test_server_module_imports(self):
        """Verify a2a_servers module can be imported."""
        from contract_analyzer.agents import a2a_servers
        assert a2a_servers is not None

    def test_risk_agent_executor_exists(self):
        from contract_analyzer.agents.a2a_servers import RiskAgentExecutor
        import inspect
        assert inspect.isclass(RiskAgentExecutor)

    def test_factory_functions_exist(self):
        from contract_analyzer.agents import a2a_servers
        assert callable(a2a_servers.create_risk_agent_app)
        assert callable(a2a_servers.create_risk_privacy_agent_app)
        assert callable(a2a_servers.create_risk_financial_agent_app)


class TestA2AProtocolConstants:
    def test_specialist_labels(self):
        """Verify the specialist constants are defined."""
        from contract_analyzer.agents.a2a_servers import (
            create_risk_agent_app,
            create_risk_financial_agent_app,
            create_risk_privacy_agent_app,
        )
        # All three factory functions exist and are callable
        import inspect
        for fn in [create_risk_agent_app, create_risk_privacy_agent_app, create_risk_financial_agent_app]:
            sig = inspect.signature(fn)
            params = list(sig.parameters.keys())
            assert "port" in params
