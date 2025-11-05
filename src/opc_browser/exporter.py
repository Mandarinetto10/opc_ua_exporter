"""
Export context implementing Strategy Pattern for multi-format export.

This module provides a unified interface for exporting OPC UA browse results
to various file formats. It uses the Strategy Pattern to allow easy addition
of new export formats without modifying existing code (Open/Closed Principle).
"""

from datetime import datetime
from pathlib import Path

from loguru import logger

from .models import BrowseResult
from .strategies.base import ExportStrategy
from .strategies.csv_strategy import CsvExportStrategy
from .strategies.json_strategy import JsonExportStrategy
from .strategies.xml_strategy import XmlExportStrategy


class ExporterError(Exception):
    """Base exception for exporter errors."""

    pass


class Exporter:
    """
    Export context that delegates to format-specific strategies.

    This class serves as a facade for the export functionality, providing:
    - Automatic strategy selection based on format
    - Default output path generation with timestamps
    - Directory creation for output files
    - Unified error handling

    The Strategy Pattern allows adding new export formats by simply:
    1. Creating a new strategy class inheriting from ExportStrategy
    2. Adding it to STRATEGIES dict
    3. Adding format name to supported formats list

    Attributes:
        export_format: Selected export format (csv, json, xml)
        strategy: Concrete strategy instance for the format

    Example:
        >>> result = await browser.browse()
        >>> exporter = Exporter(export_format="json")
        >>> output_path = await exporter.export(result)
        >>> print(f"Exported to {output_path}")
    """

    STRATEGIES: dict[str, type[ExportStrategy]] = {
        "csv": CsvExportStrategy,
        "json": JsonExportStrategy,
        "xml": XmlExportStrategy,
    }

    def __init__(self, export_format: str = "csv", full_export: bool = False) -> None:
        """
        Initialize exporter with specified format.

        Args:
            export_format: Export format name (csv, json, xml)
            full_export: If True, export includes all OPC UA extended attributes

        Raises:
            ValueError: If export_format is not supported
        """
        export_format = export_format.lower()

        if export_format not in self.STRATEGIES:
            supported = ", ".join(self.STRATEGIES.keys())
            error_msg = (
                f"Unsupported export format '{export_format}'. " f"Supported formats: {supported}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        self.export_format = export_format
        self.full_export = full_export  # NEW
        self.strategy = self.STRATEGIES[export_format]()

        logger.debug("Exporter initialized successfully")
        logger.debug(f"   Format: {export_format.upper()}")
        logger.debug(f"   Full Export: {full_export}")
        logger.debug(f"   Strategy: {self.strategy.__class__.__name__}")

    async def export(
        self,
        result: BrowseResult,
        output_path: Path | None = None,
    ) -> Path:
        """
        Export browse result to file using selected strategy.

        This method:
        1. Validates the browse result
        2. Generates default output path if not provided
        3. Ensures output directory exists
        4. Delegates export to format-specific strategy
        5. Returns the path to the created file

        Args:
            result: BrowseResult containing nodes to export
            output_path: Optional custom output path

        Returns:
            Path: Absolute path to the exported file

        Raises:
            ValueError: If result is invalid or empty
            IOError: If file cannot be written
            ExporterError: If export operation fails
        """
        logger.debug("=" * 80)
        logger.debug("EXPORT OPERATION DETAILS")
        logger.debug("=" * 80)
        logger.debug(f"Format:       {self.export_format.upper()}")
        logger.debug(f"Total Nodes:  {result.total_nodes}")
        logger.debug(f"Max Depth:    {result.max_depth_reached}")
        logger.debug(f"Namespaces:   {len(result.namespaces)}")

        # Validate result early
        if not result.success:
            error_msg = f"Cannot export failed browse result: {result.error_message}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if not result.nodes:
            error_msg = "Cannot export empty result - no nodes discovered"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Generate default output path if not provided
        if output_path is None:
            output_path = self._generate_default_path()
            logger.debug(f"Auto-generated output path: {output_path}")
        else:
            logger.debug(f"Using custom output path: {output_path}")

        # Ensure parent directory exists
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Output directory ready: {output_path.parent.absolute()}")
        except Exception as e:
            error_msg = f"Failed to create output directory: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise OSError(error_msg) from e

        # Delegate to strategy with full_export flag
        try:
            await self.strategy.export(result, output_path, self.full_export)  # MODIFIED

            # Verify file was created
            if not output_path.exists():
                error_msg = f"Export completed but output file not found: {output_path}"
                logger.error(error_msg)
                raise ExporterError(error_msg)

            logger.debug("=" * 80)
            logger.debug("EXPORT VERIFICATION")
            logger.debug("=" * 80)
            logger.debug(f"File exists: {output_path.exists()}")
            logger.debug(f"File size: {output_path.stat().st_size:,} bytes")
            logger.debug("=" * 80)

            return output_path.absolute()

        except ValueError:
            # Already logged by strategy
            raise
        except OSError:
            # Already logged by strategy
            raise
        except Exception as e:
            error_msg = f"Export operation failed: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise ExporterError(error_msg) from e

    def _generate_default_path(self) -> Path:
        """
        Generate default output path with timestamp.

        The default path format is:
        export/opcua_export_YYYYMMDD_HHMMSS.<format>

        Returns:
            Path: Default output file path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"opcua_export_{timestamp}.{self.export_format}"
        default_path = Path("export") / filename

        logger.debug(f"Generated default filename: {filename}")

        return default_path

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """
        Get list of supported export format names.

        Returns:
            list[str]: List of format names (e.g., ['csv', 'json', 'xml'])
        """
        return list(cls.STRATEGIES.keys())
