"""Data models for OPC UA nodes and browse results.

This module implements the dataclass pattern following DRY principle for
representing OPC UA address space nodes and browse operation results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from asyncua import ua
from loguru import logger


@dataclass
class OpcUaNode:
    """Represents an OPC UA node with complete metadata.

    This class encapsulates all information about an OPC UA node including
    identification, classification, value, hierarchy position, and timestamp.
    Provides multiple serialization methods for export to different formats.

    Attributes:
        node_id: Unique identifier of the node (e.g., 'i=84', 'ns=2;s=MyNode').
        browse_name: QualifiedName used for browsing the address space.
        display_name: Human-readable name shown in user interfaces.
        node_class: Class of the node (Object, Variable, Method, ObjectType, etc.).
        data_type: Data type for Variable nodes (Int32, String, etc.), None for others.
        value: Current value if include_values is enabled, None otherwise.
        parent_id: Node ID of the parent node in the hierarchy.
        depth: Depth level in the browsing hierarchy (0 for root).
        namespace_index: Namespace index of the node (0 for OPC UA base namespace).
        is_namespace_node: True if this node represents namespace metadata.
        timestamp: Timestamp when the node data was captured.
    """

    node_id: str
    browse_name: str
    display_name: str
    node_class: str
    data_type: str | None = None
    value: Any | None = None
    parent_id: str | None = None
    depth: int = 0
    namespace_index: int = 0
    is_namespace_node: bool = False
    timestamp: datetime | None = field(default_factory=datetime.now)
    full_path: str | None = None  # NEW: OPC UA hierarchical path

    def __str__(self) -> str:
        """Return simple string representation with indentation.

        Returns:
            Indented string showing node class, display name, ID, and optional value.

        Note:
            This method is kept for backward compatibility. Use to_formatted_string()
            for richer output with icons and colors.
        """
        indent: str = "  " * self.depth
        value_str: str = f" = {self.value}" if self.value is not None else ""
        return f"{indent}[{self.node_class}] {self.display_name} ({self.node_id}){value_str}"

    def to_formatted_string(self) -> str:
        """Return rich formatted string with emoji icons and detailed information.

        Provides a tree-like representation with:
        - Visual hierarchy using box-drawing characters
        - Emoji icons representing node types
        - Display name and browse name (if different)
        - Data type for variables
        - Current value (truncated if too long)
        - Namespace index (if non-zero)

        Returns:
            Formatted string suitable for console tree visualization.

        Examples:
            >>> node = OpcUaNode(
            ...     node_id="ns=2;i=1001",
            ...     browse_name="Temperature",
            ...     display_name="Temperature Sensor",
            ...     node_class="Variable",
            ...     data_type="Double",
            ...     value=23.5,
            ...     depth=2,
            ...     namespace_index=2
            ... )
            >>> print(node.to_formatted_string())
            │  │  └─ 📊 Temperature Sensor (Temperature) [Double] = 23.5 [ns=2]
        """
        indent: str = "│  " * self.depth
        connector: str = "└─ " if self.depth > 0 else ""

        # Map node classes to emoji icons for visual identification
        icons: dict[str, str] = {
            "Object": "📁",
            "Variable": "📊",
            "Method": "⚙️",
            "ObjectType": "📦",
            "VariableType": "📈",
            "DataType": "🔢",
            "ReferenceType": "🔗",
            "View": "👁️",
        }
        icon: str = icons.get(self.node_class, "📄")

        parts: list[str] = [f"{indent}{connector}{icon} {self.display_name}"]

        if self.display_name != self.browse_name:
            parts.append(f"({self.browse_name})")

        if self.data_type:
            parts.append(f"[{self.data_type}]")

        if self.value is not None:
            value_str: str = str(self.value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            parts.append(f"= {value_str}")

        if self.namespace_index > 0:
            parts.append(f"[ns={self.namespace_index}]")

        return " ".join(parts)

    @staticmethod
    def get_csv_headers() -> list[str]:
        """Return CSV column headers for OpcUaNode export.

        Returns:
            List of header names matching the order of to_csv_row().

        Examples:
            >>> OpcUaNode.get_csv_headers()
            [
                'NodeId',
                'BrowseName',
                'DisplayName',
                'FullPath',
                'NodeClass',
                'DataType',
                'Value',
                'ParentId',
                'Depth',
                'NamespaceIndex',
                'IsNamespaceNode',
                'Timestamp'
            ]
        """
        return [
            "NodeId",
            "BrowseName",
            "DisplayName",
            "FullPath",  # NEW
            "NodeClass",
            "DataType",
            "Value",
            "ParentId",
            "Depth",
            "NamespaceIndex",
            "IsNamespaceNode",
            "Timestamp",
        ]

    def to_csv_row(self) -> list[str]:
        """Convert node to CSV row with string values for all fields.

        Handles asyncua-specific types by extracting the actual value.
        All fields are converted to strings suitable for CSV export.

        Returns:
            List of string values representing a CSV row.

        Examples:
            >>> node.to_csv_row()
            [
                'ns=2;i=1001',
                'Temperature',
                'Temperature Sensor',
                'FullPath',  # NEW
                'Variable',
                'Double',
                '23.5',
                'ns=2;i=1000',
                '2',
                '2',
                'False',
                '2025-01-04T14:30:22.123456'
            ]
        """
        value_str: str = ""
        if self.value is not None:
            if isinstance(self.value, (ua.DataValue, ua.Variant)):
                value_str = str(
                    self.value.Value if hasattr(self.value, "Value") else self.value
                )
            else:
                value_str = str(self.value)

        return [
            self.node_id,
            self.browse_name,
            self.display_name,
            self.full_path or "",  # NEW
            self.node_class,
            self.data_type or "",
            value_str,
            self.parent_id or "",
            str(self.depth),
            str(self.namespace_index),
            str(self.is_namespace_node),
            self.timestamp.isoformat() if self.timestamp else "",
        ]

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary for JSON/XML serialization.

        Handles asyncua-specific types (DataValue, Variant) by extracting
        the actual value. Converts datetime objects to ISO format strings.

        Returns:
            Dictionary with all node attributes, suitable for JSON serialization.

        Examples:
            >>> node.to_dict()
            {
                'node_id': 'ns=2;i=1001',
                'browse_name': 'Temperature',
                'display_name': 'Temperature Sensor',
                'node_class': 'Variable',
                'data_type': 'Double',
                'value': '23.5',
                'parent_id': 'ns=2;i=1000',
                'depth': 2,
                'namespace_index': 2,
                'is_namespace_node': False,
                'timestamp': '2025-01-04T14:30:22.123456'
            }
        """
        value_serialized: str | None = None
        if self.value is not None:
            if isinstance(self.value, (ua.DataValue, ua.Variant)):
                # Extract value from asyncua wrapper types
                value_serialized = str(
                    self.value.Value if hasattr(self.value, "Value") else self.value
                )
            elif isinstance(self.value, datetime):
                value_serialized = self.value.isoformat()
            else:
                value_serialized = str(self.value)

        return {
            "node_id": self.node_id,
            "browse_name": self.browse_name,
            "display_name": self.display_name,
            "full_path": self.full_path,  # NEW
            "node_class": self.node_class,
            "data_type": self.data_type,
            "value": value_serialized,
            "parent_id": self.parent_id,
            "depth": self.depth,
            "namespace_index": self.namespace_index,
            "is_namespace_node": self.is_namespace_node,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


@dataclass
class BrowseResult:
    """Container for OPC UA browse operation results and metadata.

    Stores all nodes discovered during a browse operation along with
    statistics, namespace information, and success/error status.

    Attributes:
        nodes: List of all discovered OPC UA nodes.
        total_nodes: Total count of nodes discovered.
        max_depth_reached: Maximum hierarchy depth reached during browsing.
        namespaces: Dictionary mapping namespace indices to their URIs.
        success: True if browse operation completed successfully.
        error_message: Error description if operation failed, None otherwise.
    """

    nodes: list[OpcUaNode] = field(default_factory=list)
    total_nodes: int = 0
    max_depth_reached: int = 0
    namespaces: dict[int, str] = field(default_factory=dict)
    success: bool = True
    error_message: str | None = None

    def add_node(self, node: OpcUaNode) -> None:
        """Add a node to the result and update statistics.

        Automatically increments total_nodes counter and updates
        max_depth_reached if the new node is deeper than previous ones.

        Args:
            node: OPC UA node to add to the result set.

        Examples:
            >>> result = BrowseResult()
            >>> node = OpcUaNode(node_id="i=85", browse_name="Objects",
            ...                  display_name="Objects", node_class="Object", depth=1)
            >>> result.add_node(node)
            >>> result.total_nodes
            1
            >>> result.max_depth_reached
            1
        """
        self.nodes.append(node)
        self.total_nodes += 1
        if node.depth > self.max_depth_reached:
            self.max_depth_reached = node.depth

    def compute_full_paths(self) -> None:
        """Compute full OPC UA paths for all nodes.

        Builds hierarchical paths like:
        - Root
        - Root/Objects
        - Root/Objects/Server
        - Root/Objects/Server/ServerStatus

        This method should be called after all nodes are added.
        Uses a dictionary for O(1) lookup performance.

        Examples:
            >>> result = BrowseResult()
            >>> # ... add nodes ...
            >>> result.compute_full_paths()
            >>> result.nodes[0].full_path
            'Root/Objects/Server/ServerStatus'
        """
        # Build node lookup dictionary for fast parent resolution
        node_dict: dict[str, OpcUaNode] = {node.node_id: node for node in self.nodes}

        logger.debug(f"Computing full paths for {len(self.nodes)} nodes")

        for node in self.nodes:
            if node.full_path:
                continue  # Already computed

            # Build path by walking up the hierarchy
            path_parts: list[str] = []
            current_node: OpcUaNode | None = node

            while current_node:
                # Use display_name for readability, fallback to browse_name
                name = current_node.display_name or current_node.browse_name
                path_parts.insert(0, name)

                # Move to parent
                if current_node.parent_id and current_node.parent_id in node_dict:
                    current_node = node_dict[current_node.parent_id]
                else:
                    current_node = None

            # Join path with forward slash (OPC UA convention)
            node.full_path = "/".join(path_parts)

        logger.debug("Full paths computation completed")

    def get_namespace_nodes(self) -> list[OpcUaNode]:
        """Filter and return only namespace-related nodes.

        Returns:
            List of nodes that represent namespace metadata.

        Examples:
            >>> result.get_namespace_nodes()
            [OpcUaNode(node_id='i=2253', is_namespace_node=True, ...)]
        """
        return [node for node in self.nodes if node.is_namespace_node]

    def get_nodes_by_class(self, node_class: str) -> list[OpcUaNode]:
        """Filter nodes by their node class type.

        Args:
            node_class: Node class to filter by (e.g., 'Variable', 'Object', 'Method').

        Returns:
            List of nodes matching the specified node class.

        Examples:
            >>> result.get_nodes_by_class('Variable')
            [OpcUaNode(node_class='Variable', ...), ...]

            >>> result.get_nodes_by_class('Method')
            [OpcUaNode(node_class='Method', ...), ...]
        """
        return [node for node in self.nodes if node.node_class == node_class]
