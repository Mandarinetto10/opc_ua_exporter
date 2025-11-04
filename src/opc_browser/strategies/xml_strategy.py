"""
XML export strategy implementation.
"""

from datetime import datetime
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
        Export nodes to XML file with pretty formatting.
        
        Creates a well-structured XML document with:
        - Metadata section with statistics
        - Namespaces section with index and URI
        - Nodes section with complete node information
        - Proper indentation for readability
        - ISO 8601 timestamp formatting
        
        Args:
            result: BrowseResult to export
            output_path: Path to output XML file
            
        Raises:
            ValueError: If result is invalid or empty
            IOError: If file cannot be written
        """
        logger.debug(f"XML export started: {len(result.nodes)} nodes to {output_path}")
        
        self.validate_result(result)
        self.ensure_output_directory(output_path)
        
        logger.info(f"Exporting {len(result.nodes)} nodes to XML: {output_path}")
        
        try:
            # Create root element
            logger.debug("Building XML structure...")
            root = Element("OpcUaAddressSpace")
            
            # Add metadata section
            metadata = SubElement(root, "Metadata")
            SubElement(metadata, "TotalNodes").text = str(result.total_nodes)
            SubElement(metadata, "MaxDepthReached").text = str(result.max_depth_reached)
            SubElement(metadata, "Success").text = str(result.success)
            SubElement(metadata, "ExportTimestamp").text = datetime.now().isoformat()
            if result.error_message:
                SubElement(metadata, "ErrorMessage").text = result.error_message
            
            logger.debug(f"Metadata created: {result.total_nodes} nodes, max depth {result.max_depth_reached}")
            
            # Add namespaces section
            namespaces = SubElement(root, "Namespaces")
            for idx, uri in result.namespaces.items():
                ns = SubElement(namespaces, "Namespace")
                SubElement(ns, "Index").text = str(idx)
                SubElement(ns, "URI").text = uri
            
            logger.debug(f"Namespaces section created: {len(result.namespaces)} namespaces")
            
            # Add nodes section with progress logging
            nodes = SubElement(root, "Nodes")
            nodes_added = 0
            for node in result.nodes:
                self._add_node_element(nodes, node)
                nodes_added += 1
                
                # Progress logging for large exports
                if nodes_added % 100 == 0:
                    logger.debug(f"Progress: {nodes_added}/{len(result.nodes)} nodes added")
            
            logger.debug(f"All {nodes_added} nodes added to XML structure")
            
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
            logger.success(
                f"✅ XML export completed successfully\n"
                f"   File: {output_path.absolute()}\n"
                f"   Size: {file_size / 1024:.2f} KB\n"
                f"   Nodes: {result.total_nodes}\n"
                f"   Format: UTF-8 with XML declaration, 2-space indentation"
            )
            
        except IOError as e:
            error_msg = f"Failed to write XML file: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg) from e
        except Exception as e:
            error_msg = f"XML export failed: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise
    
    def _add_node_element(self, parent: Element, node: OpcUaNode) -> None:
        """
        Add a node as XML element with all attributes.
        
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
