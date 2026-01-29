"""Tests for the ResearchAgent class.

Note: These are basic test templates. For actual testing, you would need to:
1. Mock the external API calls (Anthropic, Tavily)
2. Create fixtures for test data
3. Test edge cases and error handling
"""

import pytest
from unittest.mock import Mock, patch

from lonai import ResearchAgent
from lonai.config import Settings


class TestResearchAgent:
    """Test suite for ResearchAgent."""
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings for testing."""
        from lonai.config.constants import AgentProvider
        settings = Mock(spec=Settings)
        # We need to set attributes properly for spec=Settings
        settings.agent_provider = AgentProvider.ANTHROPIC
        settings.anthropic_api_key = "test-anthropic-key"
        settings.tavily_api_key = "test-tavily-key"
        settings.agent_api_key = None
        settings.agent_base_url = None
        settings.agent_model = "claude-test"
        settings.agent_temperature = 0.7
        settings.agent_max_tokens = 1000
        
        settings.search_max_results = 5
        settings.storage_data_dir = "/tmp/research_test"
        settings.export_output_dir = "/tmp/reports_test"
        settings.storage_auto_save = True
        settings.export_default_format = "markdown"
        return settings
    
    @patch('lonai.core.agent.create_deep_agent')
    @patch('lonai.core.agent.SearchTool')
    @patch('lonai.core.agent.StorageManager')
    @patch('lonai.core.agent.ReportExporter')
    @patch('langchain_anthropic.ChatAnthropic') 
    def test_agent_initialization(
        self,
        mock_anthropic,
        mock_exporter,
        mock_storage,
        mock_search,
        mock_create_agent,
        mock_settings
    ):
        """Test that ResearchAgent initializes correctly."""
        # Ensure model init returns our mock
        mock_anthropic.return_value = Mock()
        
        agent = ResearchAgent(settings=mock_settings)
        
        assert agent is not None
        assert agent.settings == mock_settings
        mock_search.assert_called_once()
        mock_storage.assert_called_once()
        mock_exporter.assert_called_once()
        mock_create_agent.assert_called_once()
        mock_anthropic.assert_called_once()

    @patch('lonai.core.agent.create_deep_agent')
    @patch('langchain_anthropic.ChatAnthropic')
    def test_research_method(self, mock_anthropic, mock_create_agent, mock_settings):
        """Test the research method."""
        # Mock the agent's invoke method
        mock_agent_instance = Mock()
        mock_agent_instance.invoke.return_value = {
            "messages": [
                Mock(content="This is a test research response.")
            ]
        }
        mock_create_agent.return_value = mock_agent_instance
        mock_anthropic.return_value = Mock()
        
        # Create agent and conduct research
        agent = ResearchAgent(settings=mock_settings)
        
        with patch.object(agent.storage_manager, 'save_research') as mock_save:
            mock_save.return_value = "/tmp/test.json"
            
            result = agent.research(
                query="Test query",
                save_results=True,
                export_report=False
            )
        
        assert "query" in result
        assert "response" in result
        assert result["query"] == "Test query"
        assert "saved_path" in result
    
    @patch('lonai.core.agent.create_deep_agent')
    @patch('langchain_anthropic.ChatAnthropic')
    def test_batch_research(self, mock_anthropic, mock_create_agent, mock_settings):
        """Test batch research functionality."""
        mock_agent_instance = Mock()
        mock_agent_instance.invoke.return_value = {
            "messages": [Mock(content="Test response")]
        }
        mock_create_agent.return_value = mock_agent_instance
        mock_anthropic.return_value = Mock()
        
        agent = ResearchAgent(settings=mock_settings)
        
        with patch.object(agent.storage_manager, 'save_research'):
            results = agent.batch_research(
                queries=["Query 1", "Query 2"],
                save_results=False
            )
        
        assert len(results) == 2
        assert all("query" in r for r in results)
        assert all("response" in r for r in results)

    @patch('lonai.core.agent.create_deep_agent')
    @patch('lonai.core.agent.SearchTool')
    @patch('lonai.core.agent.StorageManager')
    @patch('lonai.core.agent.ReportExporter')
    def test_agent_openai_init(self, mock_exporter, mock_storage, mock_search, mock_create, mock_settings):
        """Test initialization with OpenAI provider."""
        from lonai.config.constants import AgentProvider
        
        # Configure settings for OpenAI
        mock_settings.agent_provider = AgentProvider.OPENAI
        mock_settings.openai_api_key = "sk-test-key"
        mock_settings.agent_api_key = None
        mock_settings.agent_base_url = None
        mock_settings.agent_model = "gpt-4"
        
        # When mocking imports inside the function, we need to patch specifically where it is imported
        # But since the import happens INSIDE _configure_model based on provider, 
        # it is safer to patch sys.modules or just patch the import target in the module namespace 
        # IF it was top-level.
        # Since it is inside the method, we can use patch with 'lonai.core.agent.ChatOpenAI'
        # BUT this only works if the runtime actually tries to resolve it.
        # Let's ensure the previous failure (AttributeError) is fixed by ensuring the import succeeds or is mocked.
        
        # NOTE: patch('lonai.core.agent.ChatOpenAI') Failed because ChatOpenAI is not in agent.py namespace
        # until imported. Since it is dynamic, we should patch where it comes from: 'langchain_openai.ChatOpenAI'
        # OR force it into the namespace. 
        
        with patch('langchain_openai.ChatOpenAI') as MockChatOpenAI:
             agent = ResearchAgent(settings=mock_settings)
             MockChatOpenAI.assert_called_once()
             _, kwargs = MockChatOpenAI.call_args
             assert kwargs['model'] == "gpt-4"
             assert kwargs['api_key'] == "sk-test-key"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
