"""Constants and enumerations for the research assistant."""

from enum import Enum
from pathlib import Path


class SearchTopic(str, Enum):
    """Available search topics."""
    
    GENERAL = "general"
    NEWS = "news"
    FINANCE = "finance"


class ExportFormat(str, Enum):
    """Available export formats."""
    
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"


class StorageBackend(str, Enum):
    """Available storage backends."""
    
    JSON = "json"
    SQLITE = "sqlite"


class AgentProvider(str, Enum):
    """Available AI agent providers."""
    
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    CUSTOM = "custom"


# Default values
DEFAULT_MAX_RESULTS = 5
DEFAULT_SEARCH_TOPIC = SearchTopic.GENERAL
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096

# File paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESEARCH_DIR = DATA_DIR / "research"
REPORTS_DIR = DATA_DIR / "reports"
LOGS_DIR = PROJECT_ROOT / "logs"
CONFIG_DIR = PROJECT_ROOT / "config"

# Ensure directories exist
RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
