"""
JSON export strategy implementation.
"""

import json
from pathlib import Path
from typing import Any
from loguru import logger

from .base import ExportStrategy
from ..models import BrowseResult


class JsonExportStrategy(ExportStrategy):
    """
    Exports browse results to JSON format.
    
    JSON format is ideal for:
    - Web applications and APIs
    - JavaScript/TypeScript consumption
    - Structured data interchange
    - Hierarchical data representation
    """
    
    async def export(self, result: BrowseResult, output_path: Path) -> None:
        """
        Export nodes to JSON file.
        
        Args:
            result: BrowseResult to export
            output_path: Path to output JSON file
        """
        self.validate_result(result)
        self.ensure_output_directory(output_path)
        
        logger.info(f"Exporting {len(result.nodes)} nodes to JSON: {output_path}")
        
        try:
            # Build JSON structure
            export_data: dict[str, Any] = {
                "metadata": {
                    "total_nodes": result.total_nodes,
                    "max_depth_reached": result.max_depth_reached,
                    "success": result.success,
                    "error_message": result.error_message,
                },
                "namespaces": [
                    {"index": idx, "uri": uri}
                    for idx, uri in result.namespaces.items()
                ],
                "nodes": [node.to_dict() for node in result.nodes],
            }
            
            # Write to file with pretty formatting
            with open(output_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(
                    export_data,
                    jsonfile,
                    indent=2,
                    ensure_ascii=False,
                    default=str,  # Convert non-serializable objects to string
                )
            
            logger.success(f"JSON export completed: {output_path}")
            
        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            raise
    
    def get_file_extension(self) -> str:
        """Get JSON file extension."""
        return "json"
