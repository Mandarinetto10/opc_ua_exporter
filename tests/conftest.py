"""Shared pytest fixtures for OPC UA Browser tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from asyncua import ua
from asyncua.common.node import Node
from asyncua.ua import NodeClass, ObjectIds, VariantType


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock OPC UA client."""
    client = MagicMock()

    # Create a default mock node for get_node
    default_node = AsyncMock(spec=Node)
    default_node.nodeid = MagicMock()
    default_node.nodeid.to_string = MagicMock(return_value="i=84")
    default_node.nodeid.NamespaceIndex = 0
    default_node.nodeid.Identifier = 84

    browse_name = MagicMock(spec=ua.QualifiedName)
    browse_name.Name = "Root"
    default_node.read_browse_name = AsyncMock(return_value=browse_name)

    display_name = MagicMock(spec=ua.LocalizedText)
    display_name.Text = "Root"
    default_node.read_display_name = AsyncMock(return_value=display_name)

    default_node.read_node_class = AsyncMock(return_value=NodeClass.Object)
    default_node.get_children = AsyncMock(return_value=[])

    client.get_node = MagicMock(return_value=default_node)
    client.get_namespace_array = AsyncMock(
        return_value=["http://opcfoundation.org/UA/", "urn:test:server", "urn:custom:namespace"]
    )
    return client


@pytest.fixture
def mock_node() -> AsyncMock:
    """Create a mock OPC UA node."""
    node = AsyncMock(spec=Node)

    # Node ID
    node.nodeid = MagicMock()
    node.nodeid.to_string = MagicMock(return_value="i=84")
    node.nodeid.NamespaceIndex = 0
    node.nodeid.Identifier = 84

    # Browse name
    browse_name = MagicMock(spec=ua.QualifiedName)
    browse_name.Name = "Root"
    node.read_browse_name = AsyncMock(return_value=browse_name)

    # Display name
    display_name = MagicMock(spec=ua.LocalizedText)
    display_name.Text = "Root"
    node.read_display_name = AsyncMock(return_value=display_name)

    # Node class
    node.read_node_class = AsyncMock(return_value=NodeClass.Object)

    # Children
    node.get_children = AsyncMock(return_value=[])

    return node


@pytest.fixture
def mock_variable_node() -> AsyncMock:
    """Create a mock Variable node with data type and value."""
    node = AsyncMock(spec=Node)

    # Node ID
    node.nodeid = MagicMock()
    node.nodeid.to_string = MagicMock(return_value="ns=2;i=1000")
    node.nodeid.NamespaceIndex = 2
    node.nodeid.Identifier = 1000

    # Browse name
    browse_name = MagicMock(spec=ua.QualifiedName)
    browse_name.Name = "Temperature"
    node.read_browse_name = AsyncMock(return_value=browse_name)

    # Display name
    display_name = MagicMock(spec=ua.LocalizedText)
    display_name.Text = "Temperature Sensor"
    node.read_display_name = AsyncMock(return_value=display_name)

    # Node class
    node.read_node_class = AsyncMock(return_value=NodeClass.Variable)

    # Data type
    data_type_node = MagicMock(spec=ua.NodeId)
    data_type_node.to_string = MagicMock(return_value="i=11")  # Double
    node.read_data_type = AsyncMock(return_value=data_type_node)

    # Data value with variant type
    data_value = MagicMock(spec=ua.DataValue)
    variant = MagicMock()
    variant.VariantType = VariantType.Double
    data_value.Value = variant
    node.read_data_value = AsyncMock(return_value=data_value)

    # Value
    node.read_value = AsyncMock(return_value=23.5)

    # Children
    node.get_children = AsyncMock(return_value=[])

    return node


@pytest.fixture
def mock_namespace_node() -> AsyncMock:
    """Create a mock namespace-related node."""
    node = AsyncMock(spec=Node)

    # Node ID
    node.nodeid = MagicMock()
    node.nodeid.to_string = MagicMock(return_value=f"i={ObjectIds.Server_NamespaceArray}")
    node.nodeid.NamespaceIndex = 0
    node.nodeid.Identifier = ObjectIds.Server_NamespaceArray

    # Browse name
    browse_name = MagicMock(spec=ua.QualifiedName)
    browse_name.Name = "NamespaceArray"
    node.read_browse_name = AsyncMock(return_value=browse_name)

    # Display name
    display_name = MagicMock(spec=ua.LocalizedText)
    display_name.Text = "NamespaceArray"
    node.read_display_name = AsyncMock(return_value=display_name)

    # Node class
    node.read_node_class = AsyncMock(return_value=NodeClass.Variable)

    # Children
    node.get_children = AsyncMock(return_value=[])

    return node


@pytest.fixture
def mock_node_with_children(mock_node: AsyncMock, mock_variable_node: AsyncMock) -> AsyncMock:
    """Create a mock node with children."""
    child1 = AsyncMock(spec=Node)
    child1.nodeid = MagicMock()
    child1.nodeid.to_string = MagicMock(return_value="i=85")
    child1.nodeid.NamespaceIndex = 0
    child1.nodeid.Identifier = 85

    browse_name = MagicMock(spec=ua.QualifiedName)
    browse_name.Name = "Objects"
    child1.read_browse_name = AsyncMock(return_value=browse_name)

    display_name = MagicMock(spec=ua.LocalizedText)
    display_name.Text = "Objects"
    child1.read_display_name = AsyncMock(return_value=display_name)

    child1.read_node_class = AsyncMock(return_value=NodeClass.Object)
    child1.get_children = AsyncMock(return_value=[mock_variable_node])

    mock_node.get_children = AsyncMock(return_value=[child1])

    return mock_node


@pytest.fixture
def mock_ua_status_error() -> type[ua.UaStatusCodeError]:
    """Create a mock UaStatusCodeError class."""

    class MockUaStatusCodeError(Exception):
        def __init__(self, code: Any):
            self.code = code
            super().__init__(f"OPC UA Error: {code}")

    return MockUaStatusCodeError


@pytest.fixture
def sample_browse_result():
    """Create a sample BrowseResult for testing."""
    from opc_browser.models import BrowseResult, OpcUaNode

    result = BrowseResult()
    result.namespaces = {0: "http://opcfoundation.org/UA/", 1: "urn:test:server"}

    # Add root node
    root = OpcUaNode(
        node_id="i=84",
        browse_name="Root",
        display_name="Root",
        node_class="Object",
        depth=0,
        namespace_index=0,
        parent_id=None,
    )
    result.add_node(root)

    # Add Objects node
    objects = OpcUaNode(
        node_id="i=85",
        browse_name="Objects",
        display_name="Objects",
        node_class="Object",
        depth=1,
        namespace_index=0,
        parent_id="i=84",
    )
    result.add_node(objects)

    # Add Variable node
    var = OpcUaNode(
        node_id="ns=2;i=1000",
        browse_name="Temperature",
        display_name="Temperature Sensor",
        node_class="Variable",
        data_type="Double",
        value=23.5,
        depth=2,
        namespace_index=2,
        parent_id="i=85",
    )
    result.add_node(var)

    return result
