"""Comprehensive tests for CLI module."""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from opc_browser.cli import (
    async_main,
    create_parser,
    execute_browse,
    execute_export,
    execute_generate_cert,
    main,
    setup_logging,
)
from opc_browser.models import BrowseResult


class TestSetupLogging:
    """Test logging setup."""

    def test_setup_logging_configures_logger(self):
        """Test that setup_logging configures loguru."""
        with patch("opc_browser.cli.logger") as mock_logger:
            setup_logging()
            mock_logger.remove.assert_called_once()
            mock_logger.add.assert_called_once()


class TestCreateParser:
    """Test argument parser creation."""

    def test_create_parser_returns_parser(self):
        """Test that create_parser returns ArgumentParser."""
        parser = create_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_parser_has_browse_command(self):
        """Test parser has browse subcommand."""
        parser = create_parser()
        args = parser.parse_args(["browse", "-s", "opc.tcp://localhost:4840"])
        assert args.command == "browse"
        assert args.server_url == "opc.tcp://localhost:4840"

    def test_parser_has_export_command(self):
        """Test parser has export subcommand."""
        parser = create_parser()
        args = parser.parse_args(["export", "-s", "opc.tcp://localhost:4840", "-f", "json"])
        assert args.command == "export"
        assert args.format == "json"

    def test_parser_has_generate_cert_command(self):
        """Test parser has generate-cert subcommand."""
        parser = create_parser()
        args = parser.parse_args(["generate-cert"])
        assert args.command == "generate-cert"

    def test_browse_command_all_args(self):
        """Test browse command with all arguments."""
        parser = create_parser()
        args = parser.parse_args(
            [
                "browse",
                "-s",
                "opc.tcp://localhost:4840",
                "-n",
                "ns=2;i=1000",
                "-d",
                "5",
                "--security",
                "Basic256Sha256",
                "--mode",
                "SignAndEncrypt",
                "--cert",
                "cert.pem",
                "--key",
                "key.pem",
                "-u",
                "admin",
                "-p",
                "password",
            ]
        )
        assert args.node_id == "ns=2;i=1000"
        assert args.depth == 5
        assert args.security == "Basic256Sha256"
        assert args.mode == "SignAndEncrypt"
        assert args.user == "admin"

    def test_export_command_all_args(self):
        """Test export command with all arguments."""
        parser = create_parser()
        args = parser.parse_args(
            [
                "export",
                "-s",
                "opc.tcp://localhost:4840",
                "-f",
                "xml",
                "-o",
                "output.xml",
                "--namespaces-only",
                "--include-values",
                "--full-export",
            ]
        )
        assert args.format == "xml"
        assert args.output == Path("output.xml")
        assert args.namespaces_only is True
        assert args.include_values is True
        assert args.full_export is True

    def test_generate_cert_command_all_args(self):
        """Test generate-cert command with all arguments."""
        parser = create_parser()
        args = parser.parse_args(
            [
                "generate-cert",
                "--dir",
                "certs",
                "--cn",
                "My Client",
                "--org",
                "My Org",
                "--country",
                "US",
                "--days",
                "730",
                "--uri",
                "urn:test:client",
                "--hostname",
                "host1",
                "--hostname",
                "host2",
            ]
        )
        assert args.dir == Path("certs")
        assert args.common_name == "My Client"
        assert args.organization == "My Org"
        assert args.country == "US"
        assert args.days == 730
        assert args.application_uri == "urn:test:client"
        assert args.hostnames == ["host1", "host2"]


