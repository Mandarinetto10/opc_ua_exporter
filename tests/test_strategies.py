"""Comprehensive tests for all export strategies."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from opc_browser.models import BrowseResult, OpcUaNode
from opc_browser.strategies.base import ExportStrategy
from opc_browser.strategies.csv_strategy import CsvExportStrategy
from opc_browser.strategies.json_strategy import JsonExportStrategy
from opc_browser.strategies.xml_strategy import XmlExportStrategy

# Fixtures for test data


@pytest.fixture
def sample_result():
    """Create a sample BrowseResult for testing."""
    result = BrowseResult()
    result.success = True
    result.namespaces = {0: "http://opcfoundation.org/UA/", 2: "urn:test:namespace"}

    # Root node
    root = OpcUaNode(
        node_id="i=84",
        browse_name="Root",
        display_name="Root",
        node_class="Object",
        depth=0,
        namespace_index=0,
        full_path="Root",
    )
    result.add_node(root)

    # Child object
    child_obj = OpcUaNode(
        node_id="i=85",
        browse_name="Objects",
        display_name="Objects",
        node_class="Object",
        parent_id="i=84",
        depth=1,
        namespace_index=0,
        full_path="Root/Objects",
    )
    result.add_node(child_obj)

    # Variable node
    var_node = OpcUaNode(
        node_id="ns=2;i=1000",
        browse_name="Temperature",
        display_name="Temperature Sensor",
        node_class="Variable",
        data_type="Double",
        value=23.5,
        parent_id="i=85",
        depth=2,
        namespace_index=2,
        full_path="Root/Objects/Temperature",
    )
    result.add_node(var_node)

    return result


@pytest.fixture
def full_export_result():
    """Create a BrowseResult with full export attributes."""
    result = BrowseResult()
    result.success = True
    result.namespaces = {0: "http://opcfoundation.org/UA/"}

    # Variable with all attributes
    var = OpcUaNode(
        node_id="i=100",
        browse_name="Sensor",
        display_name="Sensor",
        node_class="Variable",
        data_type="Double",
        value=42.5,
        depth=0,
        namespace_index=0,
        description="Temperature sensor",
        access_level="CurrentRead",
        user_access_level="CurrentRead",
        write_mask=123,
        user_write_mask=456,
        minimum_sampling_interval=100.0,
        historizing=True,
    )
    result.add_node(var)

    # Object with event notifier
    obj = OpcUaNode(
        node_id="i=200",
        browse_name="Device",
        display_name="Device",
        node_class="Object",
        depth=0,
        namespace_index=0,
        description="Device object",
        event_notifier=1,
    )
    result.add_node(obj)

    # Method with executable flags
    method = OpcUaNode(
        node_id="i=300",
        browse_name="Execute",
        display_name="Execute",
        node_class="Method",
        depth=0,
        namespace_index=0,
        description="Execute method",
        executable=True,
        user_executable=False,
    )
    result.add_node(method)

    return result


# Base Strategy Tests


class TestBaseStrategy:
    """Test ExportStrategy base class."""

    def test_validate_result_success(self, sample_result):
        """Test validate_result with successful result."""
        strategy = CsvExportStrategy()  # Use concrete implementation
        # Should not raise
        strategy.validate_result(sample_result)

    def test_validate_result_failed(self):
        """Test validate_result with failed result."""
        result = BrowseResult()
        result.success = False
        result.error_message = "Connection failed"

        strategy = CsvExportStrategy()
        with pytest.raises(ValueError) as exc_info:
            strategy.validate_result(result)
        assert "Browse operation failed" in str(exc_info.value)

    def test_validate_result_empty(self):
        """Test validate_result with empty nodes."""
        result = BrowseResult()
        result.success = True
        result.nodes = []

        strategy = CsvExportStrategy()
        with pytest.raises(ValueError) as exc_info:
            strategy.validate_result(result)
        assert "No nodes to export" in str(exc_info.value)

    def test_ensure_output_directory_creates(self, tmp_path):
        """Test ensure_output_directory creates missing directories."""
        strategy = CsvExportStrategy()
        output_path = tmp_path / "subdir" / "nested" / "file.csv"

        assert not output_path.parent.exists()
        strategy.ensure_output_directory(output_path)
        assert output_path.parent.exists()

    def test_ensure_output_directory_error(self, tmp_path):
        """Test ensure_output_directory handles errors."""
        from unittest.mock import patch

        strategy = CsvExportStrategy()
        output_path = tmp_path / "file.csv"

        with patch.object(Path, "mkdir", side_effect=OSError("Permission denied")):
            with pytest.raises(OSError) as exc_info:
                strategy.ensure_output_directory(output_path)
            assert "Failed to create output directory" in str(exc_info.value)


# CSV Strategy Tests


class TestCsvStrategy:
    """Test CsvExportStrategy."""

    @pytest.mark.asyncio
    async def test_export_basic(self, tmp_path, sample_result):
        """Test basic CSV export."""
        strategy = CsvExportStrategy()
        output_path = tmp_path / "test.csv"

        await strategy.export(sample_result, output_path, full_export=False)

        assert output_path.exists()

        # Verify CSV content
        with open(output_path, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)

            # Check header
            assert rows[0][0] == "NodeId"
            assert rows[0][1] == "BrowseName"
            assert "Description" not in rows[0]  # Not in basic export

            # Check data rows
            assert len(rows) == 4  # Header + 3 nodes
            assert rows[1][0] == "i=84"
            assert rows[1][1] == "Root"

    @pytest.mark.asyncio
    async def test_export_full(self, tmp_path, full_export_result):
        """Test CSV export with full_export=True."""
        strategy = CsvExportStrategy()
        output_path = tmp_path / "test_full.csv"

        await strategy.export(full_export_result, output_path, full_export=True)

        assert output_path.exists()

        # Verify extended attributes
        with open(output_path, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)

            # Check extended headers
            assert "Description" in rows[0]
            assert "AccessLevel" in rows[0]
            assert "Historizing" in rows[0]

            # Check extended data for Variable
            var_row = rows[1]
            assert "Temperature sensor" in var_row
            assert "CurrentRead" in var_row
            assert "True" in var_row  # historizing

    @pytest.mark.asyncio
    async def test_export_os_error(self, tmp_path, sample_result):
        """Test CSV export handles OSError."""
        from unittest.mock import patch

        strategy = CsvExportStrategy()
        output_path = tmp_path / "test.csv"

        with patch("builtins.open", side_effect=OSError("Disk full")):
            with pytest.raises(OSError) as exc_info:
                await strategy.export(sample_result, output_path)
            assert "Failed to write CSV file" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_general_exception(self, tmp_path, sample_result):
        """Test CSV export handles general exceptions."""
        from unittest.mock import patch

        strategy = CsvExportStrategy()
        output_path = tmp_path / "test.csv"

        with (
            patch("builtins.open", side_effect=RuntimeError("Unexpected")),
            pytest.raises(RuntimeError),
        ):
            await strategy.export(sample_result, output_path)

    def test_get_file_extension(self):
        """Test get_file_extension returns 'csv'."""
        strategy = CsvExportStrategy()
        assert strategy.get_file_extension() == "csv"


# JSON Strategy Tests


class TestJsonStrategy:
    """Test JsonExportStrategy."""

    @pytest.mark.asyncio
    async def test_export_basic(self, tmp_path, sample_result):
        """Test basic JSON export."""
        strategy = JsonExportStrategy()
        output_path = tmp_path / "test.json"

        await strategy.export(sample_result, output_path, full_export=False)

        assert output_path.exists()

        # Verify JSON content
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)

            assert "metadata" in data
            assert "nodes" in data
            assert "namespaces" in data

            assert data["metadata"]["total_nodes"] == 3
            assert data["metadata"]["full_export"] is False

            assert len(data["nodes"]) == 3
            assert data["nodes"][0]["node_id"] == "i=84"
            assert "description" not in data["nodes"][0]  # Not in basic export

    @pytest.mark.asyncio
    async def test_export_full(self, tmp_path, full_export_result):
        """Test JSON export with full_export=True."""
        strategy = JsonExportStrategy()
        output_path = tmp_path / "test_full.json"

        await strategy.export(full_export_result, output_path, full_export=True)

        assert output_path.exists()

        # Verify extended attributes
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)

            assert data["metadata"]["full_export"] is True

            # Variable with extended attrs
            var_node = data["nodes"][0]
            assert var_node["description"] == "Temperature sensor"
            assert var_node["access_level"] == "CurrentRead"
            assert var_node["historizing"] is True

            # Object with event notifier
            obj_node = data["nodes"][1]
            assert obj_node["event_notifier"] == 1

            # Method with executable flags
            method_node = data["nodes"][2]
            assert method_node["executable"] is True
            assert method_node["user_executable"] is False

    @pytest.mark.asyncio
    async def test_export_os_error(self, tmp_path, sample_result):
        """Test JSON export handles OSError."""
        from unittest.mock import patch

        strategy = JsonExportStrategy()
        output_path = tmp_path / "test.json"

        with patch("builtins.open", side_effect=OSError("Disk full")):
            with pytest.raises(OSError) as exc_info:
                await strategy.export(sample_result, output_path)
            assert "Failed to write JSON file" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_json_encode_error(self, tmp_path):
        """Test JSON export handles TypeError (encoding error)."""
        from unittest.mock import patch

        result = BrowseResult()
        result.success = True
        result.namespaces = {0: "test"}

        # Create node
        node = OpcUaNode(
            node_id="i=1", browse_name="Test", display_name="Test", node_class="Object"
        )
        result.add_node(node)

        strategy = JsonExportStrategy()
        output_path = tmp_path / "test.json"

        # json.dump can raise TypeError for encoding issues
        with (
            patch("json.dump", side_effect=TypeError("Object not JSON serializable")),
            pytest.raises(TypeError),
        ):
            await strategy.export(result, output_path)

    @pytest.mark.asyncio
    async def test_export_general_exception(self, tmp_path, sample_result):
        """Test JSON export handles general exceptions during file write."""
        from unittest.mock import mock_open, patch

        strategy = JsonExportStrategy()
        output_path = tmp_path / "test.json"

        # Mock open to succeed but json.dump to fail
        m = mock_open()
        with (
            patch("builtins.open", m),
            patch("json.dump", side_effect=RuntimeError("Unexpected")),
            pytest.raises(RuntimeError),
        ):
            await strategy.export(sample_result, output_path)

    def test_get_file_extension(self):
        """Test get_file_extension returns 'json'."""
        strategy = JsonExportStrategy()
        assert strategy.get_file_extension() == "json"


# XML Strategy Tests


class TestXmlStrategy:
    """Test XmlExportStrategy."""

    @pytest.mark.asyncio
    async def test_export_basic(self, tmp_path, sample_result):
        """Test basic XML export."""
        strategy = XmlExportStrategy()
        output_path = tmp_path / "test.xml"

        await strategy.export(sample_result, output_path, full_export=False)

        assert output_path.exists()

        # Verify XML content
        tree = ET.parse(output_path)
        root = tree.getroot()

        assert root.tag == "OpcUaAddressSpace"

        # Check metadata
        metadata = root.find("Metadata")
        assert metadata is not None
        assert metadata.find("TotalNodes").text == "3"
        assert metadata.find("FullExport").text == "False"

        # Check namespaces
        namespaces = root.find("Namespaces")
        assert namespaces is not None
        assert len(namespaces.findall("Namespace")) == 2

        # Check nodes
        nodes = root.find("Nodes")
        assert nodes is not None
        assert len(nodes.findall("Node")) == 3

        # Check first node
        first_node = nodes.find("Node")
        assert first_node.find("NodeId").text == "i=84"
        assert first_node.find("BrowseName").text == "Root"
        assert first_node.find("Description") is None  # Not in basic export

    @pytest.mark.asyncio
    async def test_export_full(self, tmp_path, full_export_result):
        """Test XML export with full_export=True."""
        strategy = XmlExportStrategy()
        output_path = tmp_path / "test_full.xml"

        await strategy.export(full_export_result, output_path, full_export=True)

        assert output_path.exists()

        # Verify extended attributes
        tree = ET.parse(output_path)
        root = tree.getroot()

        metadata = root.find("Metadata")
        assert metadata.find("FullExport").text == "True"

        nodes = root.find("Nodes")

        # Variable with extended attrs
        var_node = nodes.findall("Node")[0]
        assert var_node.find("Description").text == "Temperature sensor"
        assert var_node.find("AccessLevel").text == "CurrentRead"
        assert var_node.find("Historizing").text == "True"

        # Object with event notifier
        obj_node = nodes.findall("Node")[1]
        assert obj_node.find("EventNotifier").text == "1"

        # Method with executable flags
        method_node = nodes.findall("Node")[2]
        assert method_node.find("Executable").text == "True"
        assert method_node.find("UserExecutable").text == "False"

    @pytest.mark.asyncio
    async def test_export_with_error_message(self, tmp_path):
        """Test XML export includes error message if present."""
        result = BrowseResult()
        result.success = True
        result.error_message = "Warning: Some nodes inaccessible"
        result.namespaces = {0: "test"}

        node = OpcUaNode(
            node_id="i=1", browse_name="Test", display_name="Test", node_class="Object"
        )
        result.add_node(node)

        strategy = XmlExportStrategy()
        output_path = tmp_path / "test.xml"

        await strategy.export(result, output_path)

        tree = ET.parse(output_path)
        root = tree.getroot()
        metadata = root.find("Metadata")
        assert metadata.find("ErrorMessage").text == "Warning: Some nodes inaccessible"

    @pytest.mark.asyncio
    async def test_export_node_with_all_optional_fields(self, tmp_path):
        """Test XML export with node containing all optional fields."""
        result = BrowseResult()
        result.success = True
        result.namespaces = {0: "test"}

        node = OpcUaNode(
            node_id="ns=2;i=1000",
            browse_name="ComplexNode",
            display_name="Complex Node",
            node_class="Variable",
            data_type="Double",
            value=123.45,
            parent_id="i=85",
            depth=2,
            namespace_index=2,
            timestamp=datetime(2025, 1, 5, 10, 30, 0),
        )
        result.add_node(node)

        strategy = XmlExportStrategy()
        output_path = tmp_path / "test.xml"

        await strategy.export(result, output_path)

        tree = ET.parse(output_path)
        root = tree.getroot()
        nodes = root.find("Nodes")
        xml_node = nodes.find("Node")

        assert xml_node.find("DataType").text == "Double"
        assert xml_node.find("Value").text == "123.45"
        assert xml_node.find("ParentId").text == "i=85"
        assert xml_node.find("Depth").text == "2"
        assert xml_node.find("NamespaceIndex").text == "2"
        assert "2025-01-05" in xml_node.find("Timestamp").text

    @pytest.mark.asyncio
    async def test_export_os_error(self, tmp_path, sample_result):
        """Test XML export handles OSError."""
        from unittest.mock import patch

        strategy = XmlExportStrategy()
        output_path = tmp_path / "test.xml"

        # Mock the tree.write method to raise OSError
        with patch("xml.etree.ElementTree.ElementTree.write", side_effect=OSError("Disk full")):
            with pytest.raises(OSError) as exc_info:
                await strategy.export(sample_result, output_path)
            assert "Failed to write XML file" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_general_exception(self, tmp_path, sample_result):
        """Test XML export handles general exceptions."""
        from unittest.mock import patch

        strategy = XmlExportStrategy()
        output_path = tmp_path / "test.xml"

        # Mock SubElement to raise exception during node creation
        with (
            patch(
                "opc_browser.strategies.xml_strategy.SubElement",
                side_effect=RuntimeError("Unexpected"),
            ),
            pytest.raises(RuntimeError),
        ):
            await strategy.export(sample_result, output_path)

    @pytest.mark.asyncio
    async def test_export_node_without_optional_fields(self, tmp_path):
        """Test XML export with node missing all optional fields."""
        result = BrowseResult()
        result.success = True
        result.namespaces = {0: "test"}

        # Node with no optional fields
        node = OpcUaNode(
            node_id="i=1",
            browse_name="Test",
            display_name="Test",
            node_class="Object",
            depth=0,
            namespace_index=0,
        )
        result.add_node(node)

        strategy = XmlExportStrategy()
        output_path = tmp_path / "test.xml"

        await strategy.export(result, output_path)

        tree = ET.parse(output_path)
        root = tree.getroot()
        nodes = root.find("Nodes")
        xml_node = nodes.find("Node")

        # Optional fields should not be present
        assert xml_node.find("DataType") is None
        assert xml_node.find("Value") is None
        assert xml_node.find("ParentId") is None


# Integration tests for all strategies


class TestAllStrategies:
    """Integration tests for all export strategies."""

    @pytest.mark.asyncio
    async def test_all_strategies_produce_output(self, tmp_path, sample_result):
        """Test that all strategies successfully produce output files."""
        strategies = [
            (CsvExportStrategy(), "test.csv"),
            (JsonExportStrategy(), "test.json"),
            (XmlExportStrategy(), "test.xml"),
        ]

        for strategy, filename in strategies:
            output_path = tmp_path / filename
            await strategy.export(sample_result, output_path)
            assert output_path.exists()
            assert output_path.stat().st_size > 0

    @pytest.mark.asyncio
    async def test_all_strategies_handle_full_export(self, tmp_path, full_export_result):
        """Test that all strategies handle full_export correctly."""
        strategies = [
            (CsvExportStrategy(), "full.csv"),
            (JsonExportStrategy(), "full.json"),
            (XmlExportStrategy(), "full.xml"),
        ]

        for strategy, filename in strategies:
            output_path = tmp_path / filename
            await strategy.export(full_export_result, output_path, full_export=True)
            assert output_path.exists()

            # Verify extended attributes are present in output
            content = output_path.read_text(encoding="utf-8")
            assert "Temperature sensor" in content  # Description
            assert "CurrentRead" in content  # AccessLevel

    @pytest.mark.asyncio
    async def test_all_strategies_validate_before_export(self, tmp_path):
        """Test that all strategies validate input before export."""
        failed_result = BrowseResult()
        failed_result.success = False
        failed_result.error_message = "Test error"

        strategies = [
            CsvExportStrategy(),
            JsonExportStrategy(),
            XmlExportStrategy(),
        ]

        for strategy in strategies:
            output_path = tmp_path / f"test_{strategy.__class__.__name__}.txt"
            with pytest.raises(ValueError):
                await strategy.export(failed_result, output_path)


# Add new test class for missing coverage


class TestStrategyCoverage:
    """Additional tests to achieve 100% coverage for all strategies."""

    @pytest.mark.asyncio
    async def test_base_strategy_abstract_methods(self):
        """Test that ExportStrategy abstract methods cannot be called."""
        # Cannot instantiate abstract class directly
        with pytest.raises(TypeError):
            ExportStrategy()

    @pytest.mark.asyncio
    async def test_base_strategy_export_not_implemented(self):
        """Test that calling abstract export method raises NotImplementedError."""

        # Create a minimal concrete class that doesn't implement abstract methods properly
        class IncompleteStrategy(ExportStrategy):
            def get_file_extension(self) -> str:
                return "test"

        # This will fail because export is not implemented
        with pytest.raises(TypeError):
            IncompleteStrategy()

    @pytest.mark.asyncio
    async def test_csv_export_exception_in_write(self, tmp_path):
        """Test CSV export handles exception during row writing."""
        from unittest.mock import MagicMock, patch

        result = BrowseResult()
        result.success = True
        result.namespaces = {0: "test"}

        node = OpcUaNode(
            node_id="i=1", browse_name="Test", display_name="Test", node_class="Object"
        )
        result.add_node(node)

        strategy = CsvExportStrategy()
        output_path = tmp_path / "test.csv"

        # Mock csv.writer to raise exception during writerow
        mock_writer = MagicMock()
        mock_writer.writerow = MagicMock(side_effect=Exception("Write failed"))

        with patch("csv.writer", return_value=mock_writer):
            with pytest.raises(Exception) as exc_info:
                await strategy.export(result, output_path)
            assert "Write failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_json_export_progress_logging(self, tmp_path):
        """Test JSON export progress logging for large datasets."""
        result = BrowseResult()
        result.success = True
        result.namespaces = {0: "test"}

        # Add 150 nodes to trigger progress logging (logged every 100 nodes)
        for i in range(150):
            node = OpcUaNode(
                node_id=f"i={i}",
                browse_name=f"Node{i}",
                display_name=f"Node{i}",
                node_class="Object",
                depth=0,
                namespace_index=0,
            )
            result.add_node(node)

        strategy = JsonExportStrategy()
        output_path = tmp_path / "test.json"

        await strategy.export(result, output_path)

        assert output_path.exists()
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)
            assert len(data["nodes"]) == 150

    @pytest.mark.asyncio
    async def test_xml_export_progress_logging(self, tmp_path):
        """Test XML export progress logging for large datasets."""
        result = BrowseResult()
        result.success = True
        result.namespaces = {0: "test"}

        # Add 150 nodes to trigger progress logging
        for i in range(150):
            node = OpcUaNode(
                node_id=f"i={i}",
                browse_name=f"Node{i}",
                display_name=f"Node{i}",
                node_class="Object",
                depth=0,
                namespace_index=0,
            )
            result.add_node(node)

        strategy = XmlExportStrategy()
        output_path = tmp_path / "test.xml"

        await strategy.export(result, output_path)

        assert output_path.exists()
        tree = ET.parse(output_path)
        root = tree.getroot()
        nodes = root.find("Nodes")
        assert len(nodes.findall("Node")) == 150

    @pytest.mark.asyncio
    async def test_csv_export_progress_logging(self, tmp_path):
        """Test CSV export progress logging for large datasets."""
        result = BrowseResult()
        result.success = True
        result.namespaces = {0: "test"}

        # Add 150 nodes to trigger progress logging
        for i in range(150):
            node = OpcUaNode(
                node_id=f"i={i}",
                browse_name=f"Node{i}",
                display_name=f"Node{i}",
                node_class="Object",
                depth=0,
                namespace_index=0,
            )
            result.add_node(node)

        strategy = CsvExportStrategy()
        output_path = tmp_path / "test.csv"

        await strategy.export(result, output_path)

        assert output_path.exists()
        with open(output_path, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 151  # Header + 150 nodes

    @pytest.mark.asyncio
    async def test_xml_export_element_tree_write_exception(self, tmp_path):
        """Test XML export handles ElementTree.write exceptions."""
        from unittest.mock import patch

        result = BrowseResult()
        result.success = True
        result.namespaces = {0: "test"}

        node = OpcUaNode(
            node_id="i=1",
            browse_name="Test",
            display_name="Test",
            node_class="Object",
            depth=0,
            namespace_index=0,
        )
        result.add_node(node)

        strategy = XmlExportStrategy()
        output_path = tmp_path / "test.xml"

        # Mock ElementTree.write to raise a generic Exception (not OSError)
        with patch(
            "xml.etree.ElementTree.ElementTree.write",
            side_effect=Exception("Unexpected write error"),
        ):
            with pytest.raises(Exception) as exc_info:
                await strategy.export(result, output_path)
            # Should re-raise the exception (line 167 coverage)
            assert "Unexpected write error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_xml_add_node_element_exception(self, tmp_path):
        """Test XML export handles exception during node element creation."""
        from unittest.mock import patch

        result = BrowseResult()
        result.success = True
        result.namespaces = {0: "test"}

        node = OpcUaNode(
            node_id="i=1",
            browse_name="Test",
            display_name="Test",
            node_class="Object",
            depth=0,
            namespace_index=0,
            description="Test description",
        )
        result.add_node(node)

        strategy = XmlExportStrategy()
        output_path = tmp_path / "test.xml"

        # Mock SubElement to fail when creating the "Node" element specifically
        original_subelement = __import__(
            "xml.etree.ElementTree", fromlist=["SubElement"]
        ).SubElement

        def failing_subelement(parent, tag):
            # Fail specifically when trying to create a "Node" element inside "Nodes" parent
            if hasattr(parent, "tag") and parent.tag == "Nodes" and tag == "Node":
                raise RuntimeError("SubElement failed")
            return original_subelement(parent, tag)

        with patch(
            "opc_browser.strategies.xml_strategy.SubElement", side_effect=failing_subelement
        ):
            with pytest.raises(RuntimeError) as exc_info:
                await strategy.export(result, output_path)
            assert "SubElement failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_xml_export_full_with_all_extended_attributes(self, tmp_path):
        """Test XML export with full_export and all possible extended attributes."""
        result = BrowseResult()
        result.success = True
        result.namespaces = {0: "test"}

        # Create nodes with every possible extended attribute
        var_node = OpcUaNode(
            node_id="i=1",
            browse_name="Var",
            display_name="Variable",
            node_class="Variable",
            depth=0,
            namespace_index=0,
            description="Desc",
            access_level="Read",
            user_access_level="Read",
            write_mask=1,
            user_write_mask=2,
            minimum_sampling_interval=10.5,
            historizing=True,
        )
        result.add_node(var_node)

        obj_node = OpcUaNode(
            node_id="i=2",
            browse_name="Obj",
            display_name="Object",
            node_class="Object",
            depth=0,
            namespace_index=0,
            description="Obj Desc",
            event_notifier=5,
        )
        result.add_node(obj_node)

        method_node = OpcUaNode(
            node_id="i=3",
            browse_name="Method",
            display_name="Method",
            node_class="Method",
            depth=0,
            namespace_index=0,
            description="Method Desc",
            executable=True,
            user_executable=False,
        )
        result.add_node(method_node)

        strategy = XmlExportStrategy()
        output_path = tmp_path / "test.xml"

        await strategy.export(result, output_path, full_export=True)

        tree = ET.parse(output_path)
        root = tree.getroot()
        nodes = root.find("Nodes")

        # Verify all extended attributes are present
        var_xml = nodes.findall("Node")[0]
        assert var_xml.find("Description").text == "Desc"
        assert var_xml.find("AccessLevel").text == "Read"
        assert var_xml.find("UserAccessLevel").text == "Read"
        assert var_xml.find("WriteMask").text == "1"
        assert var_xml.find("UserWriteMask").text == "2"
        assert var_xml.find("MinimumSamplingInterval").text == "10.5"
        assert var_xml.find("Historizing").text == "True"

        obj_xml = nodes.findall("Node")[1]
        assert obj_xml.find("Description").text == "Obj Desc"
        assert obj_xml.find("EventNotifier").text == "5"

        method_xml = nodes.findall("Node")[2]
        assert method_xml.find("Description").text == "Method Desc"
        assert method_xml.find("Executable").text == "True"
        assert method_xml.find("UserExecutable").text == "False"
