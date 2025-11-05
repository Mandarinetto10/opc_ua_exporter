"""Comprehensive tests for OPC UA models module."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

from asyncua import ua

from opc_browser.models import BrowseResult, OpcUaNode


class TestOpcUaNode:
    """Test OpcUaNode dataclass."""

    def test_init_minimal(self):
        """Test initialization with minimal required parameters."""
        node = OpcUaNode(
            node_id="i=84",
            browse_name="Root",
            display_name="Root",
            node_class="Object",
        )
        assert node.node_id == "i=84"
        assert node.browse_name == "Root"
        assert node.display_name == "Root"
        assert node.node_class == "Object"
        assert node.data_type is None
        assert node.value is None
        assert node.parent_id is None
        assert node.depth == 0
        assert node.namespace_index == 0
        assert node.is_namespace_node is False
        assert node.timestamp is not None
        assert node.full_path is None

    def test_init_full(self):
        """Test initialization with all parameters."""
        ts = datetime.now()
        node = OpcUaNode(
            node_id="ns=2;i=1000",
            browse_name="Temperature",
            display_name="Temperature Sensor",
            node_class="Variable",
            data_type="Double",
            value=23.5,
            parent_id="ns=2;i=999",
            depth=3,
            namespace_index=2,
            is_namespace_node=False,
            timestamp=ts,
            full_path="Root/Objects/Sensors/Temperature",
            description="Temperature sensor description",
            access_level="CurrentRead",
            user_access_level="CurrentRead",
            write_mask=123,
            user_write_mask=456,
            event_notifier=1,
            executable=True,
            user_executable=False,
            minimum_sampling_interval=100.0,
            historizing=True,
        )
        assert node.node_id == "ns=2;i=1000"
        assert node.value == 23.5
        assert node.depth == 3
        assert node.timestamp == ts
        assert node.full_path == "Root/Objects/Sensors/Temperature"
        assert node.description == "Temperature sensor description"
        assert node.access_level == "CurrentRead"
        assert node.historizing is True

    def test_str(self):
        """Test __str__ method."""
        node = OpcUaNode(
            node_id="i=85",
            browse_name="Objects",
            display_name="Objects",
            node_class="Object",
            depth=1,
        )
        s = str(node)
        assert "Objects" in s
        assert "i=85" in s
        assert "Object" in s

    def test_str_with_value(self):
        """Test __str__ method with value."""
        node = OpcUaNode(
            node_id="i=100",
            browse_name="Temp",
            display_name="Temp",
            node_class="Variable",
            value=42,
            depth=0,
        )
        s = str(node)
        assert "42" in s

    def test_to_formatted_string_basic(self):
        """Test to_formatted_string with basic node."""
        node = OpcUaNode(
            node_id="i=85",
            browse_name="Objects",
            display_name="Objects",
            node_class="Object",
            depth=1,
        )
        s = node.to_formatted_string()
        assert "📁" in s
        assert "Objects" in s

    def test_to_formatted_string_variable_with_value(self):
        """Test to_formatted_string for Variable with value."""
        node = OpcUaNode(
            node_id="ns=2;i=1000",
            browse_name="Temp",
            display_name="Temperature",
            node_class="Variable",
            data_type="Double",
            value=23.5,
            depth=2,
            namespace_index=2,
        )
        s = node.to_formatted_string()
        assert "📊" in s
        assert "Temperature" in s
        assert "(Temp)" in s
        assert "[Double]" in s
        assert "23.5" in s
        assert "[ns=2]" in s

    def test_to_formatted_string_long_value_truncation(self):
        """Test to_formatted_string with long value truncation."""
        long_value = "x" * 100
        node = OpcUaNode(
            node_id="i=1",
            browse_name="Data",
            display_name="Data",
            node_class="Variable",
            value=long_value,
            depth=0,
        )
        s = node.to_formatted_string()
        assert "..." in s
        assert len(s) < len(long_value) + 100

    def test_to_formatted_string_same_browse_display(self):
        """Test to_formatted_string when browse_name == display_name."""
        node = OpcUaNode(
            node_id="i=1",
            browse_name="Same",
            display_name="Same",
            node_class="Object",
            depth=0,
        )
        s = node.to_formatted_string()
        assert s.count("Same") == 1  # Should appear only once

    def test_get_csv_headers_basic(self):
        """Test get_csv_headers without full export."""
        headers = OpcUaNode.get_csv_headers(full_export=False)
        assert "NodeId" in headers
        assert "BrowseName" in headers
        assert "DisplayName" in headers
        assert "FullPath" in headers
        assert "NodeClass" in headers
        assert "DataType" in headers
        assert "Value" in headers
        assert "ParentId" in headers
        assert "Depth" in headers
        assert "NamespaceIndex" in headers
        assert "IsNamespaceNode" in headers
        assert "Timestamp" in headers
        assert "Description" not in headers

    def test_get_csv_headers_full_export(self):
        """Test get_csv_headers with full export."""
        headers = OpcUaNode.get_csv_headers(full_export=True)
        assert "Description" in headers
        assert "AccessLevel" in headers
        assert "UserAccessLevel" in headers
        assert "WriteMask" in headers
        assert "UserWriteMask" in headers
        assert "EventNotifier" in headers
        assert "Executable" in headers
        assert "UserExecutable" in headers
        assert "MinimumSamplingInterval" in headers
        assert "Historizing" in headers

    def test_to_csv_row_basic(self):
        """Test to_csv_row without full export."""
        node = OpcUaNode(
            node_id="i=85",
            browse_name="Objects",
            display_name="Objects",
            node_class="Object",
            depth=1,
            namespace_index=0,
            full_path="Root/Objects",
        )
        row = node.to_csv_row(full_export=False)
        assert row[0] == "i=85"
        assert row[1] == "Objects"
        assert row[2] == "Objects"
        assert row[3] == "Root/Objects"
        assert row[4] == "Object"
        assert row[8] == "1"
        assert len(row) == 12

    def test_to_csv_row_full_export(self):
        """Test to_csv_row with full export."""
        node = OpcUaNode(
            node_id="i=85",
            browse_name="Objects",
            display_name="Objects",
            node_class="Object",
            depth=1,
            description="Test description",
            access_level="CurrentRead",
            write_mask=123,
        )
        row = node.to_csv_row(full_export=True)
        assert len(row) > 12
        assert "Test description" in row
        assert "CurrentRead" in row
        assert "123" in row

    def test_to_csv_row_with_ua_datavalue(self):
        """Test to_csv_row with ua.DataValue."""
        mock_value = MagicMock(spec=ua.DataValue)
        mock_value.Value = 42
        node = OpcUaNode(
            node_id="i=1",
            browse_name="Test",
            display_name="Test",
            node_class="Variable",
            value=mock_value,
        )
        row = node.to_csv_row()
        assert "42" in row[6]

    def test_to_csv_row_with_ua_variant(self):
        """Test to_csv_row with ua.Variant."""
        mock_value = MagicMock(spec=ua.Variant)
        mock_value.Value = "test"
        node = OpcUaNode(
            node_id="i=1",
            browse_name="Test",
            display_name="Test",
            node_class="Variable",
            value=mock_value,
        )
        row = node.to_csv_row()
        assert "test" in row[6]

    def test_to_csv_row_empty_optional_fields(self):
        """Test to_csv_row with None optional fields."""
        node = OpcUaNode(
            node_id="i=1",
            browse_name="Test",
            display_name="Test",
            node_class="Object",
        )
        row = node.to_csv_row()
        assert row[5] == ""  # data_type
        assert row[6] == ""  # value
        assert row[7] == ""  # parent_id

    def test_to_dict_basic(self):
        """Test to_dict without full export."""
        node = OpcUaNode(
            node_id="i=85",
            browse_name="Objects",
            display_name="Objects",
            node_class="Object",
            depth=1,
            namespace_index=0,
            full_path="Root/Objects",
        )
        d = node.to_dict(full_export=False)
        assert d["node_id"] == "i=85"
        assert d["browse_name"] == "Objects"
        assert d["display_name"] == "Objects"
        assert d["full_path"] == "Root/Objects"
        assert d["node_class"] == "Object"
        assert d["depth"] == 1
        assert "description" not in d

    def test_to_dict_full_export(self):
        """Test to_dict with full export."""
        node = OpcUaNode(
            node_id="i=85",
            browse_name="Objects",
            display_name="Objects",
            node_class="Object",
            description="Test",
            access_level="CurrentRead",
            historizing=True,
        )
        d = node.to_dict(full_export=True)
        assert d["description"] == "Test"
        assert d["access_level"] == "CurrentRead"
        assert d["historizing"] is True

    def test_to_dict_with_ua_datavalue(self):
        """Test to_dict with ua.DataValue."""
        mock_value = MagicMock(spec=ua.DataValue)
        mock_value.Value = 42
        node = OpcUaNode(
            node_id="i=1",
            browse_name="Test",
            display_name="Test",
            node_class="Variable",
            value=mock_value,
        )
        d = node.to_dict()
        assert d["value"] == "42"

    def test_to_csv_row_with_datetime_value(self):
        """Test to_csv_row with datetime value (covers line 244)."""
        from datetime import datetime

        dt = datetime(2025, 1, 5, 10, 30, 45)
        node = OpcUaNode(
            node_id="i=1",
            browse_name="Test",
            display_name="Test",
            node_class="Variable",
            value=dt,
        )
        row = node.to_csv_row()
        assert "2025-01-05" in row[6]  # value field should contain ISO format

    def test_to_dict_with_datetime_timestamp(self):
        """Test to_dict with datetime in value field (covers line 296)."""
        from datetime import datetime

        dt = datetime(2025, 1, 5, 10, 30, 45)
        node = OpcUaNode(
            node_id="i=1",
            browse_name="Test",
            display_name="Test",
            node_class="Variable",
            value=dt,
        )
        d = node.to_dict()
        # The value should be serialized as ISO string
        assert "2025-01-05" in d["value"]
        assert "10:30:45" in d["value"]

    def test_to_dict_with_datetime_value(self):
        """Test to_dict with datetime value."""
        dt = datetime.now()
        node = OpcUaNode(
            node_id="i=1",
            browse_name="Test",
            display_name="Test",
            node_class="Variable",
            value=dt,
        )
        d = node.to_dict()
        assert dt.isoformat() in d["value"]

    def test_to_dict_timestamp_serialization(self):
        """Test to_dict timestamp serialization."""
        ts = datetime.now()
        node = OpcUaNode(
            node_id="i=1",
            browse_name="Test",
            display_name="Test",
            node_class="Object",
            timestamp=ts,
        )
        d = node.to_dict()
        assert d["timestamp"] == ts.isoformat()

    def test_to_dict_with_non_datetime_value(self):
        """Test to_dict with a non-datetime, non-ua value."""
        node = OpcUaNode(
            node_id="i=1",
            browse_name="Test",
            display_name="Test",
            node_class="Variable",
            value=123.45,
        )
        d = node.to_dict()
        assert d["value"] == "123.45"


class TestBrowseResult:
    """Test BrowseResult dataclass."""

    def test_init_default(self):
        """Test initialization with defaults."""
        result = BrowseResult()
        assert result.nodes == []
        assert result.total_nodes == 0
        assert result.max_depth_reached == 0
        assert result.namespaces == {}
        assert result.success is True
        assert result.error_message is None

    def test_add_node(self):
        """Test add_node method."""
        result = BrowseResult()
        node1 = OpcUaNode(
            node_id="i=84",
            browse_name="Root",
            display_name="Root",
            node_class="Object",
            depth=0,
        )
        node2 = OpcUaNode(
            node_id="i=85",
            browse_name="Objects",
            display_name="Objects",
            node_class="Object",
            depth=1,
        )
        result.add_node(node1)
        assert result.total_nodes == 1
        assert result.max_depth_reached == 0

        result.add_node(node2)
        assert result.total_nodes == 2
        assert result.max_depth_reached == 1

    def test_add_node_updates_max_depth(self):
        """Test that add_node updates max_depth_reached."""
        result = BrowseResult()
        for depth in [0, 2, 1, 5, 3]:
            node = OpcUaNode(
                node_id=f"i={depth}",
                browse_name=f"Node{depth}",
                display_name=f"Node{depth}",
                node_class="Object",
                depth=depth,
            )
            result.add_node(node)
        assert result.max_depth_reached == 5

    def test_compute_full_paths_single_node(self):
        """Test compute_full_paths with single root node."""
        result = BrowseResult()
        node = OpcUaNode(
            node_id="i=84",
            browse_name="Root",
            display_name="Root",
            node_class="Object",
            depth=0,
        )
        result.add_node(node)
        result.compute_full_paths()
        assert node.full_path == "Root"

    def test_compute_full_paths_hierarchy(self):
        """Test compute_full_paths with hierarchical nodes."""
        result = BrowseResult()
        root = OpcUaNode(
            node_id="i=84",
            browse_name="Root",
            display_name="Root",
            node_class="Object",
            depth=0,
        )
        child1 = OpcUaNode(
            node_id="i=85",
            browse_name="Objects",
            display_name="Objects",
            node_class="Object",
            parent_id="i=84",
            depth=1,
        )
        child2 = OpcUaNode(
            node_id="i=86",
            browse_name="Server",
            display_name="Server",
            node_class="Object",
            parent_id="i=85",
            depth=2,
        )
        result.add_node(root)
        result.add_node(child1)
        result.add_node(child2)
        result.compute_full_paths()
        assert root.full_path == "Root"
        assert child1.full_path == "Root/Objects"
        assert child2.full_path == "Root/Objects/Server"

    def test_compute_full_paths_uses_display_name(self):
        """Test that compute_full_paths uses display_name."""
        result = BrowseResult()
        node = OpcUaNode(
            node_id="i=1",
            browse_name="BrowseName",
            display_name="DisplayName",
            node_class="Object",
            depth=0,
        )
        result.add_node(node)
        result.compute_full_paths()
        assert "DisplayName" in node.full_path

    def test_compute_full_paths_fallback_to_browse_name(self):
        """Test that compute_full_paths falls back to browse_name if display_name is None."""
        result = BrowseResult()
        node = OpcUaNode(
            node_id="i=1",
            browse_name="BrowseName",
            display_name="",
            node_class="Object",
            depth=0,
        )
        result.add_node(node)
        result.compute_full_paths()
        assert "BrowseName" in node.full_path

    def test_compute_full_paths_skips_already_computed(self):
        """Test that compute_full_paths skips nodes with full_path already set."""
        result = BrowseResult()
        node = OpcUaNode(
            node_id="i=1",
            browse_name="Test",
            display_name="Test",
            node_class="Object",
            full_path="PrecomputedPath",
        )
        result.add_node(node)
        result.compute_full_paths()
        assert node.full_path == "PrecomputedPath"

    def test_compute_full_paths_orphan_node(self):
        """Test compute_full_paths with orphan node (parent not in result)."""
        result = BrowseResult()
        node = OpcUaNode(
            node_id="i=100",
            browse_name="Orphan",
            display_name="Orphan",
            node_class="Object",
            parent_id="i=999",  # Parent not in result
            depth=1,
        )
        result.add_node(node)
        result.compute_full_paths()
        assert node.full_path == "Orphan"

    def test_get_namespace_nodes(self):
        """Test get_namespace_nodes filter."""
        result = BrowseResult()
        ns_node = OpcUaNode(
            node_id="i=2253",
            browse_name="Namespaces",
            display_name="Namespaces",
            node_class="Object",
            is_namespace_node=True,
        )
        regular_node = OpcUaNode(
            node_id="i=85",
            browse_name="Objects",
            display_name="Objects",
            node_class="Object",
            is_namespace_node=False,
        )
        result.add_node(ns_node)
        result.add_node(regular_node)
        ns_nodes = result.get_namespace_nodes()
        assert len(ns_nodes) == 1
        assert ns_nodes[0].node_id == "i=2253"

    def test_get_nodes_by_class(self):
        """Test get_nodes_by_class filter."""
        result = BrowseResult()
        obj_node = OpcUaNode(
            node_id="i=85",
            browse_name="Objects",
            display_name="Objects",
            node_class="Object",
        )
        var_node = OpcUaNode(
            node_id="i=100",
            browse_name="Temp",
            display_name="Temp",
            node_class="Variable",
        )
        method_node = OpcUaNode(
            node_id="i=200",
            browse_name="Execute",
            display_name="Execute",
            node_class="Method",
        )
        result.add_node(obj_node)
        result.add_node(var_node)
        result.add_node(method_node)

        objects = result.get_nodes_by_class("Object")
        assert len(objects) == 1
        assert objects[0].node_id == "i=85"

        variables = result.get_nodes_by_class("Variable")
        assert len(variables) == 1
        assert variables[0].node_id == "i=100"

        methods = result.get_nodes_by_class("Method")
        assert len(methods) == 1
        assert methods[0].node_id == "i=200"

    def test_error_state(self):
        """Test BrowseResult in error state."""
        result = BrowseResult()
        result.success = False
        result.error_message = "Connection failed"
        assert result.success is False
        assert result.error_message == "Connection failed"
        assert result.total_nodes == 0
