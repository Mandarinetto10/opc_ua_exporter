"""
Abstract base class for export strategies.
Implements Strategy Pattern following Open/Closed Principle (OCP).
"""

from abc import ABC, abstractmethod
from pathlib import Path
from ..models import BrowseResult


class ExportStrategy(ABC):
    """
    Abstract base class for export strategies.
    
    Defines the interface that all concrete export strategies must implement.
    This allows adding new export formats without modifying existing code (OCP).
    """
    
    @abstractmethod
    async def export(self, result: BrowseResult, output_path: Path) -> None:
        """
        Export browse result to a file.
        
        Args:
            result: BrowseResult containing nodes to export
            output_path: Path where the file should be saved
            
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
            raise ValueError(f"Browse failed: {result.error_message}")
        
        if not result.nodes:
            raise ValueError("No nodes to export")
    
    def ensure_output_directory(self, output_path: Path) -> None:
        """
        Ensure output directory exists.
        
        Args:
            output_path: Path to the output file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)