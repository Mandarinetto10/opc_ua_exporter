"""
CSV export strategy implementation.
"""

import csv
from pathlib import Path

from loguru import logger

from ..models import BrowseResult
from .base import ExportStrategy


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

    async def export(
        self, 
        result: BrowseResult, 
        output_path: Path,
        full_export: bool = False  # NEW
    ) -> None:
        """Export nodes to CSV file with proper quoting for Excel compatibility.

        Args:
            result: BrowseResult to export
            output_path: Path to output CSV file
            full_export: If True, include all OPC UA extended attributes
        """
        logger.debug(f"CSV export started: {len(result.nodes)} nodes to {output_path}")

        self.validate_result(result)
        self.ensure_output_directory(output_path)

        logger.info(f"Exporting {len(result.nodes)} nodes to CSV: {output_path}")

        try:
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(
                    csvfile,
                    delimiter=',',
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL
                )

                # Write header
                headers = result.nodes[0].get_csv_headers(full_export)  # MODIFIED
                writer.writerow(headers)
                logger.debug(f"CSV headers written: {len(headers)} columns")

                # Write data rows
                nodes_written = 0
                for node in result.nodes:
                    writer.writerow(node.to_csv_row(full_export))  # MODIFIED
                    nodes_written += 1

                    if nodes_written % 100 == 0:
                        logger.debug(f"Progress: {nodes_written}/{len(result.nodes)} nodes written")

                logger.debug(f"All {nodes_written} node rows written")

            file_size = output_path.stat().st_size
            logger.debug(f"CSV file written successfully: {file_size:,} bytes")

        except OSError as e:
            error_msg = f"Failed to write CSV file: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise OSError(error_msg) from e
        except Exception as e:
            error_msg = f"CSV export failed: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise

    def get_file_extension(self) -> str:
        """Get CSV file extension."""
        return "csv"
