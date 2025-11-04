"""OPC UA Address Space browser with recursive navigation.

This module provides functionality to recursively browse and explore OPC UA
address spaces, extracting node information at configurable depths with
support for value reading and namespace filtering.
"""

from __future__ import annotations

import re

from asyncua import Client, ua
from asyncua.common.node import Node
from asyncua.ua import NodeClass, ObjectIds, VariantType
from loguru import logger

from .models import BrowseResult, OpcUaNode


class OpcUaBrowser:
    """Handles recursive browsing of OPC UA Address Space.

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
        client: Connected asyncua Client instance.
        max_depth: Maximum recursion depth for browsing.
        include_values: Whether to read current values from Variable nodes.
        namespaces_only: Filter to show only namespace-related nodes.

    Examples:
        Basic browse:
            >>> async with OpcUaClient("opc.tcp://localhost:4840") as client:
            ...     browser = OpcUaBrowser(client.get_client(), max_depth=5)
            ...     result = await browser.browse()
            ...     browser.print_tree(result)

        Browse with value reading:
            >>> browser = OpcUaBrowser(
            ...     client.get_client(),
            ...     max_depth=3,
            ...     include_values=True
            ... )
            >>> result = await browser.browse(start_node_id="ns=2;i=1000")
    """

    # Map asyncua NodeClass enum to human-readable names
    NODE_CLASS_NAMES: dict[NodeClass, str] = {
        NodeClass.Object: "Object",
        NodeClass.Variable: "Variable",
        NodeClass.Method: "Method",
        NodeClass.ObjectType: "ObjectType",
        NodeClass.VariableType: "VariableType",
        NodeClass.ReferenceType: "ReferenceType",
        NodeClass.DataType: "DataType",
        NodeClass.View: "View",
    }

    # Map asyncua VariantType enum to human-readable names
    DATA_TYPE_NAMES: dict[VariantType, str] = {
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

    # Node ID validation patterns (OPC UA specification compliant)
    NODE_ID_PATTERNS: list[re.Pattern] = [
        re.compile(r"^i=\d+$"),  # Numeric: i=123
        re.compile(r"^ns=\d+;i=\d+$"),  # Numeric with namespace: ns=2;i=456
        re.compile(r"^ns=\d+;s=.+$"),  # String: ns=2;s=StringId
        re.compile(r"^ns=\d+;g=[0-9a-fA-F-]+$"),  # GUID: ns=2;g=UUID
        re.compile(r"^ns=\d+;b=.+$"),  # ByteString: ns=2;b=Base64
    ]

    # Namespace-related keywords for filtering
    NAMESPACE_KEYWORDS: list[str] = [
        "Namespace",
        "NamespaceArray",
        "Server",
        "ServerArray",
        "ServerCapabilities",
        "ServerDiagnostics",
    ]

    # OPC UA standard namespace-related ObjectIds
    NAMESPACE_OBJECT_IDS: list[int] = [
        ObjectIds.Server,
        ObjectIds.Server_NamespaceArray,
        ObjectIds.Server_ServerArray,
        ObjectIds.Server_ServerCapabilities,
        ObjectIds.Server_ServerDiagnostics,
    ]

    def __init__(
        self,
        client: Client,
        max_depth: int = 3,
        include_values: bool = False,
        namespaces_only: bool = False,
        namespace_filter: int | None = None,
    ) -> None:
        """Initialize OPC UA browser with configuration.

        Args:
            client: Connected asyncua Client instance.
            max_depth: Maximum depth for recursive browsing (default: 3).
            include_values: Whether to read variable values (default: False).
            namespaces_only: Whether to filter only namespace-related nodes (default: False).
            namespace_filter: Filter nodes by namespace index (e.g., 2).
        """
        self.client: Client = client
        self.max_depth: int = max_depth
        self.include_values: bool = include_values
        self.namespaces_only: bool = namespaces_only
        self.namespace_filter: int | None = namespace_filter

        logger.info(
            f"Browser initialized (max_depth={max_depth}, "
            f"include_values={include_values}, namespaces_only={namespaces_only}, "
            f"namespace_filter={namespace_filter})"
        )

    async def browse(self, start_node_id: str = "i=84") -> BrowseResult:
        """Browse the OPC UA Address Space starting from a specific node.

        Performs recursive navigation of the address space, collecting node
        information, namespaces, and optional values. Validates node ID format
        before starting and provides detailed error messages for failures.

        Args:
            start_node_id: Node ID to start browsing from. Default is "i=84"
                (RootFolder). Format: "i=123", "ns=2;i=456", or "ns=2;s=MyNode".

        Returns:
            BrowseResult containing all discovered nodes, namespaces, statistics,
            and success/error status.

        Examples:
            >>> result = await browser.browse()  # From RootFolder
            >>> result = await browser.browse("ns=2;i=1000")  # Custom start
        """
        result: BrowseResult = BrowseResult()

        try:
            logger.info(f"Starting browse from node: {start_node_id}")

            if not self._validate_node_id(start_node_id):
                error_msg: str = self._get_node_id_validation_error(start_node_id)
                logger.error(error_msg)
                result.success = False
                result.error_message = error_msg
                return result

            result.namespaces = await self._get_namespaces()
            logger.info(f"Found {len(result.namespaces)} namespaces")

            # Log namespace URIs for user reference
            for idx, uri in result.namespaces.items():
                logger.debug(f"  Namespace[{idx}]: {uri}")

            # Validate namespace_filter if provided
            if self.namespace_filter is not None:
                if self.namespace_filter not in result.namespaces:
                    error_msg = (
                        f"Namespace index {self.namespace_filter} not found. "
                        f"Available: {list(result.namespaces.keys())}"
                    )
                    logger.error(error_msg)
                    result.success = False
                    result.error_message = error_msg
                    return result
                logger.info(
                    f"Filtering nodes by namespace[{self.namespace_filter}]: "
                    f"{result.namespaces[self.namespace_filter]}"
                )

            # Get and validate starting node
            try:
                start_node: Node = self.client.get_node(start_node_id)
                await start_node.read_node_class()  # Verify node exists
            except ua.UaStatusCodeError as e:
                error_code: str = (
                    e.code.name if hasattr(e.code, "name") else f"Status code: {e.code}"
                )
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

            await self._browse_recursive(
                node=start_node,
                parent_id=None,
                depth=0,
                result=result,
            )

            # Apply namespace filtering if configured
            if self.namespaces_only:
                original_count = result.total_nodes
                result.nodes = [node for node in result.nodes if node.is_namespace_node]
                result.total_nodes = len(result.nodes)
                logger.info(
                    f"Namespace filter applied: {result.total_nodes} namespace nodes "
                    f"out of {original_count} total nodes"
                )
            elif self.namespace_filter is not None:
                original_count = result.total_nodes
                result.nodes = [
                    node for node in result.nodes
                    if node.namespace_index == self.namespace_filter
                ]
                result.total_nodes = len(result.nodes)
                logger.info(
                    f"Namespace index filter applied: {result.total_nodes} nodes "
                    f"from namespace[{self.namespace_filter}] out of {original_count} total nodes"
                )

            if result.total_nodes == 0:
                logger.warning(
                    f"No nodes discovered from '{start_node_id}'. "
                    f"The node may have no children or access is restricted."
                )
            else:
                # Compute full OPC UA paths for all nodes
                logger.info("Computing full OPC UA paths...")
                result.compute_full_paths()

            logger.success(
                f"✅ Browse completed: {result.total_nodes} nodes discovered "
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
        parent_id: str | None,
        depth: int,
        result: BrowseResult,
    ) -> None:
        """Recursively browse nodes up to configured maximum depth.

        Extracts complete node information including ID, names, class, type,
        and optional values. Applies namespace filtering if configured.

        Args:
            node: Current asyncua Node instance to browse.
            parent_id: Node ID of the parent node (None for root).
            depth: Current recursion depth level.
            result: BrowseResult accumulator for discovered nodes.
        """
        if depth > self.max_depth:
            return

        try:
            node_id: str = node.nodeid.to_string()
            browse_name_obj: ua.QualifiedName = await node.read_browse_name()
            browse_name: str = browse_name_obj.Name
            display_name_obj: ua.LocalizedText = await node.read_display_name()
            display_name: str = display_name_obj.Text
            node_class: NodeClass = await node.read_node_class()
            namespace_index: int = node.nodeid.NamespaceIndex

            is_namespace_node: bool = await self._is_namespace_node(node, browse_name)

            data_type: str | None = None
            value: any | None = None
            data_type_name: str | None = None

            if node_class == NodeClass.Variable:
                try:
                    data_type_node: ua.NodeId = await node.read_data_type()
                    data_type = data_type_node.to_string()

                    # Attempt to get variant type for better type name
                    try:
                        variant: ua.DataValue = await node.read_data_value()
                        if variant.Value and hasattr(variant.Value, "VariantType"):
                            variant_type: VariantType = variant.Value.VariantType
                            data_type_name = self.DATA_TYPE_NAMES.get(
                                variant_type,
                                self._parse_data_type_id(data_type),
                            )
                        else:
                            data_type_name = self._parse_data_type_id(data_type)
                    except Exception:
                        data_type_name = self._parse_data_type_id(data_type)

                    if self.include_values:
                        value_variant = await node.read_value()
                        value = value_variant

                except Exception as e:
                    logger.debug(f"Could not read variable data for {node_id}: {e}")

            opc_node: OpcUaNode = OpcUaNode(
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

            result.add_node(opc_node)

            # Progress logging for large address spaces
            if depth == 0 and result.total_nodes % 10 == 0:
                logger.info(f"Discovered {result.total_nodes} nodes so far...")

            if depth < self.max_depth:
                try:
                    children: list[Node] = await node.get_children()

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
        """Parse OPC UA data type Node ID to human-readable name.

        Maps standard OPC UA data type IDs to their canonical names using
        asyncua's ObjectIds constants for accuracy.

        Args:
            data_type: Data type node ID string (e.g., "i=12" for String).

        Returns:
            Human-readable data type name or simplified type ID.

        Examples:
            >>> self._parse_data_type_id("i=12")
            "String"
            >>> self._parse_data_type_id("i=11")
            "Double"
        """
        type_map: dict[str, str] = {
            f"i={ObjectIds.Boolean}": "Boolean",
            f"i={ObjectIds.SByte}": "SByte",
            f"i={ObjectIds.Byte}": "Byte",
            f"i={ObjectIds.Int16}": "Int16",
            f"i={ObjectIds.UInt16}": "UInt16",
            f"i={ObjectIds.Int32}": "Int32",
            f"i={ObjectIds.UInt32}": "UInt32",
            f"i={ObjectIds.Int64}": "Int64",
            f"i={ObjectIds.UInt64}": "UInt64",
            f"i={ObjectIds.Float}": "Float",
            f"i={ObjectIds.Double}": "Double",
            f"i={ObjectIds.String}": "String",
            f"i={ObjectIds.DateTime}": "DateTime",
            f"i={ObjectIds.Guid}": "Guid",
            f"i={ObjectIds.ByteString}": "ByteString",
            f"i={ObjectIds.XmlElement}": "XmlElement",
            f"i={ObjectIds.NodeId}": "NodeId",
            f"i={ObjectIds.ExpandedNodeId}": "ExpandedNodeId",
            f"i={ObjectIds.StatusCode}": "StatusCode",
            f"i={ObjectIds.QualifiedName}": "QualifiedName",
            f"i={ObjectIds.LocalizedText}": "LocalizedText",
        }

        return type_map.get(data_type, data_type.replace("i=", "Type"))

    async def _get_namespaces(self) -> dict[int, str]:
        """Retrieve namespace array from OPC UA server.

        Uses asyncua's native method to fetch the complete namespace array,
        which maps namespace indices to their URIs.

        Returns:
            Dictionary mapping namespace index (int) to namespace URI (str).
            Empty dict if retrieval fails.

        Examples:
            >>> namespaces = await self._get_namespaces()
            {0: 'http://opcfoundation.org/UA/', 1: 'urn:MyServer', ...}
        """
        try:
            namespace_array: list[str] = await self.client.get_namespace_array()
            return dict(enumerate(namespace_array))
        except Exception as e:
            logger.warning(f"Could not retrieve namespaces: {e}")
            return {}

    async def _is_namespace_node(self, node: Node, browse_name: str) -> bool:
        """Check if node is namespace-related using OPC UA standards.

        Identifies namespace nodes by checking browse name keywords and
        comparing node IDs against standard OPC UA ObjectIds.

        Args:
            node: asyncua Node instance to check.
            browse_name: Browse name of the node.

        Returns:
            True if node is namespace-related, False otherwise.
        """
        if any(keyword in browse_name for keyword in self.NAMESPACE_KEYWORDS):
            return True

        node_id_int: int | None = None
        if node.nodeid.NamespaceIndex == 0 and hasattr(node.nodeid, "Identifier"):
            node_id_int = node.nodeid.Identifier

        return node_id_int in self.NAMESPACE_OBJECT_IDS if node_id_int else False

    def _validate_node_id(self, node_id: str) -> bool:
        """Validate Node ID format against OPC UA specification.

        Checks if the node ID string matches one of the standard OPC UA
        formats: numeric, string, GUID, or opaque (ByteString).

        Args:
            node_id: Node ID string to validate.

        Returns:
            True if format is valid, False otherwise.

        Valid Formats:
            - i=123 (numeric in namespace 0)
            - ns=2;i=456 (numeric with namespace)
            - ns=2;s=StringId (string with namespace)
            - ns=2;g=UUID (GUID with namespace)
            - ns=2;b=Base64 (byte string with namespace)
        """
        return any(pattern.match(node_id) for pattern in self.NODE_ID_PATTERNS)

    def _get_node_id_validation_error(self, node_id: str) -> str:
        """Generate detailed validation error message with examples.

        Args:
            node_id: Invalid node ID string.

        Returns:
            Detailed error message with valid format examples.
        """
        error_msg = f"Invalid Node ID format: '{node_id}'\n\n"
        error_msg += "Valid formats:\n"
        error_msg += "  • Numeric (ns=0):        i=84\n"
        error_msg += "  • Numeric with ns:       ns=2;i=1000\n"
        error_msg += "  • String with ns:        ns=2;s=Studio\n"
        error_msg += "  • GUID with ns:          ns=2;g=09087e75-8e5e-499b-954f-f2a9603db28a\n"
        error_msg += "  • ByteString with ns:    ns=2;b=YWJjZGVm\n\n"

        # Try to provide helpful hints
        if "=" not in node_id:
            error_msg += "Hint: Node ID must contain '=' (e.g., 'i=84' or 'ns=2;s=Studio')\n"
        elif node_id.startswith("s="):
            error_msg += f"Hint: Did you mean 'ns=2;s={node_id[2:]}'? String IDs require namespace prefix.\n"
        elif node_id.startswith("ns=") and ";" not in node_id:
            error_msg += "Hint: After 'ns=X' you need ';i=', ';s=', ';g=', or ';b=' followed by the identifier.\n"

        return error_msg

    def print_tree(self, result: BrowseResult) -> None:
        """Print browse result as formatted tree structure to console.

        Generates a visual tree representation of the browsed address space with:
        - Hierarchical indentation showing parent-child relationships
        - Emoji icons indicating node types
        - Summary statistics (total nodes, depth, namespaces)
        - Type information for variables
        - Namespace indicators
        - Node ID references for root and depth-1 nodes

        The output is limited to 500 nodes for performance. Use the export
        command for complete data extraction of large address spaces.

        Args:
            result: BrowseResult containing discovered nodes and metadata.

        Output Format:
            - Header with summary statistics
            - Node type distribution
            - Namespace list with node counts
            - Tree structure with visual connectors
            - NodeID hints for navigable nodes
            - Truncation warning if needed

        Note:
            Only prints tree if result.success is True. Failed browse operations
            display only an error message.
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

        print("\n📊 SUMMARY:")
        print(f"   • Total Nodes: {result.total_nodes}")
        print(f"   • Max Depth: {result.max_depth_reached}")
        print(f"   • Namespaces: {len(result.namespaces)}")

        # Count and display node type distribution
        node_types: dict[str, int] = {}
        for node in result.nodes:
            node_types[node.node_class] = node_types.get(node.node_class, 0) + 1

        print("\n📈 NODE TYPES:")
        icon_map: dict[str, str] = {
            "Object": "📁",
            "Variable": "📊",
            "Method": "⚙️",
            "ObjectType": "📦",
            "VariableType": "📈",
            "DataType": "🔢",
            "ReferenceType": "🔗",
            "View": "👁️",
        }
        for node_type, count in sorted(node_types.items()):
            icon: str = icon_map.get(node_type, "📄")
            print(f"   {icon} {node_type}: {count}")

        if result.namespaces:
            print("\n🌐 NAMESPACES:")
            for idx, uri in result.namespaces.items():
                ns_count: int = sum(1 for n in result.nodes if n.namespace_index == idx)
                print(f"   [{idx}] {uri}")
                if ns_count > 0:
                    print(f"       └─ {ns_count} nodes")

        print("\n🌳 NODE TREE:")
        print("-" * 100)

        # Limit display for very large trees to prevent performance issues
        max_display: int = 500
        display_nodes: list[OpcUaNode] = result.nodes[:max_display]

        # Common data type ID to name mapping for display
        type_names: dict[str, str] = {
            "i=1": "Boolean",
            "i=3": "Byte",
            "i=6": "Int32",
            "i=7": "UInt32",
            "i=11": "Double",
            "i=12": "String",
            "i=13": "DateTime",
            "i=21": "LocalizedText",
        }

        for node in display_nodes:
            indent: str = "│  " * node.depth
            icon: str = icon_map.get(node.node_class, "📄")
            connector: str = "└─ " if node.depth > 0 else ""
            node_info: str = f"{indent}{connector}{icon} {node.display_name}"

            # Add browse name if different and meaningful
            if (
                node.display_name != node.browse_name
                and not node.browse_name.startswith("[")
                and not node.browse_name.isdigit()
            ):
                node_info += f" ({node.browse_name})"

            # Add data type for variables
            if node.data_type:
                type_part: str = (
                    node.data_type.split(";")[-1]
                    if ";" in node.data_type
                    else node.data_type
                )
                type_display: str = type_names.get(type_part, type_part.replace("i=", "Type"))
                node_info += f" [{type_display}]"

            # Add value for Variable nodes
            if node.value is not None and node.node_class == "Variable":
                value_str: str = str(node.value)
                if len(value_str) > 40:
                    value_str = value_str[:37] + "..."
                node_info += f" = {value_str}"

            # Add namespace indicator for non-standard namespaces
            if node.namespace_index > 0:
                node_info += f" [ns={node.namespace_index}]"

            print(node_info)

            # Display NodeID for root nodes (depth=0) and direct children (depth=1)
            # This helps users identify correct NodeIDs for -n parameter
            if node.depth <= 1:
                print(f"{indent}   💡 NodeId: {node.node_id}")

        if len(result.nodes) > max_display:
            print(f"\n⚠️  Tree truncated: showing {max_display} of {result.total_nodes} nodes")
            print("   Use 'export' command to see all nodes")

        print("-" * 100)
        print("\n✅ Browse completed successfully")
        print("=" * 100 + "\n")
