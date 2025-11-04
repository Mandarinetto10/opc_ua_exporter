"""
Data models for OPC UA nodes.
Implements dataclass pattern following DRY principle.
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime
from asyncua import ua


@dataclass
class OpcUaNode:
    """
    Represents an OPC UA node with all its metadata.
    
    Attributes:
        node_id: Unique identifier of the node
        browse_name: QualifiedName used for browsing
        display_name: Human-readable name
        node_class: Class of the node (Object, Variable, Method, etc.)
        data_type: Data type for Variable nodes
        value: Current value (if include_values is True)
        parent_id: Node ID of the parent node
        depth: Depth level in the browsing hierarchy
        namespace_index: Namespace index of the node
        is_namespace_node: Flag indicating if this is a namespace-related node
        timestamp: Timestamp when the node was read
    """
    
    node_id: str
    browse_name: str
    display_name: str
    node_class: str
    data_type: Optional[str] = None
    value: Optional[Any] = None
    parent_id: Optional[str] = None
    depth: int = 0
    namespace_index: int = 0
    is_namespace_node: bool = False
    timestamp: Optional[datetime] = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        """String representation of the node (legacy, kept for compatibility)."""
        indent = "  " * self.depth
        value_str = f" = {self.value}" if self.value is not None else ""
        return f"{indent}[{self.node_class}] {self.display_name} ({self.node_id}){value_str}"
    
    def to_formatted_string(self) -> str:
        """
        Rich formatted string representation with icons and details.
        
        Returns:
            Formatted string with emoji icons and detailed information
        """
        indent = "│  " * self.depth
        connector = "└─ " if self.depth > 0 else ""
        
        # Icon mapping
        icons = {
            "Object": "📁",
            "Variable": "📊",
            "Method": "⚙️",
            "ObjectType": "📦",
            "VariableType": "📈",
            "DataType": "🔢",
            "ReferenceType": "🔗",
            "View": "👁️",
        }
        icon = icons.get(self.node_class, "📄")
        
        # Build formatted string
        parts = [f"{indent}{connector}{icon} {self.display_name}"]
        
        if self.display_name != self.browse_name:
            parts.append(f"({self.browse_name})")
        
        if self.data_type:
            parts.append(f"[{self.data_type}]")
        
        if self.value is not None:
            value_str = str(self.value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            parts.append(f"= {value_str}")
        
        if self.namespace_index > 0:
            parts.append(f"[ns={self.namespace_index}]")
        
        return " ".join(parts)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary for serialization with asyncua type handling."""
        # Handle asyncua specific types
        value_serialized = None
        if self.value is not None:
            if isinstance(self.value, (ua.DataValue, ua.Variant)):
                # Extract actual value from asyncua types
                value_serialized = str(self.value.Value if hasattr(self.value, 'Value') else self.value)
            elif isinstance(self.value, datetime):
                value_serialized = self.value.isoformat()
            else:
                value_serialized = str(self.value)
        
        return {
            "node_id": self.node_id,
            "browse_name": self.browse_name,
            "display_name": self.display_name,
            "node_class": self.node_class,
            "data_type": self.data_type,
            "value": value_serialized,
            "parent_id": self.parent_id,
            "depth": self.depth,
            "namespace_index": self.namespace_index,
            "is_namespace_node": self.is_namespace_node,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
    
    def to_csv_row(self) -> list[str]:
        """Convert node to CSV row with asyncua type handling."""
        # Handle asyncua specific types for CSV
        value_str = ""
        if self.value is not None:
            if isinstance(self.value, (ua.DataValue, ua.Variant)):
                value_str = str(self.value.Value if hasattr(self.value, 'Value') else self.value)
            else:
                value_str = str(self.value)
        
        return [
            self.node_id,
            self.browse_name,
            self.display_name,
            self.node_class,
            self.data_type or "",
            value_str,
            self.parent_id or "",
            str(self.depth),
            str(self.namespace_index),
            str(self.is_namespace_node),
            self.timestamp.isoformat() if self.timestamp else "",
        ]


@dataclass
class BrowseResult:
    """
    Container for browse operation results.
    
    Attributes:
        nodes: List of discovered nodes
        total_nodes: Total number of nodes discovered
        max_depth_reached: Maximum depth reached during browsing
        namespaces: Dictionary of namespace URIs
        success: Whether the browse operation was successful
        error_message: Error message if operation failed
    """
    
    nodes: list[OpcUaNode] = field(default_factory=list)
    total_nodes: int = 0
    max_depth_reached: int = 0
    namespaces: dict[int, str] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None
    
    def add_node(self, node: OpcUaNode) -> None:
        """Add a node to the result."""
        self.nodes.append(node)
        self.total_nodes += 1
        if node.depth > self.max_depth_reached:
            self.max_depth_reached = node.depth
    
    def get_namespace_nodes(self) -> list[OpcUaNode]:
        """Get only namespace-related nodes."""
        return [node for node in self.nodes if node.is_namespace_node]
    
    def get_nodes_by_class(self, node_class: str) -> list[OpcUaNode]:
        """Get nodes filtered by node class."""
        return [node for node in self.nodes if node.node_class == node_class]