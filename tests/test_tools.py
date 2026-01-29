"""Tests for tool modules."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import json

from lonai.tools.search import SearchTool
from lonai.tools.storage import StorageManager
from lonai.tools.export import ReportExporter
from lonai.config.constants import ExportFormat


class TestSearchTool:
    """Tests for SearchTool."""
    
    @patch('lonai.tools.search.TavilyClient')
    def test_search_initialization(self, mock_tavily):
        """Test SearchTool initialization."""
        tool = SearchTool(api_key="test-key", max_results=5)
        
        assert tool is not None
        assert tool.max_results == 5
        mock_tavily.assert_called_once_with(api_key="test-key")
    
    @patch('lonai.tools.search.TavilyClient')
    def test_search_execution(self, mock_tavily):
        """Test search execution."""
        mock_client = Mock()
        mock_client.search.return_value = {
            "query": "test",
            "results": [{"title": "Test", "url": "http://test.com"}]
        }
        mock_tavily.return_value = mock_client
        
        tool = SearchTool(api_key="test-key")
        result = tool.search("test query", max_results=3)
        
        assert "query" in result
        assert "results" in result
        mock_client.search.assert_called_once()
    
    @patch('lonai.tools.search.TavilyClient')
    def test_search_cache(self, mock_tavily):
        """Test search result caching."""
        mock_client = Mock()
        mock_client.search.return_value = {"query": "test", "results": []}
        mock_tavily.return_value = mock_client
        
        tool = SearchTool(api_key="test-key")
        
        # First call
        result1 = tool.search("test")
        # Second call (should use cache)
        result2 = tool.search("test")
        
        # Search should only be called once due to caching
        assert mock_client.search.call_count == 1
        assert result1 == result2


class TestStorageManager:
    """Tests for StorageManager."""
    
    def test_storage_initialization(self):
        """Test StorageManager initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StorageManager(data_dir=tmpdir)
            assert manager is not None
            assert manager.data_dir == Path(tmpdir)
    
    def test_save_and_load_research(self):
        """Test saving and loading research data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StorageManager(data_dir=tmpdir)
            
            # Save research
            filepath = manager.save_research(
                query="Test query",
                results="Test results",
                metadata={"test": "data"}
            )
            
            assert filepath.exists()
            
            # Load research
            data = manager.load_research(filepath.name)
            
            assert data is not None
            assert data["query"] == "Test query"
            assert data["results"] == "Test results"
            assert data["metadata"]["test"] == "data"
    
    def test_list_research(self):
        """Test listing research files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StorageManager(data_dir=tmpdir)
            
            # Save multiple research files
            manager.save_research("Query 1", "Results 1")
            manager.save_research("Query 2", "Results 2")
            
            # List research
            research_list = manager.list_research()
            
            assert len(research_list) >= 2
            assert all("filename" in r for r in research_list)
            assert all("query" in r for r in research_list)


class TestReportExporter:
    """Tests for ReportExporter."""
    
    def test_exporter_initialization(self):
        """Test ReportExporter initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = ReportExporter(output_dir=tmpdir)
            assert exporter is not None
            assert exporter.output_dir == Path(tmpdir)
    
    def test_markdown_export(self):
        """Test Markdown export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = ReportExporter(output_dir=tmpdir)
            
            filepath = exporter.export(
                content="# Test Report\n\nThis is a test.",
                title="Test",
                format=ExportFormat.MARKDOWN
            )
            
            assert filepath.exists()
            assert filepath.suffix == ".md"
            
            content = filepath.read_text(encoding='utf-8')
            assert "Test Report" in content
    
    def test_html_export(self):
        """Test HTML export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = ReportExporter(output_dir=tmpdir)
            
            filepath = exporter.export(
                content="Test content",
                title="Test HTML",
                format=ExportFormat.HTML
            )
            
            assert filepath.exists()
            assert filepath.suffix == ".html"
            
            content = filepath.read_text(encoding='utf-8')
            assert "<!DOCTYPE html>" in content
            assert "Test HTML" in content
    
    def test_json_export(self):
        """Test JSON export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = ReportExporter(output_dir=tmpdir)
            
            filepath = exporter.export(
                content="Test content",
                title="Test JSON",
                format=ExportFormat.JSON,
                metadata={"key": "value"}
            )
            
            assert filepath.exists()
            assert filepath.suffix == ".json"
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            assert data["title"] == "Test JSON"
            assert data["content"] == "Test content"
            assert data["metadata"]["key"] == "value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
