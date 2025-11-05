"""
Abstract base class for export strategies.
Implements Strategy Pattern following Open/Closed Principle (OCP).
"""

from abc import ABC, abstractmethod
from pathlib import Path

from loguru import logger

from ..models import BrowseResult


class ExportStrategy(ABC):
    """
    Abstract base class for export strategies.

    Defines the interface that all concrete export strategies must implement.
    This allows adding new export formats without modifying existing code (OCP).
    """

    @abstractmethod
    async def export(
        self,
        result: BrowseResult,
        output_path: Path,
        full_export: bool = False,  # NEW
    ) -> None:
        """
        Export browse result to a file.

        Args:
            result: BrowseResult containing nodes to export
            output_path: Path where the file should be saved
            full_export: If True, include all OPC UA extended attributes

        Raises:
            Exception: If export fails
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """
        Get the file extension for this export format.

        Returns:
            File extension (e.g., 'csv', 'json', 'xml')
        """
        pass

    def validate_result(self, result: BrowseResult) -> None:
        """
        Validate browse result before export.

        Args:
            result: BrowseResult to validate

        Raises:
            ValueError: If result is invalid
        """
        if not result.success:
            error_msg = f"Browse operation failed: {result.error_message}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if not result.nodes:
            error_msg = "No nodes to export - browse result is empty"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.debug(f"✅ Validation passed: {len(result.nodes)} nodes ready for export")
        logger.debug(f"   Max depth: {result.max_depth_reached}")
        logger.debug(f"   Namespaces: {len(result.namespaces)}")

    def ensure_output_directory(self, output_path: Path) -> None:
        """
        Ensure output directory exists.

        Args:
            output_path: Path to the output file

        Raises:
            IOError: If directory cannot be created
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"✅ Output directory ensured: {output_path.parent.absolute()}")
        except Exception as e:
            error_msg = f"Failed to create output directory: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise OSError(error_msg) from e
