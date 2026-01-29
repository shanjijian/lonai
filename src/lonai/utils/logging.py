"""Logging configuration."""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Optional

import yaml

from lonai.config.constants import CONFIG_DIR, LOGS_DIR


def setup_logging(
    config_path: Optional[Path] = None,
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> None:
    """Setup logging configuration.
    
    Args:
        config_path: Path to logging config file (YAML)
        log_level: Override log level
        log_file: Override log file path
    """
    # Ensure logs directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Try to load from config file
    if config_path is None:
        config_path = CONFIG_DIR / "logging.yaml"
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Override log file if specified
            if log_file:
                for handler in config.get('handlers', {}).values():
                    if 'filename' in handler:
                        handler['filename'] = str(log_file)
            
            logging.config.dictConfig(config)
            
            # Override log level if specified
            if log_level:
                logging.getLogger().setLevel(log_level)
            
            return
        except Exception as e:
            print(f"Warning: Failed to load logging config from {config_path}: {e}", file=sys.stderr)
    
    # Fallback to basic configuration
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    level = getattr(logging, log_level.upper() if log_level else 'INFO')
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    else:
        default_log_file = LOGS_DIR / "lonai.log"
        handlers.append(logging.FileHandler(default_log_file))
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
