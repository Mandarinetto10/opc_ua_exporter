"""
JSON export strategy implementation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from ..models import BrowseResult
from .base import ExportStrategy


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
        Export nodes to JSON file with pretty formatting.

        Creates a well-structured JSON file with:
        - Metadata section with statistics
        - Namespaces array with index and URI
        - Nodes array with complete node information
        - ISO 8601 timestamp formatting

        Args:
            result: BrowseResult to export
            output_path: Path to output JSON file

        Raises:
            ValueError: If result is invalid or empty
            IOError: If file cannot be written
        """
        logger.debug(f"JSON export started: {len(result.nodes)} nodes to {output_path}")

        self.validate_result(result)
        self.ensure_output_directory(output_path)

        logger.info(f"Exporting {len(result.nodes)} nodes to JSON: {output_path}")

        try:
            # Build JSON structure
            logger.debug("Building JSON structure...")
            export_data: dict[str, Any] = {
                "metadata": {
                    "total_nodes": result.total_nodes,
                    "max_depth_reached": result.max_depth_reached,
                    "success": result.success,
                    "error_message": result.error_message,
                    "export_timestamp": datetime.now().isoformat(),
                },
                "namespaces": [
                    {"index": idx, "uri": uri}
                    for idx, uri in result.namespaces.items()
                ],
                "nodes": [],
            }

            logger.debug(f"Metadata created: {result.total_nodes} nodes, {len(result.namespaces)} namespaces")

            # Convert nodes to dictionaries with progress logging
            nodes_converted = 0
            for node in result.nodes:
                export_data["nodes"].append(node.to_dict())
                nodes_converted += 1

                # Progress logging for large exports
                if nodes_converted % 100 == 0:
                    logger.debug(f"Progress: {nodes_converted}/{len(result.nodes)} nodes converted")

            logger.debug(f"All {nodes_converted} nodes converted to JSON structure")

            # Write to file with pretty formatting
            logger.debug(f"Writing JSON to file: {output_path}")
            with open(output_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(
                    export_data,
                    jsonfile,
                    indent=2,
                    ensure_ascii=False,
                    default=str,  # Convert non-serializable objects (datetime, etc.) to string
                )

            file_size = output_path.stat().st_size
            logger.success(
                f"✅ JSON export completed successfully\n"
                f"   File: {output_path.absolute()}\n"
                f"   Size: {file_size / 1024:.2f} KB\n"
                f"   Nodes: {result.total_nodes}\n"
                f"   Format: UTF-8, pretty-printed with 2-space indentation"
            )

        except OSError as e:
            error_msg = f"Failed to write JSON file: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise OSError(error_msg) from e
        except json.JSONEncodeError as e:
            error_msg = f"JSON encoding failed: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise
        except Exception as e:
            error_msg = f"JSON export failed: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise

    def get_file_extension(self) -> str:
        """Get JSON file extension."""
        return "json"