class TestExecuteBrowse:
    """Test execute_browse function."""

    @pytest.mark.asyncio
    async def test_execute_browse_success(self):
        """Test successful browse execution."""
        args = argparse.Namespace(
            server_url="opc.tcp://localhost:4840",
            node_id="i=84",
            depth=3,
            security="None",
            mode=None,
            cert=None,
            key=None,
            user=None,
            password=None,
        )

        mock_result = BrowseResult()
        mock_result.success = True
        mock_result.total_nodes = 10

        with patch("opc_browser.cli.OpcUaClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get_client = MagicMock()
            mock_client_cls.return_value = mock_client

            with patch("opc_browser.cli.OpcUaBrowser") as mock_browser_cls:
                mock_browser = MagicMock()
                mock_browser.browse = AsyncMock(return_value=mock_result)
                mock_browser.print_tree = MagicMock()
                mock_browser_cls.return_value = mock_browser

                exit_code = await execute_browse(args)
                assert exit_code == 0
                mock_browser.print_tree.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_browse_failure(self):
        """Test browse execution with failed result."""
        args = argparse.Namespace(
            server_url="opc.tcp://localhost:4840",
            node_id="i=84",
            depth=3,
            security="None",
            mode=None,
            cert=None,
            key=None,
            user=None,
            password=None,
        )

        mock_result = BrowseResult()
        mock_result.success = False

        with patch("opc_browser.cli.OpcUaClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get_client = MagicMock()
            mock_client_cls.return_value = mock_client

            with patch("opc_browser.cli.OpcUaBrowser") as mock_browser_cls:
                mock_browser = MagicMock()
                mock_browser.browse = AsyncMock(return_value=mock_result)
                mock_browser_cls.return_value = mock_browser

                exit_code = await execute_browse(args)
                assert exit_code == 1

    @pytest.mark.asyncio
    async def test_execute_browse_keyboard_interrupt(self):
        """Test browse execution with keyboard interrupt."""
        args = argparse.Namespace(
            server_url="opc.tcp://localhost:4840",
            node_id="i=84",
            depth=3,
            security="None",
            mode=None,
            cert=None,
            key=None,
            user=None,
            password=None,
        )

        with patch("opc_browser.cli.OpcUaClient") as mock_client_cls:
            mock_client_cls.side_effect = KeyboardInterrupt()

            exit_code = await execute_browse(args)
            assert exit_code == 130

    @pytest.mark.asyncio
    async def test_execute_browse_general_exception(self):
        """Test browse with general exception."""
        args = argparse.Namespace(
            server_url="opc.tcp://localhost:4840",
            node_id="i=84",
            depth=3,
            security="None",
            mode=None,
            cert=None,
            key=None,
            user=None,
            password=None,
        )

        with patch("opc_browser.cli.OpcUaClient") as mock_client_cls:
            mock_client_cls.side_effect = RuntimeError("Unexpected error")

            exit_code = await execute_browse(args)
            assert exit_code == 1


class TestExecuteExport:
    """Test execute_export function."""

    @pytest.mark.asyncio
    async def test_execute_export_success(self):
        """Test successful export execution."""
        args = argparse.Namespace(
            server_url="opc.tcp://localhost:4840",
            node_id="i=84",
            depth=3,
            security="None",
            mode=None,
            cert=None,
            key=None,
            user=None,
            password=None,
            format="csv",
            output=None,
            namespaces_only=False,
            include_values=False,
            full_export=False,
        )

        mock_result = BrowseResult()
        mock_result.success = True
        mock_result.total_nodes = 10
        mock_result.namespaces = {0: "http://opcfoundation.org/UA/"}

        with patch("opc_browser.cli.OpcUaClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get_client = MagicMock()
            mock_client_cls.return_value = mock_client

            with patch("opc_browser.cli.OpcUaBrowser") as mock_browser_cls:
                mock_browser = MagicMock()
                mock_browser.browse = AsyncMock(return_value=mock_result)
                mock_browser_cls.return_value = mock_browser

                with patch("opc_browser.cli.Exporter") as mock_exporter_cls:
                    mock_exporter = MagicMock()
                    mock_exporter.export = AsyncMock(return_value=Path("output.csv"))
                    mock_exporter_cls.return_value = mock_exporter

                    with patch.object(Path, "stat") as mock_stat:
                        mock_stat.return_value = MagicMock(st_size=1024)

                        exit_code = await execute_export(args)
                        assert exit_code == 0

    @pytest.mark.asyncio
    async def test_execute_export_browse_failure(self):
        """Test export with failed browse."""
        args = argparse.Namespace(
            server_url="opc.tcp://localhost:4840",
            node_id="i=84",
            depth=3,
            security="None",
            mode=None,
            cert=None,
            key=None,
            user=None,
            password=None,
            format="csv",
            output=None,
            namespaces_only=False,
            include_values=False,
            full_export=False,
        )

        mock_result = BrowseResult()
        mock_result.success = False

        with patch("opc_browser.cli.OpcUaClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get_client = MagicMock()
            mock_client_cls.return_value = mock_client

            with patch("opc_browser.cli.OpcUaBrowser") as mock_browser_cls:
                mock_browser = MagicMock()
                mock_browser.browse = AsyncMock(return_value=mock_result)
                mock_browser_cls.return_value = mock_browser

                exit_code = await execute_export(args)
                assert exit_code == 1

    @pytest.mark.asyncio
    async def test_execute_export_no_nodes(self):
        """Test export with no nodes discovered."""
        args = argparse.Namespace(
            server_url="opc.tcp://localhost:4840",
            node_id="i=84",
            depth=3,
            security="None",
            mode=None,
            cert=None,
            key=None,
            user=None,
            password=None,
            format="csv",
            output=None,
            namespaces_only=False,
            include_values=False,
            full_export=False,
        )

        mock_result = BrowseResult()
        mock_result.success = True
        mock_result.total_nodes = 0

        with patch("opc_browser.cli.OpcUaClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get_client = MagicMock()
            mock_client_cls.return_value = mock_client

            with patch("opc_browser.cli.OpcUaBrowser") as mock_browser_cls:
                mock_browser = MagicMock()
                mock_browser.browse = AsyncMock(return_value=mock_result)
                mock_browser_cls.return_value = mock_browser

                exit_code = await execute_export(args)
                assert exit_code == 1

    @pytest.mark.asyncio
    async def test_execute_export_format_autodetect(self):
        """Test export format auto-detection from filename."""
        args = argparse.Namespace(
            server_url="opc.tcp://localhost:4840",
            node_id="i=84",
            depth=3,
            security="None",
            mode=None,
            cert=None,
            key=None,
            user=None,
            password=None,
            format="csv",  # default
            output=Path("output.json"),  # but output has .json extension
            namespaces_only=False,
            include_values=False,
            full_export=False,
        )

        mock_result = BrowseResult()
        mock_result.success = True
        mock_result.total_nodes = 10
        mock_result.namespaces = {0: "http://opcfoundation.org/UA/"}

        with patch("opc_browser.cli.OpcUaClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get_client = MagicMock()
            mock_client_cls.return_value = mock_client

            with patch("opc_browser.cli.OpcUaBrowser") as mock_browser_cls:
                mock_browser = MagicMock()
                mock_browser.browse = AsyncMock(return_value=mock_result)
                mock_browser_cls.return_value = mock_browser

                with patch("opc_browser.cli.Exporter") as mock_exporter_cls:
                    mock_exporter = MagicMock()
                    mock_exporter.export = AsyncMock(return_value=Path("output.json"))
                    mock_exporter_cls.return_value = mock_exporter
                    # Mock get_supported_formats to allow autodetect
                    mock_exporter_cls.get_supported_formats = MagicMock(
                        return_value=["csv", "json", "xml"]
                    )

                    with patch.object(Path, "stat") as mock_stat:
                        mock_stat.return_value = MagicMock(st_size=2048)

                        exit_code = await execute_export(args)
                        # Should auto-detect json from extension
                        mock_exporter_cls.assert_called_with(
                            export_format="json", full_export=False
                        )
                        assert exit_code == 0

    @pytest.mark.asyncio
    async def test_execute_export_exception(self):
        """Test export with exception during export."""
        args = argparse.Namespace(
            server_url="opc.tcp://localhost:4840",
            node_id="i=84",
            depth=3,
            security="None",
            mode=None,
            cert=None,
            key=None,
            user=None,
            password=None,
            format="csv",
            output=None,
            namespaces_only=False,
            include_values=False,
            full_export=False,
        )

        mock_result = BrowseResult()
        mock_result.success = True
        mock_result.total_nodes = 10
        mock_result.namespaces = {0: "http://opcfoundation.org/UA/"}

        with patch("opc_browser.cli.OpcUaClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get_client = MagicMock()
            mock_client_cls.return_value = mock_client

            with patch("opc_browser.cli.OpcUaBrowser") as mock_browser_cls:
                mock_browser = MagicMock()
                mock_browser.browse = AsyncMock(return_value=mock_result)
                mock_browser_cls.return_value = mock_browser

                with patch("opc_browser.cli.Exporter") as mock_exporter_cls:
                    mock_exporter = MagicMock()
                    mock_exporter.export = AsyncMock(side_effect=Exception("Export failed"))
                    mock_exporter_cls.return_value = mock_exporter

                    exit_code = await execute_export(args)
                    assert exit_code == 1

    @pytest.mark.asyncio
    async def test_execute_export_value_error(self):
        """Test export with ValueError during export."""
        args = argparse.Namespace(
            server_url="opc.tcp://localhost:4840",
            node_id="i=84",
            depth=3,
            security="None",
            mode=None,
            cert=None,
            key=None,
            user=None,
            password=None,
            format="csv",
            output=None,
            namespaces_only=False,
            include_values=False,
            full_export=False,
        )

        mock_result = BrowseResult()
        mock_result.success = True
        mock_result.total_nodes = 10
        mock_result.namespaces = {0: "http://opcfoundation.org/UA/"}

        with patch("opc_browser.cli.OpcUaClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get_client = MagicMock()
            mock_client_cls.return_value = mock_client

            with patch("opc_browser.cli.OpcUaBrowser") as mock_browser_cls:
                mock_browser = MagicMock()
                mock_browser.browse = AsyncMock(return_value=mock_result)
                mock_browser_cls.return_value = mock_browser

                with patch("opc_browser.cli.Exporter") as mock_exporter_cls:
                    mock_exporter = MagicMock()
                    mock_exporter.export = AsyncMock(side_effect=ValueError("Invalid data"))
                    mock_exporter_cls.return_value = mock_exporter

                    exit_code = await execute_export(args)
                    assert exit_code == 1

    @pytest.mark.asyncio
    async def test_execute_export_os_error(self):
        """Test export with OSError during export."""
        args = argparse.Namespace(
            server_url="opc.tcp://localhost:4840",
            node_id="i=84",
            depth=3,
            security="None",
            mode=None,
            cert=None,
            key=None,
            user=None,
            password=None,
            format="csv",
            output=None,
            namespaces_only=False,
            include_values=False,
            full_export=False,
        )

        mock_result = BrowseResult()
        mock_result.success = True
        mock_result.total_nodes = 10
        mock_result.namespaces = {0: "http://opcfoundation.org/UA/"}

        with patch("opc_browser.cli.OpcUaClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get_client = MagicMock()
            mock_client_cls.return_value = mock_client

            with patch("opc_browser.cli.OpcUaBrowser") as mock_browser_cls:
                mock_browser = MagicMock()
                mock_browser.browse = AsyncMock(return_value=mock_result)
                mock_browser_cls.return_value = mock_browser

                with patch("opc_browser.cli.Exporter") as mock_exporter_cls:
                    mock_exporter = MagicMock()
                    mock_exporter.export = AsyncMock(side_effect=OSError("Disk full"))
                    mock_exporter_cls.return_value = mock_exporter

                    exit_code = await execute_export(args)
                    assert exit_code == 1

    @pytest.mark.asyncio
    async def test_execute_export_keyboard_interrupt(self):
        """Test export with keyboard interrupt."""
        args = argparse.Namespace(
            server_url="opc.tcp://localhost:4840",
            node_id="i=84",
            depth=3,
            security="None",
            mode=None,
            cert=None,
            key=None,
            user=None,
            password=None,
            format="csv",
            output=None,
            namespaces_only=False,
            include_values=False,
            full_export=False,
        )

        with patch("opc_browser.cli.OpcUaClient") as mock_client_cls:
            mock_client_cls.side_effect = KeyboardInterrupt()

            exit_code = await execute_export(args)
            assert exit_code == 130

    @pytest.mark.asyncio
    async def test_execute_export_general_exception(self):
        """Test export with general exception."""
        args = argparse.Namespace(
            server_url="opc.tcp://localhost:4840",
            node_id="i=84",
            depth=3,
            security="None",
            mode=None,
            cert=None,
            key=None,
            user=None,
            password=None,
            format="csv",
            output=None,
            namespaces_only=False,
            include_values=False,
            full_export=False,
        )

        with patch("opc_browser.cli.OpcUaClient") as mock_client_cls:
            mock_client_cls.side_effect = RuntimeError("Unexpected error")

            exit_code = await execute_export(args)
            assert exit_code == 1

    @pytest.mark.asyncio
    async def test_execute_export_format_mismatch_warning(self):
        """Test export with format mismatch warning."""
        args = argparse.Namespace(
            server_url="opc.tcp://localhost:4840",
            node_id="i=84",
            depth=3,
            security="None",
            mode=None,
            cert=None,
            key=None,
            user=None,
            password=None,
            format="json",  # Explicitly set
            output=Path("output.xml"),  # Mismatched extension
            namespaces_only=False,
            include_values=False,
            full_export=False,
        )

        mock_result = BrowseResult()
        mock_result.success = True
        mock_result.total_nodes = 10
        mock_result.namespaces = {0: "http://opcfoundation.org/UA/"}

        with patch("opc_browser.cli.OpcUaClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get_client = MagicMock()
            mock_client_cls.return_value = mock_client

            with patch("opc_browser.cli.OpcUaBrowser") as mock_browser_cls:
                mock_browser = MagicMock()
                mock_browser.browse = AsyncMock(return_value=mock_result)
                mock_browser_cls.return_value = mock_browser

                with patch("opc_browser.cli.Exporter") as mock_exporter_cls:
                    mock_exporter = MagicMock()
                    mock_exporter.export = AsyncMock(return_value=Path("output.json"))
                    mock_exporter_cls.return_value = mock_exporter

                    with patch.object(Path, "stat") as mock_stat:
                        mock_stat.return_value = MagicMock(st_size=2048)

                        exit_code = await execute_export(args)
                        # Should use explicitly set format (json)
                        mock_exporter_cls.assert_called_with(
                            export_format="json", full_export=False
                        )
                        assert exit_code == 0


class TestExecuteGenerateCert:
    """Test execute_generate_cert function."""

    @pytest.mark.asyncio
    async def test_execute_generate_cert_success(self):
        """Test successful certificate generation."""
        args = argparse.Namespace(
            dir=Path("certificates"),
            common_name="Test Client",
            organization="Test Org",
            country="US",
            days=365,
            application_uri="urn:test:client",
            hostnames=None,
        )

        with patch("opc_browser.cli.generate_self_signed_cert") as mock_gen:
            exit_code = await execute_generate_cert(args)
            assert exit_code == 0
            mock_gen.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_generate_cert_with_hostnames(self):
        """Test certificate generation with custom hostnames."""
        args = argparse.Namespace(
            dir=Path("certificates"),
            common_name="Test Client",
            organization="Test Org",
            country="US",
            days=365,
            application_uri="urn:test:client",
            hostnames=["host1", "host2"],
        )

        with patch("opc_browser.cli.generate_self_signed_cert") as mock_gen:
            exit_code = await execute_generate_cert(args)
            assert exit_code == 0
            call_args = mock_gen.call_args[1]
            assert call_args["hostnames"] == ["host1", "host2"]

    @pytest.mark.asyncio
    async def test_execute_generate_cert_failure(self):
        """Test certificate generation failure."""
        args = argparse.Namespace(
            dir=Path("certificates"),
            common_name="Test Client",
            organization="Test Org",
            country="US",
            days=365,
            application_uri="urn:test:client",
            hostnames=None,
        )

        with patch("opc_browser.cli.generate_self_signed_cert") as mock_gen:
            mock_gen.side_effect = Exception("Generation failed")

            exit_code = await execute_generate_cert(args)
            assert exit_code == 1


class TestAsyncMain:
    """Test async_main function."""

    @pytest.mark.asyncio
    async def test_async_main_browse(self):
        """Test async_main with browse command."""
        with patch("opc_browser.cli.create_parser") as mock_parser:
            mock_args = MagicMock()
            mock_args.command = "browse"
            mock_parser.return_value.parse_args.return_value = mock_args

            with patch("opc_browser.cli.execute_browse") as mock_execute:
                mock_execute.return_value = 0

                exit_code = await async_main()
                assert exit_code == 0
                mock_execute.assert_called_once_with(mock_args)

    @pytest.mark.asyncio
    async def test_async_main_export(self):
        """Test async_main with export command."""
        with patch("opc_browser.cli.create_parser") as mock_parser:
            mock_args = MagicMock()
            mock_args.command = "export"
            mock_parser.return_value.parse_args.return_value = mock_args

            with patch("opc_browser.cli.execute_export") as mock_execute:
                mock_execute.return_value = 0

                exit_code = await async_main()
                assert exit_code == 0
                mock_execute.assert_called_once_with(mock_args)

    @pytest.mark.asyncio
    async def test_async_main_generate_cert(self):
        """Test async_main with generate-cert command."""
        with patch("opc_browser.cli.create_parser") as mock_parser:
            mock_args = MagicMock()
            mock_args.command = "generate-cert"
            mock_parser.return_value.parse_args.return_value = mock_args

            with patch("opc_browser.cli.execute_generate_cert") as mock_execute:
                mock_execute.return_value = 0

                exit_code = await async_main()
                assert exit_code == 0
                mock_execute.assert_called_once_with(mock_args)

    @pytest.mark.asyncio
    async def test_async_main_unknown_command(self):
        """Test async_main with unknown command."""
        with patch("opc_browser.cli.create_parser") as mock_parser:
            mock_args = MagicMock()
            mock_args.command = "unknown"
            mock_parser.return_value.parse_args.return_value = mock_args

            exit_code = await async_main()
            assert exit_code == 1


class TestMain:
    """Test main entry point."""

    def test_main_success(self):
        """Test main with successful execution."""
        with patch("opc_browser.cli.asyncio.run") as mock_run:
            mock_run.return_value = 0

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0

    def test_main_keyboard_interrupt(self):
        """Test main with keyboard interrupt."""
        with patch("opc_browser.cli.asyncio.run") as mock_run:
            mock_run.side_effect = KeyboardInterrupt()

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 130

    def test_main_exception(self):
        """Test main with unexpected exception."""
        with patch("opc_browser.cli.asyncio.run") as mock_run:
            mock_run.side_effect = Exception("Unexpected error")

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1
