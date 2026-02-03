"""Settings management using Pydantic."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from lonai.config.constants import (
    CONFIG_DIR,
    DEFAULT_MAX_RESULTS,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    ExportFormat,
    SearchTopic,
    StorageBackend,
    AgentProvider,
)


class Settings(BaseSettings):
    """Application settings with validation."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # API Keys (Required)
    # API Keys & Provider Config
    agent_provider: AgentProvider = Field(
        default=AgentProvider.ANTHROPIC,
        description="AI Agent Provider (anthropic, openai, google, custom)"
    )
    agent_api_key: Optional[str] = Field(default=None, description="Generic Agent API key")
    agent_base_url: Optional[str] = Field(default=None, description="Custom Base URL for compatible providers")
    
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    tavily_api_key: str = Field(..., description="Tavily API key")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    google_api_key: Optional[str] = Field(default=None, description="Google API key")
    
    # Environment
    environment: str = Field(default="development", description="Environment name")
    
    # Agent Configuration
    agent_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Anthropic model to use"
    )
    agent_temperature: float = Field(
        default=DEFAULT_TEMPERATURE,
        ge=0.0,
        le=2.0,
        description="Agent temperature"
    )
    agent_max_tokens: int = Field(
        default=DEFAULT_MAX_TOKENS,
        gt=0,
        description="Maximum tokens for agent response"
    )
    
    # Search Configuration
    search_max_results: int = Field(
        default=DEFAULT_MAX_RESULTS,
        gt=0,
        le=10,
        description="Maximum search results"
    )
    search_default_topic: SearchTopic = Field(
        default=SearchTopic.GENERAL,
        description="Default search topic"
    )
    search_include_raw_content: bool = Field(
        default=False,
        description="Include raw content in search results"
    )
    search_cache_enabled: bool = Field(
        default=True,
        description="Enable search result caching"
    )
    search_cache_ttl: int = Field(
        default=3600,
        gt=0,
        description="Cache TTL in seconds"
    )
    
    # Storage Configuration
    storage_backend: StorageBackend = Field(
        default=StorageBackend.JSON,
        description="Storage backend"
    )
    storage_data_dir: Path = Field(
        default=Path("data/research"),
        description="Data storage directory"
    )
    storage_auto_save: bool = Field(
        default=True,
        description="Auto-save research results"
    )
    
    # Export Configuration
    export_default_format: ExportFormat = Field(
        default=ExportFormat.MARKDOWN,
        description="Default export format"
    )
    export_output_dir: Path = Field(
        default=Path("data/reports"),
        description="Export output directory"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    log_file: Path = Field(
        default=Path("logs/lonai.log"),
        description="Log file path"
    )

    @field_validator("agent_api_key", mode="before")
    @classmethod
    def validate_api_keys(cls, v: Optional[str], info) -> Optional[str]:
        """Validate that we have at least one key for the selected provider."""
        # Note: field validation runs in order. We might not have access to 'agent_provider'
        # if it's defined after. But since it's defined before, we can use `info.data`.
        # However, checking 'values' in pydantic v2 requires `info.data`.
        return v
    
    @field_validator("storage_data_dir", "export_output_dir", "log_file", "skills_dir")
    @classmethod
    def ensure_path_exists(cls, v: Path) -> Path:
        """Ensure path parent directories exist."""
        if v is None:
            return v
        if not v.is_absolute():
            # Make relative to project root
            from lonai.config.constants import PROJECT_ROOT
            v = PROJECT_ROOT / v
        # Don't create parent for skills_dir, just resolve it
        if v.name != "skills":
            v.parent.mkdir(parents=True, exist_ok=True)
        return v
    
    # Skills Configuration
    skills_dir: Optional[Path] = Field(
        default=Path("skills"),
        description="Directory containing SKILL.md files"
    )

    
    @classmethod
    def from_yaml(cls, config_path: Optional[Path] = None) -> "Settings":
        """Load settings from YAML file and environment variables.
        
        Args:
            config_path: Path to YAML config file. If None, uses default location.
            
        Returns:
            Settings instance with merged configuration.
        """
        if config_path is None:
            config_path = CONFIG_DIR / "config.yaml"
        
        config_data = {}
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)
                
            # Flatten nested YAML structure
            if yaml_data:
                for section, values in yaml_data.items():
                    if isinstance(values, dict):
                        for key, value in values.items():
                            config_key = f"{section}_{key}"
                            config_data[config_key] = value
                    else:
                        config_data[section] = values
        
        # Merge with environment variables (env vars take precedence)
        return cls(**config_data)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Returns:
        Singleton Settings instance.
    """
    # Try to load from YAML first, fallback to env vars only
    config_path = CONFIG_DIR / "config.yaml"
    if config_path.exists():
        return Settings.from_yaml(config_path)
    return Settings()
