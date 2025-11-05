from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from opc_browser.client import (
    ConnectionError,
    OpcUaClient,
    SecurityConfigurationError,
)


@pytest.fixture
def dummy_client():
    # Patch asyncua.Client to avoid real network
    with patch("opc_browser.client.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        yield mock_client


def test_init_sets_attributes(dummy_client):
    c = OpcUaClient(
        server_url="opc.tcp://localhost:4840",
        username="user",
        password="pw",
        security_policy="None",
        security_mode=None,
        certificate_path=Path("cert.pem"),
        private_key_path=Path("key.pem"),
    )
    assert c.server_url == "opc.tcp://localhost:4840"
    assert c.username == "user"
    assert c.password == "pw"
    assert c.security_policy == "None"
    assert c.security_mode is None
    assert c.certificate_path == Path("cert.pem")
    assert c.private_key_path == Path("key.pem")
    assert hasattr(c, "client")


@pytest.mark.asyncio
async def test_aenter_and_aexit_calls_connect_disconnect(dummy_client):
    c = OpcUaClient("opc.tcp://localhost:4840")
    c.connect = AsyncMock()
    c.disconnect = AsyncMock()
    async with c:
        c.connect.assert_awaited_once()
    c.disconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_connect_no_security(dummy_client):
    c = OpcUaClient("opc.tcp://localhost:4840")
    c.client.connect = AsyncMock()
    server_node = MagicMock()
    server_node.read_browse_name = AsyncMock(return_value=MagicMock(Name="Server"))
    c.client.get_server_node = MagicMock(return_value=server_node)
    c.client.get_node = MagicMock(side_effect=Exception("fail"))
    await c.connect()


@pytest.mark.asyncio
async def test_connect_with_security_configured(tmp_path, dummy_client):
    cert = tmp_path / "cert.pem"
    key = tmp_path / "key.pem"
    cert.write_text("CERT")
    key.write_text("KEY")
    c = OpcUaClient(
        "opc.tcp://localhost:4840",
        security_policy="Basic256Sha256",
        security_mode="SignAndEncrypt",
        certificate_path=cert,
        private_key_path=key,
    )
    c.client.set_security = AsyncMock()
    c.client.connect = AsyncMock()
    server_node = MagicMock()
    server_node.read_browse_name = AsyncMock(return_value=MagicMock(Name="Server"))
    c.client.get_server_node = MagicMock(return_value=server_node)
    c.client.get_node = MagicMock(side_effect=Exception("fail"))
    await c.connect()
    c.client.set_security.assert_awaited()


@pytest.mark.asyncio
async def test_connect_with_username_password(dummy_client):
    c = OpcUaClient("opc.tcp://localhost:4840", username="u", password="p")
    c.client.set_user = MagicMock()
    c.client.set_password = MagicMock()
    c.client.connect = AsyncMock()
    server_node = MagicMock()
    server_node.read_browse_name = AsyncMock(return_value=MagicMock(Name="Server"))
    c.client.get_server_node = MagicMock(return_value=server_node)
    c.client.get_node = MagicMock(side_effect=Exception("fail"))
    await c.connect()
    c.client.set_user.assert_called_with("u")
    c.client.set_password.assert_called_with("p")


@pytest.mark.asyncio
async def test_connect_ua_status_code_error(dummy_client):
    from asyncua import ua

    # Create a mock UaStatusCodeError without actually instantiating it
    # to avoid asyncua's internal status code conversion
    class MockUaStatusCodeError(Exception):
        """Mock UaStatusCodeError that behaves like the real one for our test."""

        def __init__(self):
            self.code = MagicMock()
            self.code.name = "BadIdentityTokenRejected"

        def __str__(self):
            return "BadIdentityTokenRejected"

    # Patch isinstance to make our mock pass the isinstance check in client.py
    original_isinstance = isinstance

    def patched_isinstance(obj, class_or_tuple):
        if class_or_tuple == ua.UaStatusCodeError and type(obj).__name__ == "MockUaStatusCodeError":
            return True
        return original_isinstance(obj, class_or_tuple)

    import builtins

    builtins.isinstance = patched_isinstance

    try:
        c = OpcUaClient("opc.tcp://localhost:4840")
        c.client.connect = AsyncMock(side_effect=MockUaStatusCodeError())

        with pytest.raises(ConnectionError) as e:
            await c.connect()

        # Now check for the expected error message
        assert "BadIdentityTokenRejected" in str(e.value)
    finally:
        # Restore original isinstance
        builtins.isinstance = original_isinstance


@pytest.mark.asyncio
async def test_connect_generic_exception(dummy_client):
    c = OpcUaClient("opc.tcp://localhost:4840")
    c.client.connect = AsyncMock(side_effect=Exception("fail"))
    with pytest.raises(ConnectionError) as e:
        await c.connect()
    assert "Connection failed" in str(e.value)


@pytest.mark.asyncio
async def test_configure_security_errors(tmp_path, dummy_client):
    c = OpcUaClient("opc.tcp://localhost:4840", security_policy="Invalid")
    with pytest.raises(SecurityConfigurationError):
        await c._configure_security()
    c = OpcUaClient("opc.tcp://localhost:4840", security_policy="Basic256Sha256")
    with pytest.raises(SecurityConfigurationError):
        await c._configure_security()
    c = OpcUaClient(
        "opc.tcp://localhost:4840", security_policy="Basic256Sha256", security_mode="Invalid"
    )
    with pytest.raises(SecurityConfigurationError):
        await c._configure_security()
    c = OpcUaClient(
        "opc.tcp://localhost:4840", security_policy="Basic256Sha256", security_mode="Sign"
    )
    with pytest.raises(SecurityConfigurationError):
        await c._configure_security()
    cert = tmp_path / "cert.pem"
    key = tmp_path / "key.pem"
    c = OpcUaClient(
        "opc.tcp://localhost:4840",
        security_policy="Basic256Sha256",
        security_mode="Sign",
        certificate_path=cert,
        private_key_path=key,
    )
    with pytest.raises(SecurityConfigurationError):
        await c._configure_security()
    cert.write_text("CERT")
    c = OpcUaClient(
        "opc.tcp://localhost:4840",
        security_policy="Basic256Sha256",
        security_mode="Sign",
        certificate_path=cert,
        private_key_path=key,
    )
    with pytest.raises(SecurityConfigurationError):
        await c._configure_security()
    key.write_text("KEY")
    c = OpcUaClient(
        "opc.tcp://localhost:4840",
        security_policy="Basic256Sha256",
        security_mode="Sign",
        certificate_path=cert,
        private_key_path=key,
    )
    c.client.set_security = AsyncMock(side_effect=Exception("fail"))
    with pytest.raises(SecurityConfigurationError):
        await c._configure_security()


@pytest.mark.asyncio
async def test_disconnect_success(dummy_client):
    c = OpcUaClient("opc.tcp://localhost:4840")
    c.client.disconnect = AsyncMock()
    await c.disconnect()
    c.client.disconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_disconnect_exception(dummy_client):
    c = OpcUaClient("opc.tcp://localhost:4840")
    c.client.disconnect = AsyncMock(side_effect=Exception("fail"))
    await c.disconnect()  # Should not raise


def test_get_client(dummy_client):
    c = OpcUaClient("opc.tcp://localhost:4840")
    assert c.get_client() is c.client


def test_get_supported_policies_and_modes():
    policies = OpcUaClient.get_supported_policies()
    assert "None" in policies
    assert "Basic256Sha256" in policies
    modes = OpcUaClient.get_supported_modes()
    assert "Sign" in modes
    assert "SignAndEncrypt" in modes


def test_format_ua_error_all_branches():
    c = OpcUaClient("opc.tcp://localhost:4840")

    # With .code.name
    class DummyError:
        def __init__(self):
            self.code = type("C", (), {"name": "BadIdentityTokenRejected"})()

        def __str__(self):
            return "BadIdentityTokenRejected"

    msg = c._format_ua_error(DummyError())
    assert "Hint" in msg

    # With .code as int
    class DummyError2:
        def __init__(self):
            self.code = 0x80000000

        def __str__(self):
            return "BadUnexpectedError"

    msg = c._format_ua_error(DummyError2())
    assert "BadUnexpectedError" in msg

    # With no .code
    class DummyError3:
        def __str__(self):
            return "BadNodeIdUnknown"

    msg = c._format_ua_error(DummyError3())
    assert "BadNodeIdUnknown" in msg

    # Exception in code access
    class DummyError4:
        def __init__(self):
            def fail():
                raise Exception("fail")

            self.code = property(fail)

        def __str__(self):
            return "BadNodeIdUnknown"

    msg = c._format_ua_error(DummyError3())
    assert "BadNodeIdUnknown" in msg
