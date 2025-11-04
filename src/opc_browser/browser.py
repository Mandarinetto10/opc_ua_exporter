"""
OPC UA Address Space browser with recursive navigation.

This module provides functionality to recursively browse and explore OPC UA
address spaces, extracting node information at configurable depths with
support for value reading and namespace filtering.
"""

from typing import Optional
from asyncua import Client, ua
from asyncua.ua import NodeClass, ObjectIds, VariantType
from asyncua.common.node import Node
from loguru import logger

from .models import OpcUaNode, BrowseResult


class OpcUaBrowser:
    """
    Handles recursive browsing of OPC UA Address Space.
    
    This class implements a depth-limited recursive algorithm to discover
    and catalog all nodes in an OPC UA server's address space. It uses
    asyncua's native methods for optimal performance and type safety.
    
    Features:
    - Configurable depth limiting to control browse scope
    - Optional value reading for Variable nodes
    - Namespace-based filtering
    - Progress logging for large address spaces
    - Type-safe data extraction using asyncua enums
    
    Attributes:
        client: Connected asyncua Client instance
        max_depth: Maximum recursion depth for browsing
        include_values: Whether to read current values from Variable nodes
        namespaces_only: Filter to show only namespace-related nodes
        
    Example:
        >>> async with OpcUaClient("opc.tcp://localhost:4840") as client:
        ...     browser = OpcUaBrowser(client.get_client(), max_depth=5)
        ...     result = await browser.browse()
        ...     browser.print_tree(result)
    """
    
    # Map asyncua NodeClass enum to friendly names
    NODE_CLASS_NAMES = {
        NodeClass.Object: "Object",
        NodeClass.Variable: "Variable",
        NodeClass.Method: "Method",
        NodeClass.ObjectType: "ObjectType",
        NodeClass.VariableType: "VariableType",
        NodeClass.ReferenceType: "ReferenceType",
        NodeClass.DataType: "DataType",
        NodeClass.View: "View",
    }
    
    # Map asyncua VariantType to readable names
    DATA_TYPE_NAMES = {
        VariantType.Boolean: "Boolean",
        VariantType.SByte: "SByte",
        VariantType.Byte: "Byte",
        VariantType.Int16: "Int16",
        VariantType.UInt16: "UInt16",
        VariantType.Int32: "Int32",
        VariantType.UInt32: "UInt32",
        VariantType.Int64: "Int64",
        VariantType.UInt64: "UInt64",
        VariantType.Float: "Float",
        VariantType.Double: "Double",
        VariantType.String: "String",
        VariantType.DateTime: "DateTime",
        VariantType.Guid: "Guid",
        VariantType.ByteString: "ByteString",
        VariantType.XmlElement: "XmlElement",
        VariantType.NodeId: "NodeId",
        VariantType.ExpandedNodeId: "ExpandedNodeId",
        VariantType.StatusCode: "StatusCode",
        VariantType.QualifiedName: "QualifiedName",
        VariantType.LocalizedText: "LocalizedText",
    }
    
    def __init__(
        self,
        client: Client,
        max_depth: int = 3,
        include_values: bool = False,
        namespaces_only: bool = False,
    ) -> None:
        """
        Initialize browser.
        
        Args:
            client: Connected OPC UA client
            max_depth: Maximum depth for recursive browsing
            include_values: Whether to read variable values
            namespaces_only: Whether to filter only namespace-related nodes
        """
        self.client = client
        self.max_depth = max_depth
        self.include_values = include_values
        self.namespaces_only = namespaces_only
        
        logger.info(
            f"Browser initialized (max_depth={max_depth}, "
            f"include_values={include_values}, namespaces_only={namespaces_only})"
        )
    
    async def browse(self, start_node_id: str = "i=84") -> BrowseResult:
        """
        Browse the Address Space starting from a specific node.
        
        Args:
            start_node_id: Node ID to start browsing from (default: RootFolder i=84)
            
        Returns:
            BrowseResult containing all discovered nodes
        """
        result = BrowseResult()
        
        try:
            logger.info(f"Starting browse from node: {start_node_id}")
            
            # Validate Node ID format
            if not self._validate_node_id(start_node_id):
                error_msg = f"Invalid Node ID format: {start_node_id}. Expected format: 'i=123', 'ns=2;i=456', or 'ns=2;s=StringId'"
                logger.error(error_msg)
                result.success = False
                result.error_message = error_msg
                return result
            
            # Get namespaces
            result.namespaces = await self._get_namespaces()
            logger.info(f"Found {len(result.namespaces)} namespaces")
            
            # Get starting node using asyncua native method
            try:
                start_node = self.client.get_node(start_node_id)
                # Verify node exists by trying to read its class
                await start_node.read_node_class()
            except ua.UaStatusCodeError as e:
                # Safely extract error code
                try:
                    error_code = e.code.name if hasattr(e.code, 'name') else f"Status code: {e.code}"
                except Exception:
                    error_code = "Unknown error"
                    
                error_msg = f"Node '{start_node_id}' not found or not accessible: {error_code}"
                logger.error(error_msg)
                result.success = False
                result.error_message = error_msg
                return result
            except Exception as e:
                error_msg = f"Node '{start_node_id}' error: {type(e).__name__}: {str(e)}"
                logger.error(error_msg)
                result.success = False
                result.error_message = error_msg
                return result
            
            # Start recursive browse
            await self._browse_recursive(
                node=start_node,
                parent_id=None,
                depth=0,
                result=result,
            )
            
            # Warning if no nodes found
            if result.total_nodes == 0:
                logger.warning(f"No nodes discovered from '{start_node_id}'. The node may have no children or access is restricted.")
            
            logger.success(
                f"Browse completed: {result.total_nodes} nodes discovered "
                f"(max depth: {result.max_depth_reached})"
            )
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Browse failed: {error_msg}")
            result.success = False
            result.error_message = error_msg
        
        return result
    
    async def _browse_recursive(
        self,
        node: Node,
        parent_id: Optional[str],
        depth: int,
        result: BrowseResult,
    ) -> None:
        """
        Recursively browse nodes up to max_depth.
        
        Args:
            node: Current node to browse
            parent_id: Parent node ID
            depth: Current depth level
            result: BrowseResult to accumulate nodes
        """
        # Check depth limit
        if depth > self.max_depth:
            return
        
        try:
            # Get node information using asyncua native methods
            node_id = node.nodeid.to_string()
            browse_name_obj = await node.read_browse_name()
            browse_name = browse_name_obj.Name
            display_name_obj = await node.read_display_name()
            display_name = display_name_obj.Text
            node_class = await node.read_node_class()
            
            # Get namespace index from NodeId object
            namespace_index = node.nodeid.NamespaceIndex
            
            # Check if this is a namespace-related node
            is_namespace_node = await self._is_namespace_node(node, browse_name)
            
            # Skip if namespaces_only filter is active and node is not namespace-related
            if self.namespaces_only and not is_namespace_node:
                return
            
            # Get data type and value for Variable nodes
            data_type = None
            value = None
            data_type_name = None
            
            if node_class == NodeClass.Variable:
                try:
                    # Get data type using asyncua native method
                    data_type_node = await node.read_data_type()
                    data_type = data_type_node.to_string()
                    
                    # Try to get variant type for better type name
                    try:
                        variant = await node.read_data_value()
                        if variant.Value and hasattr(variant.Value, 'VariantType'):
                            variant_type = variant.Value.VariantType
                            data_type_name = self.DATA_TYPE_NAMES.get(
                                variant_type,
                                self._parse_data_type_id(data_type)
                            )
                        else:
                            data_type_name = self._parse_data_type_id(data_type)
                    except:
                        data_type_name = self._parse_data_type_id(data_type)
                    
                    # Read value if requested
                    if self.include_values:
                        value_variant = await node.read_value()
                        value = value_variant
                        
                except Exception as e:
                    logger.debug(f"Could not read variable data for {node_id}: {e}")
            
            # Create OpcUaNode object with friendly node class name
            opc_node = OpcUaNode(
                node_id=node_id,
                browse_name=browse_name,
                display_name=display_name,
                node_class=self.NODE_CLASS_NAMES.get(node_class, str(node_class)),
                data_type=data_type_name or data_type,
                value=value,
                parent_id=parent_id,
                depth=depth,
                namespace_index=namespace_index,
                is_namespace_node=is_namespace_node,
            )
            
            # Add to result
            result.add_node(opc_node)
            
            # Log progress every 10 nodes at depth 0
            if depth == 0 and result.total_nodes % 10 == 0:
                logger.info(f"Discovered {result.total_nodes} nodes so far...")
            
            # Browse children if not at max depth
            if depth < self.max_depth:
                try:
                    children = await node.get_children()
                    
                    for child in children:
                        await self._browse_recursive(
                            node=child,
                            parent_id=node_id,
                            depth=depth + 1,
                            result=result,
                        )
                        
                except Exception as e:
                    logger.debug(f"Could not get children for {node_id}: {e}")
                    
        except Exception as e:
            logger.debug(f"Error browsing node at depth {depth}: {e}")
    
    def _parse_data_type_id(self, data_type: str) -> str:
        """
        Parse data type ID to human-readable name using asyncua constants.
        
        Args:
            data_type: Data type node ID string
            
        Returns:
            Human-readable data type name
        """
        # Map common OPC UA data type IDs to names
        # Using asyncua ObjectIds where possible
        type_map = {
            f"i={ua.ObjectIds.Boolean}": "Boolean",
            f"i={ua.ObjectIds.SByte}": "SByte",
            f"i={ua.ObjectIds.Byte}": "Byte",
            f"i={ua.ObjectIds.Int16}": "Int16",
            f"i={ua.ObjectIds.UInt16}": "UInt16",
            f"i={ua.ObjectIds.Int32}": "Int32",
            f"i={ua.ObjectIds.UInt32}": "UInt32",
            f"i={ua.ObjectIds.Int64}": "Int64",
            f"i={ua.ObjectIds.UInt64}": "UInt64",
            f"i={ua.ObjectIds.Float}": "Float",
            f"i={ua.ObjectIds.Double}": "Double",
            f"i={ua.ObjectIds.String}": "String",
            f"i={ua.ObjectIds.DateTime}": "DateTime",
            f"i={ua.ObjectIds.Guid}": "Guid",
            f"i={ua.ObjectIds.ByteString}": "ByteString",
            f"i={ua.ObjectIds.XmlElement}": "XmlElement",
            f"i={ua.ObjectIds.NodeId}": "NodeId",
            f"i={ua.ObjectIds.ExpandedNodeId}": "ExpandedNodeId",
            f"i={ua.ObjectIds.StatusCode}": "StatusCode",
            f"i={ua.ObjectIds.QualifiedName}": "QualifiedName",
            f"i={ua.ObjectIds.LocalizedText}": "LocalizedText",
        }
        
        return type_map.get(data_type, data_type.replace("i=", "Type"))
    
    async def _get_namespaces(self) -> dict[int, str]:
        """
        Get namespace array from server using asyncua native method.
        
        Returns:
            Dictionary mapping namespace index to URI
        """
        try:
            # Use asyncua native method to get namespace array
            namespace_array = await self.client.get_namespace_array()
            return {idx: uri for idx, uri in enumerate(namespace_array)}
        except Exception as e:
            logger.warning(f"Could not retrieve namespaces: {e}")
            return {}
    
    async def _is_namespace_node(self, node: Node, browse_name: str) -> bool:
        """
        Check if node is namespace-related using asyncua ObjectIds.
        
        Args:
            node: Node to check
            browse_name: Browse name of the node
            
        Returns:
            True if node is namespace-related
        """
        # Check for common namespace-related names
        namespace_keywords = [
            "Namespace",
            "NamespaceArray",
            "Server",
            "ServerArray",
            "ServerCapabilities",
            "ServerDiagnostics",
        ]
        
        # Check browse name
        if any(keyword in browse_name for keyword in namespace_keywords):
            return True
        
        # Check node ID using asyncua ObjectIds constants
        node_id_int = None
        if node.nodeid.NamespaceIndex == 0 and hasattr(node.nodeid, 'Identifier'):
            node_id_int = node.nodeid.Identifier
        
        # List of standard namespace-related ObjectIds
        namespace_object_ids = [
            ua.ObjectIds.Server,
            ua.ObjectIds.Server_NamespaceArray,
            ua.ObjectIds.Server_ServerArray,
            ua.ObjectIds.Server_ServerCapabilities,
            ua.ObjectIds.Server_ServerDiagnostics,
        ]
        
        return node_id_int in namespace_object_ids if node_id_int else False
    
    def _validate_node_id(self, node_id: str) -> bool:
        """
        Validate Node ID format.
        
        Args:
            node_id: Node ID string to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Valid formats:
        # - i=123 (numeric in namespace 0)
        # - ns=2;i=456 (numeric with namespace)
        # - ns=2;s=StringId (string with namespace)
        # - ns=2;g=GUID (GUID with namespace)
        # - ns=2;b=ByteString (byte string with namespace)
        
        import re
        
        patterns = [
            r'^i=\d+$',  # i=123
            r'^ns=\d+;i=\d+$',  # ns=2;i=456
            r'^ns=\d+;s=.+$',  # ns=2;s=StringId
            r'^ns=\d+;g=[0-9a-fA-F-]+$',  # ns=2;g=GUID
            r'^ns=\d+;b=.+$',  # ns=2;b=ByteString
        ]
        
        return any(re.match(pattern, node_id) for pattern in patterns)
    
    def print_tree(self, result: BrowseResult) -> None:
        """
        Print browse result as a formatted tree structure to console.
        
        This method generates a visual tree representation of the browsed
        address space with:
        - Hierarchical indentation showing parent-child relationships
        - Emoji icons indicating node types
        - Summary statistics (total nodes, depth, namespaces)
        - Type information for variables
        - Namespace indicators
        - Node ID references for root nodes
        
        The output is limited to 500 nodes for performance. Use the export
        command for complete data extraction.
        
        Args:
            result: BrowseResult containing discovered nodes and metadata
            
        Output Format:
            - Header with summary statistics
            - Namespace list with node counts
            - Tree structure with visual connectors
            - Truncation warning if needed
            
        Note:
            Only prints if result.success is True. Failed browse operations
            only show an error message.
        """
        print("\n" + "=" * 100)
        print("OPC UA ADDRESS SPACE TREE")
        print("=" * 100)
        
        if not result.success:
            print("\n❌ Browse operation failed")
            print(f"   Error: {result.error_message}")
            print("=" * 100 + "\n")
            return
        
        if result.total_nodes == 0:
            print("\n⚠️  No nodes found")
            print("   The specified node has no children or access is restricted.")
            print("=" * 100 + "\n")
            return
        
        # Print server summary
        print(f"\n📊 SUMMARY:")
        print(f"   • Total Nodes: {result.total_nodes}")
        print(f"   • Max Depth: {result.max_depth_reached}")
        print(f"   • Namespaces: {len(result.namespaces)}")
        
        # Count node types
        node_types = {}
        for node in result.nodes:
            node_types[node.node_class] = node_types.get(node.node_class, 0) + 1
        
        print(f"\n📈 NODE TYPES:")
        for node_type, count in sorted(node_types.items()):
            icon = {
                "Object": "📁", "Variable": "📊", "Method": "⚙️",
                "ObjectType": "📦", "VariableType": "📈", "DataType": "🔢",
                "ReferenceType": "🔗", "View": "👁️"
            }.get(node_type, "📄")
            print(f"   {icon} {node_type}: {count}")
        
        # Print namespaces with details
        if result.namespaces:
            print(f"\n🌐 NAMESPACES:")
            for idx, uri in result.namespaces.items():
                # Count nodes in this namespace
                ns_count = sum(1 for n in result.nodes if n.namespace_index == idx)
                print(f"   [{idx}] {uri}")
                if ns_count > 0:
                    print(f"       └─ {ns_count} nodes")
        
        # Print node tree with better formatting
        print(f"\n🌳 NODE TREE:")
        print("-" * 100)
        
        # Optionally limit display for very large trees
        max_display = 500
        display_nodes = result.nodes[:max_display]
        
        for node in display_nodes:
            indent = "│  " * node.depth
            
            # Icon based on node class
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
            icon = icons.get(node.node_class, "📄")
            
            # Format node info
            connector = "└─ " if node.depth > 0 else ""
            node_info = f"{indent}{connector}{icon} {node.display_name}"
            
            # Add browse name if different and not just a number
            if (node.display_name != node.browse_name and 
                not node.browse_name.startswith('[') and 
                not node.browse_name.isdigit()):
                node_info += f" ({node.browse_name})"
            
            # Add data type for variables (simplified)
            if node.data_type:
                # Extract just the type number/name
                if ';' in node.data_type:
                    type_part = node.data_type.split(';')[-1]
                else:
                    type_part = node.data_type
                    
                # Map common types to readable names
                type_names = {
                    "i=1": "Boolean", "i=3": "Byte", "i=6": "Int32",
                    "i=7": "UInt32", "i=11": "Double", "i=12": "String",
                    "i=13": "DateTime", "i=21": "LocalizedText"
                }
                type_display = type_names.get(type_part, type_part.replace("i=", "Type"))
                node_info += f" [{type_display}]"
            
            # Add value if present (only for non-object nodes)
            if node.value is not None and node.node_class == "Variable":
                value_str = str(node.value)
                if len(value_str) > 40:
                    value_str = value_str[:37] + "..."
                node_info += f" = {value_str}"
            
            # Add namespace indicator if not namespace 0
            if node.namespace_index > 0:
                node_info += f" [ns={node.namespace_index}]"
            
            print(node_info)
            
            # Print node ID only for root-level nodes
            if node.depth == 0:
                print(f"{indent}   💡 NodeId: {node.node_id}")
        
        # Show warning if tree was truncated
        if len(result.nodes) > max_display:
            print(f"\n⚠️  Tree truncated: showing {max_display} of {result.total_nodes} nodes")
            print(f"   Use 'export' command to see all nodes")
        
        print("-" * 100)
        print(f"\n✅ Browse completed successfully")
        print("=" * 100 + "\n")