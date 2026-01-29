"""Report exporter for generating various output formats."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from lonai.config.constants import ExportFormat

logger = logging.getLogger(__name__)


class ReportExporter:
    """Exports research reports in various formats."""
    
    def __init__(self, output_dir: Path):
        """Initialize report exporter.
        
        Args:
            output_dir: Directory for exported reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ReportExporter initialized with output_dir: {self.output_dir}")
    
    def export(
        self,
        content: str,
        title: str,
        format: ExportFormat = ExportFormat.MARKDOWN,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Export report in specified format.
        
        Args:
            content: Report content
            title: Report title
            format: Export format (markdown, html, json)
            metadata: Optional metadata to include
            
        Returns:
            Path to the exported file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in title)
        safe_title = safe_title.replace(' ', '_')[:50]
        
        if format == ExportFormat.MARKDOWN:
            return self._export_markdown(content, safe_title, timestamp, metadata)
        elif format == ExportFormat.HTML:
            return self._export_html(content, safe_title, title, timestamp, metadata)
        elif format == ExportFormat.JSON:
            return self._export_json(content, title, timestamp, metadata)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_markdown(
        self,
        content: str,
        safe_title: str,
        timestamp: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Path:
        """Export as Markdown file."""
        filename = f"{timestamp}_{safe_title}.md"
        filepath = self.output_dir / filename
        
        # Add metadata header
        header = f"# {safe_title.replace('_', ' ').title()}\n\n"
        header += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        if metadata:
            header += "## Metadata\n\n"
            for key, value in metadata.items():
                header += f"- **{key}**: {value}\n"
            header += "\n---\n\n"
        
        full_content = header + content
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            logger.info(f"Markdown report exported to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting markdown: {e}")
            raise
    
    def _export_html(
        self,
        content: str,
        safe_title: str,
        title: str,
        timestamp: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Path:
        """Export as HTML file with styling."""
        filename = f"{timestamp}_{safe_title}.html"
        filepath = self.output_dir / filename
        
        # Convert markdown-style content to HTML (basic conversion)
        html_content = content.replace('\n', '<br>\n')
        html_content = self._simple_markdown_to_html(html_content)
        
        # Build metadata section
        metadata_html = ""
        if metadata:
            metadata_html = "<div class='metadata'><h2>Metadata</h2><ul>"
            for key, value in metadata.items():
                metadata_html += f"<li><strong>{key}:</strong> {value}</li>"
            metadata_html += "</ul></div>"
        
        # Create complete HTML document
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-style: italic;
            margin-bottom: 20px;
        }}
        .metadata {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .metadata ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        .content {{
            margin-top: 30px;
        }}
        code {{
            background-color: #f8f8f8;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        {metadata_html}
        <div class="content">
            {html_content}
        </div>
    </div>
</body>
</html>
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"HTML report exported to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting HTML: {e}")
            raise
    
    def _export_json(
        self,
        content: str,
        title: str,
        timestamp: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Path:
        """Export as JSON file."""
        safe_title = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in title)
        safe_title = safe_title.replace(' ', '_')[:50]
        
        filename = f"{timestamp}_{safe_title}.json"
        filepath = self.output_dir / filename
        
        data = {
            "title": title,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON report exported to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting JSON: {e}")
            raise
    
    def _simple_markdown_to_html(self, text: str) -> str:
        """Simple markdown to HTML conversion.
        
        Args:
            text: Markdown text
            
        Returns:
            HTML text
        """
        # This is a very basic conversion - for production use a proper markdown library
        lines = text.split('\n')
        result = []
        
        for line in lines:
            # Headers
            if line.startswith('### '):
                result.append(f"<h3>{line[4:]}</h3>")
            elif line.startswith('## '):
                result.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith('# '):
                result.append(f"<h1>{line[2:]}</h1>")
            # Bold
            elif '**' in line:
                line = line.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
                result.append(line)
            # Lists
            elif line.strip().startswith('- '):
                result.append(f"<li>{line.strip()[2:]}</li>")
            else:
                result.append(line)
        
        return '\n'.join(result)
