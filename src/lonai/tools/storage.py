"""Storage manager for persisting research data."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StorageManager:
    """Manages storage and retrieval of research data."""
    
    def __init__(self, data_dir: Path, auto_save: bool = True):
        """Initialize storage manager.
        
        Args:
            data_dir: Directory for storing research data
            auto_save: Whether to automatically save data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.auto_save = auto_save
        logger.info(f"StorageManager initialized with data_dir: {self.data_dir}")
    
    def save_research(
        self,
        query: str,
        results: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Save research results to disk.
        
        Args:
            query: Research query
            results: Research results (can be any JSON-serializable data)
            metadata: Optional metadata to include
            
        Returns:
            Path to the saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in query)
        safe_query = safe_query.replace(' ', '_')[:50]  # Limit filename length
        
        filename = f"{timestamp}_{safe_query}.json"
        filepath = self.data_dir / filename
        
        data = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "metadata": metadata or {},
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Research saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving research: {e}")
            raise
    
    def load_research(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load research results from disk.
        
        Args:
            filename: Name of the file to load
            
        Returns:
            Research data dictionary or None if not found
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Research loaded from: {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading research: {e}")
            return None
    
    def list_research(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List all saved research files.
        
        Args:
            limit: Maximum number of files to return (most recent first)
            
        Returns:
            List of research file metadata
        """
        files = sorted(
            self.data_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if limit:
            files = files[:limit]
        
        results = []
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                results.append({
                    "filename": filepath.name,
                    "query": data.get("query", ""),
                    "timestamp": data.get("timestamp", ""),
                    "path": str(filepath),
                })
            except Exception as e:
                logger.warning(f"Error reading {filepath}: {e}")
                continue
        
        return results
    
    def search_research(self, keyword: str) -> List[Dict[str, Any]]:
        """Search for research files by keyword.
        
        Args:
            keyword: Keyword to search for in queries
            
        Returns:
            List of matching research file metadata
        """
        all_research = self.list_research()
        keyword_lower = keyword.lower()
        
        return [
            r for r in all_research
            if keyword_lower in r.get("query", "").lower()
        ]
    
    def delete_research(self, filename: str) -> bool:
        """Delete a research file.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        filepath = self.data_dir / filename
        
        try:
            if filepath.exists():
                filepath.unlink()
                logger.info(f"Deleted research file: {filepath}")
                return True
            else:
                logger.warning(f"File not found: {filepath}")
                return False
        except Exception as e:
            logger.error(f"Error deleting research: {e}")
            return False
