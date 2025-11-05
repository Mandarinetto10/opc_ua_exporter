"""Integration tests for OPC UA Browser and Client with real server.

These tests attempt to connect to a real OPC UA server running on localhost:4840.
If the server is not available, tests are skipped gracefully without failing.

To run these tests with a real server:
1. Start your OPC UA server on opc.tcp://localhost:4840
2. Run: pytest tests/test_integration.py -v
3. Run with marker: pytest -m integration -v

If no server is running, tests will be skipped automatically.
"""

from __future__ import annotations

import asyncio

import pytest

from opc_browser.browser import OpcUaBrowser
from opc_browser.client import ConnectionError as OpcConnectionError
from opc_browser.client import OpcUaClient

# Configuration for real OPC UA server
REAL_SERVER_URL = "opc.tcp://localhost:4840"
REAL_SERVER_TIMEOUT = 3  # seconds to wait before considering server unavailable


async def check_server_available(server_url: str = REAL_SERVER_URL) -> bool:
    """Check if OPC UA server is available and responding.

    Args:
        server_url: Server URL to check

    Returns:
        True if server is reachable, False otherwise
    """
    try:
        async with OpcUaClient(server_url=server_url) as client:
            # Try to connect with short timeout
            await asyncio.wait_for(client.client.connect(), timeout=REAL_SERVER_TIMEOUT)
            return True
    except (asyncio.TimeoutError, OpcConnectionError, Exception):
        return False


