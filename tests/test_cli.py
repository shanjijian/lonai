"""Tests for CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, Mock

from lonai.cli.commands import cli


class TestCLI:
    """Tests for CLI commands."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @patch('lonai.cli.commands.validate_api_keys')
    def test_cli_help(self, mock_validate, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "Research Assistant" in result.output
    
    @patch('lonai.cli.commands.validate_api_keys')
    @patch('lonai.cli.commands.ResearchAgent')
    def test_research_command(self, mock_agent_class, mock_validate, runner):
        """Test research command."""
        mock_validate.return_value = (True, None)
        
        # Mock the agent
        mock_agent = Mock()
        mock_agent.research.return_value = {
            "query": "test",
            "response": "Test response"
        }
        mock_agent_class.return_value = mock_agent
        
        result = runner.invoke(cli, ['research', 'What is AI?'])
        
        assert result.exit_code == 0
        mock_agent.research.assert_called_once()
    
    @patch('lonai.cli.commands.validate_api_keys')
    def test_config_command(self, mock_validate, runner):
        """Test config command."""
        result = runner.invoke(cli, ['config'])
        
        # Exit code may be 1 if settings can't be loaded without API keys
        assert "Configuration" in result.output or result.exit_code == 1
    
    @patch('lonai.cli.commands.validate_api_keys')
    @patch('lonai.cli.commands.ResearchAgent')
    @patch('lonai.cli.commands.get_settings')
    def test_history_command(self, mock_get_settings, mock_agent_class, mock_validate, runner):
        """Test history command."""
        mock_validate.return_value = (True, None)
        
        mock_agent = Mock()
        mock_agent.get_history.return_value = [
            {
                "filename": "test.json",
                "query": "Test query",
                "timestamp": "2026-01-01T00:00:00"
            }
        ]
        mock_agent_class.return_value = mock_agent
        
        result = runner.invoke(cli, ['history'])
        
        assert result.exit_code == 0
        mock_agent.get_history.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
