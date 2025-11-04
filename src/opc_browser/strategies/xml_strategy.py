"""
XML export strategy implementation.
"""

from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree, indent
from loguru import logger

from .base import ExportStrategy
from ..models import BrowseResult, OpcUaNode


class XmlExportStrategy(ExportStrategy):
    """
    Exports browse results to XML format.
    
    XML format is ideal for:
    - Enterprise systems and SOAP services
    - Configuration files
    - Industry standard data exchange
    - Schema validation and transformation
    """
    
    async def export(self, result: BrowseResult, output_path: Path) -> None:
        """
        Export nodes to XML file.
        
        Args:
            result: BrowseResult to export
            output_path: Path to output XML file
        """
        self.validate_result(result)
        self.ensure_output_directory(output_path)
        
        logger.info(f"Exporting {len(result.nodes)} nodes to XML: {output_path}")
        
        try:
            # Create root element
            root = Element("OpcUaAddressSpace")
            
            # Add metadata section
            metadata = SubElement(root, "Metadata")
            SubElement(metadata, "TotalNodes").text = str(result.total_nodes)
            SubElement(metadata, "MaxDepthReached").text = str(result.max_depth_reached)
            SubElement(metadata, "Success").text = str(result.success)
            if result.error_message:
                SubElement(metadata, "ErrorMessage").text = result.error_message
            
            # Add namespaces section
            namespaces = SubElement(root, "Namespaces")
            for idx, uri in result.namespaces.items():
                ns = SubElement(namespaces, "Namespace")
                SubElement(ns, "Index").text = str(idx)
                SubElement(ns, "URI").text = uri
            
            # Add nodes section
            nodes = SubElement(root, "Nodes")
            for node in result.nodes:
                self._add_node_element(nodes, node)
            
            # Create tree and write to file with indentation
            tree = ElementTree(root)
            indent(tree, space="  ")  # Pretty print with 2-space indentation
            
            tree.write(
                output_path,
                encoding='utf-8',
                xml_declaration=True,
            )
            
            logger.success(f"XML export completed: {output_path}")
            
        except Exception as e:
            logger.error(f"XML export failed: {e}")
            raise
    
    def _add_node_element(self, parent: Element, node: OpcUaNode) -> None:
        """
        Add a node as XML element.
        
        Args:
            parent: Parent XML element
            node: OpcUaNode to add
        """
        node_elem = SubElement(parent, "Node")
        
        # Add node attributes as child elements
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
    
    def get_file_extension(self) -> str:
        """Get XML file extension."""
        return "xml"
