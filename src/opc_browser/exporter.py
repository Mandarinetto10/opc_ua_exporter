"""
Export context implementing Strategy Pattern for multi-format export.

This module provides a unified interface for exporting OPC UA browse results
to various file formats. It uses the Strategy Pattern to allow easy addition
of new export formats without modifying existing code (Open/Closed Principle).
"""

from pathlib import Path
from datetime import datetime
from typing import Optional
from loguru import logger

from .models import BrowseResult
from .strategies.base import ExportStrategy
from .strategies.csv_strategy import CsvExportStrategy
from .strategies.json_strategy import JsonExportStrategy
from .strategies.xml_strategy import XmlExportStrategy


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
    
    def __init__(self, export_format: str = "csv") -> None:
        """
        Initialize exporter with specified format.
        
        Args:
            export_format: Export format name (csv, json, xml)
            
        Raises:
            ValueError: If export_format is not supported
        """
        if export_format not in self.STRATEGIES:
            raise ValueError(
                f"Unsupported format '{export_format}'. "
                f"Supported: {', '.join(self.STRATEGIES.keys())}"
            )
        
        self.export_format = export_format
        self.strategy = self.STRATEGIES[export_format]()
        
        logger.debug(f"Exporter initialized for {export_format.upper()} format")
    
    async def export(
        self,
        result: BrowseResult,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Export browse result to file using selected strategy.
        
        This method:
        1. Generates default output path if not provided
        2. Ensures output directory exists
        3. Delegates export to format-specific strategy
        4. Returns the path to the created file
        
        Args:
            result: BrowseResult containing nodes to export
            output_path: Optional custom output path
            
        Returns:
            Path: Absolute path to the exported file
            
        Raises:
            ValueError: If result is invalid or empty
            IOError: If file cannot be written
        """
        # Generate default output path if not provided
        if output_path is None:
            output_path = self._generate_default_path()
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"Starting {self.export_format.upper()} export to {output_path}")
        
        # Delegate to strategy
        await self.strategy.export(result, output_path)
        
        return output_path
    
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
        return Path("export") / filename
    
    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """
        Get list of supported export format names.
        
        Returns:
            list[str]: List of format names (e.g., ['csv', 'json', 'xml'])
        """
        return list(cls.STRATEGIES.keys())