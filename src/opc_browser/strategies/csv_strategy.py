"""
CSV export strategy implementation.
"""

import csv
from pathlib import Path
from loguru import logger

from .base import ExportStrategy
from ..models import BrowseResult


class CsvExportStrategy(ExportStrategy):
    """
    Exports browse results to CSV format.
    
    CSV format is ideal for:
    - Spreadsheet applications (Excel, LibreOffice Calc)
    - Data analysis tools
    - Simple text processing
    
    The CSV uses comma (,) as delimiter and quotes fields containing
    special characters (semicolons, commas, quotes) for Excel compatibility.
    """
    
    async def export(self, result: BrowseResult, output_path: Path) -> None:
        """
        Export nodes to CSV file with proper quoting for Excel compatibility.
        
        Uses comma (,) as delimiter and automatically quotes fields containing:
        - Semicolons (;) - common in OPC UA NodeIds like "ns=2;s=Studio"
        - Commas (,)
        - Double quotes (")
        - Newlines
        
        This ensures Excel (both English and localized versions) correctly
        interprets all columns without splitting NodeIds incorrectly.
        
        Args:
            result: BrowseResult to export
            output_path: Path to output CSV file
            
        Raises:
            ValueError: If result is invalid or empty
            IOError: If file cannot be written
        """
        logger.debug(f"CSV export started: {len(result.nodes)} nodes to {output_path}")
        
        self.validate_result(result)
        self.ensure_output_directory(output_path)
        
        logger.info(f"Exporting {len(result.nodes)} nodes to CSV: {output_path}")
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                # Use comma as delimiter with QUOTE_MINIMAL for Excel compatibility
                # utf-8-sig adds BOM for Excel to recognize UTF-8 encoding
                writer = csv.writer(
                    csvfile,
                    delimiter=',',
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL
                )
                
                # Write header
                headers = result.nodes[0].get_csv_headers()
                writer.writerow(headers)
                logger.debug(f"CSV headers written: {len(headers)} columns (delimiter: comma)")
                
                # Write data rows
                nodes_written = 0
                for node in result.nodes:
                    writer.writerow(node.to_csv_row())
                    nodes_written += 1
                    
                    # Progress logging for large exports
                    if nodes_written % 100 == 0:
                        logger.debug(f"Progress: {nodes_written}/{len(result.nodes)} nodes written")
                
                logger.debug(f"All {nodes_written} node rows written")
                
                # Write summary rows
                writer.writerow([])  # Empty row
                writer.writerow(["# Summary"])
                writer.writerow(["Total Nodes", result.total_nodes])
                writer.writerow(["Max Depth", result.max_depth_reached])
                writer.writerow(["Namespaces", len(result.namespaces)])
                logger.debug("Summary section written")
                
                # Write namespace information
                if result.namespaces:
                    writer.writerow([])
                    writer.writerow(["# Namespaces"])
                    writer.writerow(["Index", "URI"])
                    for idx, uri in result.namespaces.items():
                        writer.writerow([idx, uri])
                    logger.debug(f"Namespace information written: {len(result.namespaces)} namespaces")
            
            file_size = output_path.stat().st_size
            logger.success(
                f"✅ CSV export completed successfully\n"
                f"   File: {output_path.absolute()}\n"
                f"   Size: {file_size / 1024:.2f} KB\n"
                f"   Nodes: {result.total_nodes}\n"
                f"   Format: UTF-8 with BOM, comma-delimited, quoted fields"
            )
            
        except IOError as e:
            error_msg = f"Failed to write CSV file: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg) from e
        except Exception as e:
            error_msg = f"CSV export failed: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise
    
    def get_file_extension(self) -> str:
        """Get CSV file extension."""
        return "csv"