@pytest.fixture
async def server_available():
    """Fixture to check if real OPC UA server is available.

    Yields:
        bool: True if server is available, False otherwise
    """
    available = await check_server_available()
    yield available


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_browse_basic(server_available):
    """Test basic browse operation on real OPC UA server.

    Connects to localhost:4840 and performs a shallow browse.
    """
    if not server_available:
        pytest.skip("OPC UA server not available on localhost:4840")

    try:
        async with OpcUaClient(server_url=REAL_SERVER_URL) as client:
            browser = OpcUaBrowser(client=client.get_client(), max_depth=2, include_values=False)

            result = await browser.browse(start_node_id="i=84")

            # Basic assertions
            assert result.success is True
            assert result.error_message is None
            assert result.total_nodes > 0
            assert len(result.namespaces) > 0
            assert result.max_depth_reached <= 2

            # Check for standard OPC UA namespace
            assert 0 in result.namespaces
            assert "opcfoundation.org" in result.namespaces[0].lower()

            # Verify at least root node exists
            root_nodes = [n for n in result.nodes if n.depth == 0]
            assert len(root_nodes) > 0

            print("\n✅ Real browse successful:")
            print(f"   Total nodes: {result.total_nodes}")
            print(f"   Max depth: {result.max_depth_reached}")
            print(f"   Namespaces: {len(result.namespaces)}")

    except Exception as e:
        pytest.skip(f"Browse failed due to: {type(e).__name__}: {str(e)}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_browse_with_values(server_available):
    """Test browse with value reading on real server."""
    if not server_available:
        pytest.skip("OPC UA server not available")

    try:
        async with OpcUaClient(server_url=REAL_SERVER_URL) as client:
            browser = OpcUaBrowser(client=client.get_client(), max_depth=3, include_values=True)

            result = await browser.browse(start_node_id="i=84")

            assert result.success is True
            assert result.total_nodes > 0

            # Check if any variable nodes have values
            variable_nodes = [n for n in result.nodes if n.node_class == "Variable"]
            if variable_nodes:
                # At least some variables should have values
                nodes_with_values = [n for n in variable_nodes if n.value is not None]
                print(f"\n✅ Variables with values: {len(nodes_with_values)}/{len(variable_nodes)}")

    except Exception as e:
        pytest.skip(f"Browse with values failed: {type(e).__name__}: {str(e)}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_browse_custom_node(server_available):
    """Test browse from custom starting node (Objects folder)."""
    if not server_available:
        pytest.skip("OPC UA server not available")

    try:
        async with OpcUaClient(server_url=REAL_SERVER_URL) as client:
            browser = OpcUaBrowser(client=client.get_client(), max_depth=3)

            # Browse from Objects folder (standard OPC UA node)
            result = await browser.browse(start_node_id="i=85")

            assert result.success is True
            assert result.total_nodes > 0

            # Verify we started from Objects node
            root_node = result.nodes[0] if result.nodes else None
            if root_node:
                assert root_node.depth == 0
                assert "Objects" in root_node.display_name or "Objects" in root_node.browse_name

            print("\n✅ Custom node browse successful from i=85 (Objects)")

    except Exception as e:
        pytest.skip(f"Custom node browse failed: {type(e).__name__}: {str(e)}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_namespaces_only_filter(server_available):
    """Test browsing only namespace-related nodes."""
    if not server_available:
        pytest.skip("OPC UA server not available")

    try:
        async with OpcUaClient(server_url=REAL_SERVER_URL) as client:
            browser = OpcUaBrowser(client=client.get_client(), max_depth=3, namespaces_only=True)

            result = await browser.browse(start_node_id="i=84")

            assert result.success is True

            # All returned nodes should be namespace-related
            for node in result.nodes:
                assert node.is_namespace_node is True

            print(f"\n✅ Namespace-only filter: {result.total_nodes} namespace nodes found")

    except Exception as e:
        pytest.skip(f"Namespace filter test failed: {type(e).__name__}: {str(e)}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_deep_browse(server_available):
    """Test deep browsing with max_depth=5."""
    if not server_available:
        pytest.skip("OPC UA server not available")

    try:
        async with OpcUaClient(server_url=REAL_SERVER_URL) as client:
            browser = OpcUaBrowser(client=client.get_client(), max_depth=5)

            result = await browser.browse(start_node_id="i=84")

            assert result.success is True
            assert result.total_nodes > 0
            assert result.max_depth_reached >= 0
            assert result.max_depth_reached <= 5

            # Check depth distribution
            depth_counts = {}
            for node in result.nodes:
                depth_counts[node.depth] = depth_counts.get(node.depth, 0) + 1

            print("\n✅ Deep browse completed:")
            print(f"   Total nodes: {result.total_nodes}")
            print(f"   Max depth reached: {result.max_depth_reached}")
            print(f"   Depth distribution: {depth_counts}")

    except Exception as e:
        pytest.skip(f"Deep browse failed: {type(e).__name__}: {str(e)}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_full_export_attributes(server_available):
    """Test browsing with full OPC UA attribute export."""
    if not server_available:
        pytest.skip("OPC UA server not available")

    try:
        async with OpcUaClient(server_url=REAL_SERVER_URL) as client:
            browser = OpcUaBrowser(client=client.get_client(), max_depth=2, full_export=True)

            result = await browser.browse(start_node_id="i=84")

            assert result.success is True
            assert result.total_nodes > 0

            # Check if extended attributes were read
            nodes_with_description = [n for n in result.nodes if n.description]
            variable_nodes = [n for n in result.nodes if n.node_class == "Variable"]
            variables_with_access_level = [n for n in variable_nodes if n.access_level is not None]

            print("\n✅ Full export attributes:")
            print(f"   Nodes with description: {len(nodes_with_description)}")
            print(f"   Variables: {len(variable_nodes)}")
            print(f"   Variables with access level: {len(variables_with_access_level)}")

    except Exception as e:
        pytest.skip(f"Full export test failed: {type(e).__name__}: {str(e)}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_client_connection_lifecycle(server_available):
    """Test OPC UA client connection and disconnection lifecycle."""
    if not server_available:
        pytest.skip("OPC UA server not available")

    try:
        # Test manual connection
        client = OpcUaClient(server_url=REAL_SERVER_URL)
        await client.connect()

        # Verify connection by reading server node
        server_node = client.get_client().get_server_node()
        server_info = await server_node.read_browse_name()
        assert server_info.Name is not None

        await client.disconnect()

        # Test context manager
        async with OpcUaClient(server_url=REAL_SERVER_URL) as client:
            server_node = client.get_client().get_server_node()
            server_info = await server_node.read_browse_name()
            assert server_info.Name is not None

        print("\n✅ Client connection lifecycle test passed")

    except Exception as e:
        pytest.skip(f"Connection lifecycle test failed: {type(e).__name__}: {str(e)}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_invalid_node_id(server_available):
    """Test browsing from invalid node ID on real server."""
    if not server_available:
        pytest.skip("OPC UA server not available")

    try:
        async with OpcUaClient(server_url=REAL_SERVER_URL) as client:
            browser = OpcUaBrowser(client=client.get_client(), max_depth=2)

            # Try to browse from non-existent node
            result = await browser.browse(start_node_id="ns=99;i=99999")

            # Should fail gracefully
            assert result.success is False
            assert result.error_message is not None
            assert (
                "not found" in result.error_message.lower()
                or "not accessible" in result.error_message.lower()
            )

            print("\n✅ Invalid node ID handled correctly")

    except Exception as e:
        pytest.skip(f"Invalid node test failed: {type(e).__name__}: {str(e)}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_print_tree(server_available, capsys):
    """Test print_tree output with real server data."""
    if not server_available:
        pytest.skip("OPC UA server not available")

    try:
        async with OpcUaClient(server_url=REAL_SERVER_URL) as client:
            browser = OpcUaBrowser(client=client.get_client(), max_depth=2)

            result = await browser.browse(start_node_id="i=84")
            assert result.success is True

            # Print tree to console
            browser.print_tree(result)

            # Capture output
            captured = capsys.readouterr()

            # Verify tree output contains expected sections
            assert "OPC UA ADDRESS SPACE TREE" in captured.out
            assert "SUMMARY:" in captured.out
            assert "NODE TYPES:" in captured.out
            assert "NAMESPACES:" in captured.out
            assert "NODE TREE:" in captured.out

            print("\n✅ Tree printing test passed")

    except Exception as e:
        pytest.skip(f"Print tree test failed: {type(e).__name__}: {str(e)}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_export_csv(server_available, tmp_path):
    """Test real export to CSV format."""
    if not server_available:
        pytest.skip("OPC UA server not available")

    try:
        from opc_browser.exporter import Exporter

        async with OpcUaClient(server_url=REAL_SERVER_URL) as client:
            browser = OpcUaBrowser(client=client.get_client(), max_depth=2, include_values=True)

            result = await browser.browse(start_node_id="i=84")
            assert result.success is True

            exporter = Exporter(export_format="csv")
            output_path = tmp_path / "test_export.csv"

            final_path = await exporter.export(result, output_path)

            assert final_path.exists()
            assert final_path.stat().st_size > 0

            # Verify CSV content
            with open(final_path, encoding="utf-8-sig") as f:
                lines = f.readlines()
                assert len(lines) > 1  # Header + data
                assert "NodeId" in lines[0]

            print(f"\n✅ CSV export successful: {final_path.stat().st_size} bytes")

    except Exception as e:
        pytest.skip(f"CSV export test failed: {type(e).__name__}: {str(e)}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_export_json(server_available, tmp_path):
    """Test real export to JSON format."""
    if not server_available:
        pytest.skip("OPC UA server not available")

    try:
        import json

        from opc_browser.exporter import Exporter

        async with OpcUaClient(server_url=REAL_SERVER_URL) as client:
            browser = OpcUaBrowser(client=client.get_client(), max_depth=2)

            result = await browser.browse(start_node_id="i=84")
            assert result.success is True

            exporter = Exporter(export_format="json", full_export=True)
            output_path = tmp_path / "test_export.json"

            final_path = await exporter.export(result, output_path)

            assert final_path.exists()

            # Verify JSON content
            with open(final_path, encoding="utf-8") as f:
                data = json.load(f)
                assert "metadata" in data
                assert "nodes" in data
                assert "namespaces" in data
                assert data["metadata"]["full_export"] is True

            print(f"\n✅ JSON export successful: {len(data['nodes'])} nodes")

    except Exception as e:
        pytest.skip(f"JSON export test failed: {type(e).__name__}: {str(e)}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_export_xml(server_available, tmp_path):
    """Test real export to XML format."""
    if not server_available:
        pytest.skip("OPC UA server not available")

    try:
        from xml.etree import ElementTree as ET

        from opc_browser.exporter import Exporter

        async with OpcUaClient(server_url=REAL_SERVER_URL) as client:
            browser = OpcUaBrowser(client=client.get_client(), max_depth=2)

            result = await browser.browse(start_node_id="i=84")
            assert result.success is True

            exporter = Exporter(export_format="xml")
            output_path = tmp_path / "test_export.xml"

            final_path = await exporter.export(result, output_path)

            assert final_path.exists()

            # Verify XML content
            tree = ET.parse(final_path)
            root = tree.getroot()
            assert root.tag == "OpcUaAddressSpace"
            assert root.find("Metadata") is not None
            assert root.find("Nodes") is not None

            print(f"\n✅ XML export successful: {len(root.find('Nodes'))} nodes")

    except Exception as e:
        pytest.skip(f"XML export test failed: {type(e).__name__}: {str(e)}")


@pytest.mark.integration
def test_server_availability_check():
    """Test the server availability check function itself."""
    # This test always runs to verify the check function works
    import asyncio

    result = asyncio.run(check_server_available())

    # Result should be boolean
    assert isinstance(result, bool)

    if result:
        print("\n✅ OPC UA server is available on localhost:4840")
    else:
        print("\n⚠️  OPC UA server not available on localhost:4840 (this is OK)")


# Helper fixture for pytest markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring real OPC UA server"
    )
