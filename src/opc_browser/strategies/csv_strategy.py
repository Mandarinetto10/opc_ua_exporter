"""
CSV export strategy implementation.
"""

import csv
from pathlib import Path
from loguru import logger

from .base import ExportStrategy
from ..models import BrowseResult, OpcUaNode


class CsvExportStrategy(ExportStrategy):
    """
    Exports browse results to CSV format.
    
    CSV format is ideal for:
    - Spreadsheet applications (Excel, LibreOffice Calc)
    - Data analysis tools
    - Simple text processing
    """
    
    async def export(self, result: BrowseResult, output_path: Path) -> None:
        """
        Export nodes to CSV file.
        
        Args:
            result: BrowseResult to export
            output_path: Path to output CSV file
        """
        self.validate_result(result)
        self.ensure_output_directory(output_path)
        
        logger.info(f"Exporting {len(result.nodes)} nodes to CSV: {output_path}")
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                headers = OpcUaNode.get_csv_headers()
                writer.writerow(headers)
                
                # Write data rows
                for node in result.nodes:
                    writer.writerow(node.to_csv_row())
                
                # Write summary rows
                writer.writerow([])  # Empty row
                writer.writerow(["# Summary"])
                writer.writerow(["Total Nodes", result.total_nodes])
                writer.writerow(["Max Depth", result.max_depth_reached])
                writer.writerow(["Namespaces", len(result.namespaces)])
                
                # Write namespace information
                if result.namespaces:
                    writer.writerow([])
                    writer.writerow(["# Namespaces"])
                    writer.writerow(["Index", "URI"])
                    for idx, uri in result.namespaces.items():
                        writer.writerow([idx, uri])
            
            logger.success(f"CSV export completed: {output_path}")
            
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            raise
    
    def get_file_extension(self) -> str:
        """Get CSV file extension."""
        return "csv"