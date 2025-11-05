"""Comprehensive tests for Exporter module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from opc_browser.exporter import Exporter, ExporterError
from opc_browser.models import BrowseResult, OpcUaNode


class TestExporterInit:
    """Test Exporter initialization."""

    def test_init_default_format(self):
        """Test initialization with default format."""
        exporter = Exporter()
        assert exporter.export_format == "csv"
        assert exporter.full_export is False

    def test_init_custom_format(self):
        """Test initialization with custom format."""
        exporter = Exporter(export_format="json")
        assert exporter.export_format == "json"

    def test_init_full_export(self):
        """Test initialization with full_export enabled."""
        exporter = Exporter(export_format="xml", full_export=True)
        assert exporter.export_format == "xml"
        assert exporter.full_export is True

    def test_init_case_insensitive(self):
        """Test format is case insensitive."""
        exporter = Exporter(export_format="CSV")
        assert exporter.export_format == "csv"

    def test_init_invalid_format(self):
        """Test initialization with invalid format raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            Exporter(export_format="invalid")
        assert "Unsupported export format" in str(exc_info.value)
        assert "invalid" in str(exc_info.value)

    def test_get_supported_formats(self):
        """Test get_supported_formats returns all formats."""
        formats = Exporter.get_supported_formats()
        assert "csv" in formats
        assert "json" in formats
        assert "xml" in formats
        assert len(formats) == 3


