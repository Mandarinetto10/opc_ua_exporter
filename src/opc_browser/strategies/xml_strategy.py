"""
XML export strategy implementation.
"""

from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement, indent

from loguru import logger

from ..models import BrowseResult, OpcUaNode
from .base import ExportStrategy


class XmlExportStrategy(ExportStrategy):
    """XML export strategy for OPC UA nodes."""

    async def export(
        self, 
        result: BrowseResult, 
        output_path: Path | None,
        full_export: bool = False  # NEW
    ) -> Path:
        """Export nodes to XML file with pretty formatting.

        Args:
            result: BrowseResult to export
            output_path: Path to output XML file
            full_export: If True, include all OPC UA extended attributes
        """
        logger.debug(f"XML export started: {len(result.nodes)} nodes to {output_path}")

        self.validate_result(result)
        self.ensure_output_directory(output_path)

        logger.info(f"Exporting {len(result.nodes)} nodes to XML: {output_path}")

        try:
            # Only export nodes, no summary/statistics/namespaces
            root = Element("OpcUaNodes")
            for node in result.nodes:
                node_elem = self.node_to_element(node)
                root.append(node_elem)

            logger.debug(f"All {len(result.nodes)} nodes added to XML structure")

            # Create tree and write to file with indentation
            logger.debug(f"Writing XML to file: {output_path}")
            tree = ElementTree(root)
            indent(tree, space="  ")  # Pretty print with 2-space indentation

            tree.write(
                output_path,
                encoding='utf-8',
                xml_declaration=True,
            )

            file_size = output_path.stat().st_size
            logger.debug(f"XML file written successfully: {file_size:,} bytes")

            return output_path

        except OSError as e:
            error_msg = f"Failed to write XML file: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise OSError(error_msg) from e
        except Exception as e:
            error_msg = f"XML export failed: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise

    def node_to_element(self, node: OpcUaNode, full_export: bool = False) -> Element:
        """Convert an OpcUaNode to an XML element.

        Args:
            node: OpcUaNode to convert
            full_export: If True, include all OPC UA extended attributes

        Returns:
            XML element representing the node
        """
        node_elem = Element("Node")

        # Base attributes
        SubElement(node_elem, "NodeId").text = node.node_id
        SubElement(node_elem, "BrowseName").text = node.browse_name
        SubElement(node_elem, "DisplayName").text = node.display_name
        SubElement(node_elem, "NodeClass").text = node.node_class

        if node.data_type:
            SubElement(node_elem, "DataType").text = node.data_type

        if node.value is not None:
            SubElement(node_elem, "Value").text = str(node.value)

        if node.parent_id:
            SubElement(node_elem, "ParentId").text = node.parent_id

        SubElement(node_elem, "Depth").text = str(node.depth)
        SubElement(node_elem, "NamespaceIndex").text = str(node.namespace_index)
        SubElement(node_elem, "IsNamespaceNode").text = str(node.is_namespace_node)

        if node.timestamp:
            SubElement(node_elem, "Timestamp").text = node.timestamp.isoformat()

        # Extended attributes (full export only)
        if full_export:
            if node.description:
                SubElement(node_elem, "Description").text = node.description
            if node.access_level:
                SubElement(node_elem, "AccessLevel").text = node.access_level
            if node.user_access_level:
                SubElement(node_elem, "UserAccessLevel").text = node.user_access_level
            if node.write_mask is not None:
                SubElement(node_elem, "WriteMask").text = str(node.write_mask)
            if node.user_write_mask is not None:
                SubElement(node_elem, "UserWriteMask").text = str(node.user_write_mask)
            if node.event_notifier is not None:
                SubElement(node_elem, "EventNotifier").text = str(node.event_notifier)
            if node.executable is not None:
                SubElement(node_elem, "Executable").text = str(node.executable)
            if node.user_executable is not None:
                SubElement(node_elem, "UserExecutable").text = str(node.user_executable)
            if node.minimum_sampling_interval is not None:
                SubElement(node_elem, "MinimumSamplingInterval").text = str(node.minimum_sampling_interval)
            if node.historizing is not None:
                SubElement(node_elem, "Historizing").text = str(node.historizing)

        return node_elem

    def get_file_extension(self) -> str:
        """Get XML file extension."""
        return "xml"