class TestExporterExport:
    """Test export method."""

    @pytest.mark.asyncio
    async def test_export_success_csv(self, tmp_path):
        """Test successful CSV export."""
        result = BrowseResult()
        result.success = True
        result.total_nodes = 2
        result.namespaces = {0: "http://opcfoundation.org/UA/"}

        node1 = OpcUaNode(
            node_id="i=84",
            browse_name="Root",
            display_name="Root",
            node_class="Object",
        )
        node2 = OpcUaNode(
            node_id="i=85",
            browse_name="Objects",
            display_name="Objects",
            node_class="Object",
        )
        result.add_node(node1)
        result.add_node(node2)

        exporter = Exporter(export_format="csv")
        output_path = tmp_path / "test.csv"

        final_path = await exporter.export(result, output_path)

        assert final_path.exists()
        assert final_path == output_path.absolute()
        assert final_path.stat().st_size > 0

    @pytest.mark.asyncio
    async def test_export_success_json(self, tmp_path):
        """Test successful JSON export."""
        result = BrowseResult()
        result.success = True
        result.total_nodes = 1
        result.namespaces = {0: "http://opcfoundation.org/UA/"}

        node = OpcUaNode(
            node_id="i=84",
            browse_name="Root",
            display_name="Root",
            node_class="Object",
        )
        result.add_node(node)

        exporter = Exporter(export_format="json")
        output_path = tmp_path / "test.json"

        final_path = await exporter.export(result, output_path)

        assert final_path.exists()
        assert final_path.suffix == ".json"

    @pytest.mark.asyncio
    async def test_export_success_xml(self, tmp_path):
        """Test successful XML export."""
        result = BrowseResult()
        result.success = True
        result.total_nodes = 1
        result.namespaces = {0: "http://opcfoundation.org/UA/"}

        node = OpcUaNode(
            node_id="i=84",
            browse_name="Root",
            display_name="Root",
            node_class="Object",
        )
        result.add_node(node)

        exporter = Exporter(export_format="xml")
        output_path = tmp_path / "test.xml"

        final_path = await exporter.export(result, output_path)

        assert final_path.exists()
        assert final_path.suffix == ".xml"

    @pytest.mark.asyncio
    async def test_export_auto_generate_path(self):
        """Test export with auto-generated path."""
        result = BrowseResult()
        result.success = True
        result.total_nodes = 1
        result.namespaces = {0: "http://opcfoundation.org/UA/"}

        node = OpcUaNode(
            node_id="i=84",
            browse_name="Root",
            display_name="Root",
            node_class="Object",
        )
        result.add_node(node)

        exporter = Exporter(export_format="csv")

        final_path = await exporter.export(result)

        assert final_path.exists()
        assert final_path.parent.name == "export"
        assert final_path.name.startswith("opcua_export_")
        assert final_path.suffix == ".csv"

        # Cleanup
        final_path.unlink()

    @pytest.mark.asyncio
    async def test_export_failed_result(self):
        """Test export with failed browse result raises ValueError."""
        result = BrowseResult()
        result.success = False
        result.error_message = "Connection failed"

        exporter = Exporter()

        with pytest.raises(ValueError) as exc_info:
            await exporter.export(result)
        assert "failed browse result" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_empty_result(self):
        """Test export with empty result raises ValueError."""
        result = BrowseResult()
        result.success = True
        result.nodes = []

        exporter = Exporter()

        with pytest.raises(ValueError) as exc_info:
            await exporter.export(result)
        assert "empty result" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_creates_parent_directory(self, tmp_path):
        """Test export creates parent directory if missing."""
        result = BrowseResult()
        result.success = True
        result.total_nodes = 1
        result.namespaces = {0: "http://opcfoundation.org/UA/"}

        node = OpcUaNode(
            node_id="i=84",
            browse_name="Root",
            display_name="Root",
            node_class="Object",
        )
        result.add_node(node)

        exporter = Exporter()
        output_path = tmp_path / "subdir" / "nested" / "test.csv"

        assert not output_path.parent.exists()

        final_path = await exporter.export(result, output_path)

        assert output_path.parent.exists()
        assert final_path.exists()

    @pytest.mark.asyncio
    async def test_export_directory_creation_error(self, tmp_path):
        """Test export handles directory creation errors."""
        result = BrowseResult()
        result.success = True
        result.total_nodes = 1
        result.namespaces = {0: "http://opcfoundation.org/UA/"}

        node = OpcUaNode(
            node_id="i=84",
            browse_name="Root",
            display_name="Root",
            node_class="Object",
        )
        result.add_node(node)

        exporter = Exporter()
        output_path = tmp_path / "test.csv"

        # Mock mkdir to raise OSError
        with patch.object(Path, "mkdir", side_effect=OSError("Permission denied")):
            with pytest.raises(OSError) as exc_info:
                await exporter.export(result, output_path)
            assert "output directory" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_export_strategy_raises_exception(self, tmp_path):
        """Test export handles strategy exceptions."""
        result = BrowseResult()
        result.success = True
        result.total_nodes = 1
        result.namespaces = {0: "http://opcfoundation.org/UA/"}

        node = OpcUaNode(
            node_id="i=84",
            browse_name="Root",
            display_name="Root",
            node_class="Object",
        )
        result.add_node(node)

        exporter = Exporter()
        output_path = tmp_path / "test.csv"

        # Mock strategy.export to raise exception
        with patch.object(exporter.strategy, "export", side_effect=RuntimeError("Export error")):
            with pytest.raises(ExporterError) as exc_info:
                await exporter.export(result, output_path)
            assert "Export operation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_full_export_flag(self, tmp_path):
        """Test export passes full_export flag to strategy."""
        result = BrowseResult()
        result.success = True
        result.total_nodes = 1
        result.namespaces = {0: "http://opcfoundation.org/UA/"}

        node = OpcUaNode(
            node_id="i=84",
            browse_name="Root",
            display_name="Root",
            node_class="Object",
        )
        result.add_node(node)

        exporter = Exporter(full_export=True)
        output_path = tmp_path / "test.csv"

        # Mock strategy.export to track calls AND create the file
        async def mock_export(r, p, full):
            # Create the file to satisfy exporter.export's file existence check
            p.write_text("mock,data\n")

        exporter.strategy.export = AsyncMock(side_effect=mock_export)

        await exporter.export(result, output_path)

        exporter.strategy.export.assert_called_once()
        call_args = exporter.strategy.export.call_args
        assert call_args[0][1] == output_path
        assert call_args[0][2] is True  # full_export


class TestGenerateDefaultPath:
    """Test _generate_default_path method."""

    def test_generate_default_path_format(self):
        """Test default path format."""
        exporter = Exporter(export_format="csv")
        path = exporter._generate_default_path()

        assert path.parent.name == "export"
        assert path.name.startswith("opcua_export_")
        assert path.suffix == ".csv"

    def test_generate_default_path_timestamp(self):
        """Test default path contains timestamp."""
        exporter = Exporter()
        path1 = exporter._generate_default_path()

        import time

        time.sleep(1.1)  # Increase delay to ensure different seconds

        path2 = exporter._generate_default_path()

        # Different timestamps should produce different filenames
        assert path1 != path2

    def test_generate_default_path_different_formats(self):
        """Test default path for different formats."""
        csv_exporter = Exporter(export_format="csv")
        json_exporter = Exporter(export_format="json")
        xml_exporter = Exporter(export_format="xml")

        csv_path = csv_exporter._generate_default_path()
        json_path = json_exporter._generate_default_path()
        xml_path = xml_exporter._generate_default_path()

        assert csv_path.suffix == ".csv"
        assert json_path.suffix == ".json"
        assert xml_path.suffix == ".xml"
