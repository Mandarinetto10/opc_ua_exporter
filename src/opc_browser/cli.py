"""Command Line Interface for OPC UA Browser/Exporter.

Main entry point for the application. Provides commands for browsing OPC UA
address spaces, exporting node data to multiple formats (CSV, JSON, XML),
and generating self-signed certificates for secure connections.
"""

from __future__ import annotations

import argparse
import asyncio
import socket
import sys
from pathlib import Path
from urllib.parse import ParseResult, urlparse

from loguru import logger

from .browser import OpcUaBrowser
from .client import OpcUaClient
from .exporter import Exporter
from .generate_cert import generate_self_signed_cert


def setup_logging() -> None:
    """Configure loguru logger with custom format and level.

    Removes default handler and adds stderr output with timestamp,
    level, and colored output for better readability.
    """
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
        colorize=True,
    )


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser with all commands and options.

    Returns:
        Configured ArgumentParser with browse, export, and generate-cert subcommands.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="OPC UA Browser and Exporter - Advanced CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Browse with default settings (no security)
  %(prog)s browse -s opc.tcp://localhost:4840

  # Browse with username/password (no encryption)
  %(prog)s browse -s opc.tcp://server:4840 -u admin -p password

  # Browse with security policy and certificates
  %(prog)s browse -s opc.tcp://server:4840 --security Basic256Sha256 --mode SignAndEncrypt --cert client_cert.pem --key client_key.pem -u admin -p password

  # Export to JSON with values and security
  %(prog)s export -s opc.tcp://localhost:4840 --security Aes128_Sha256_RsaOaep --mode Sign --cert cert.pem --key key.pem -f json --include-values

  # Export to CSV with namespaces only
  %(prog)s export -s opc.tcp://localhost:4840 -f csv --namespaces-only

  # Generate self-signed certificate with default settings
  %(prog)s generate-cert --dir certificates

  # Generate self-signed certificate with custom settings
  %(prog)s generate-cert --dir certificates --cn "My OPC UA Client" --org "My Company" --days 730 --key-size 2048 --validity 365
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.required = True

    def add_common_arguments(subparser: argparse.ArgumentParser) -> None:
        """Add common arguments shared by browse and export commands.

        Args:
            subparser: Subparser to add arguments to.
        """
        subparser.add_argument(
            "--server-url",
            "-s",
            required=True,
            help="OPC UA server endpoint URL (e.g., opc.tcp://localhost:4840)",
        )
        subparser.add_argument(
            "--node-id",
            "-n",
            default="i=84",
            help="Starting node ID for browsing (default: i=84 - RootFolder)",
        )
        subparser.add_argument(
            "--depth",
            "-d",
            type=int,
            default=3,
            help="Maximum depth for recursive browsing (default: 3)",
        )

        security_group = subparser.add_argument_group("Security Options")
        security_group.add_argument(
            "--security",
            "-sec",
            default="None",
            choices=OpcUaClient.get_supported_policies(),
            help="Security policy (default: None)",
        )
        security_group.add_argument(
            "--mode",
            "-m",
            choices=OpcUaClient.get_supported_modes(),
            help="Security mode (required if --security is not None): Sign, SignAndEncrypt",
        )
        security_group.add_argument(
            "--cert",
            type=Path,
            help="Path to client certificate file (required for non-None security)",
        )
        security_group.add_argument(
            "--key",
            type=Path,
            help="Path to client private key file (required for non-None security)",
        )

        auth_group = subparser.add_argument_group("Authentication Options")
        auth_group.add_argument(
            "--user",
            "-u",
            help="Username for authentication",
        )
        auth_group.add_argument(
            "--password",
            "-p",
            help="Password for authentication",
        )

    browse_parser = subparsers.add_parser(
        "browse",
        help="Browse OPC UA address space and display tree structure",
    )
    add_common_arguments(browse_parser)

    export_parser = subparsers.add_parser(
        "export",
        help="Export OPC UA address space to file",
    )
    add_common_arguments(export_parser)

    export_parser.add_argument(
        "--format",
        "-f",
        default="csv",
        choices=Exporter.get_supported_formats(),
        help="Export format (default: csv)",
    )
    export_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file path (default: export/opcua_export_<timestamp>.<format>)",
    )
    export_parser.add_argument(
        "--namespaces-only",
        action="store_true",
        help="Export only namespace-related nodes",
    )
    export_parser.add_argument(
        "--include-values",
        action="store_true",
        help="Include current values for Variable nodes",
    )
    export_parser.add_argument(
        "--namespace-filter",
        type=int,
        metavar="INDEX",
        help="Export only nodes from specific namespace index (e.g., --namespace-filter 2)",
    )

    cert_parser = subparsers.add_parser(
        "generate-cert",
        help="Generate a self-signed client certificate for OPC UA connections",
    )
    cert_parser.add_argument(
        "--dir",
        type=Path,
        default=Path("certificates"),
        help="Directory to save certificates (default: certificates)",
    )
    cert_parser.add_argument(
        "--cn",
        "--common-name",
        dest="common_name",
        default="OPC UA Python Client",
        help="Common Name for certificate (default: OPC UA Python Client)",
    )
    cert_parser.add_argument(
        "--org",
        "--organization",
        dest="organization",
        default="My Organization",
        help="Organization name (default: My Organization)",
    )
    cert_parser.add_argument(
        "--country",
        default="IT",
        help="Country code (2 letters, default: IT)",
    )
    cert_parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Certificate validity in days (default: 365)",
    )
    cert_parser.add_argument(
        "--uri",
        "--application-uri",
        dest="application_uri",
        default="urn:example.org:FreeOpcUa:opcua-asyncio",
        help="OPC UA Application URI (default: urn:example.org:FreeOpcUa:opcua-asyncio)",
    )
    cert_parser.add_argument(
        "--hostname",
        action="append",
        dest="hostnames",
        help="Hostname/DNS name to include in certificate (can be used multiple times, "
             "default: localhost + local hostname)",
    )

    return parser


async def execute_browse(args: argparse.Namespace) -> int:
    """Execute browse command to display OPC UA address space tree.

    Establishes connection to OPC UA server, performs recursive browsing
    of the address space, and displays results as a formatted tree.

    Args:
        args: Parsed command line arguments containing connection parameters,
            security settings, authentication credentials, and browse options.

    Returns:
        Exit code: 0 for success, 1 for error, 130 for user cancellation.

    Examples:
        Basic browse:
            args.server_url = "opc.tcp://localhost:4840"
            args.node_id = "i=84"
            args.depth = 3

        Secure browse:
            args.security = "Basic256Sha256"
            args.mode = "SignAndEncrypt"
            args.cert = Path("client_cert.pem")
            args.key = Path("client_key.pem")
    """
    try:
        parsed_url: ParseResult = urlparse(args.server_url)
        server_hostname: str = parsed_url.hostname or "unknown"
        port: int = parsed_url.port or 4840
    except Exception:
        server_hostname = "unknown"
        port = 4840

    client_hostname: str = socket.gethostname()

    logger.info("=" * 80)
    logger.info("BROWSE OPERATION PARAMETERS")
    logger.info("=" * 80)
    logger.info(f"Server URL:      {args.server_url}")
    logger.info(f"Server Hostname: {server_hostname}")
    logger.info(f"Server Port:     {port}")
    logger.info(f"Client Hostname: {client_hostname}")
    logger.info(f"Start Node:      {args.node_id}")
    logger.info(f"Max Depth:       {args.depth}")
    logger.info(f"Security Policy: {args.security}")
    if args.security != "None":
        logger.info(f"Security Mode:   {args.mode}")
        logger.info(f"Certificate:     {args.cert}")
        logger.info(f"Private Key:     {args.key}")
    if args.user:
        logger.info(f"Username:        {args.user}")
        logger.info(
            f"Password:        {'*' * len(args.password) if args.password else 'Not set'}"
        )
    logger.info("=" * 80)

    try:
        async with OpcUaClient(
            server_url=args.server_url,
            username=args.user,
            password=args.password,
            security_policy=args.security,
            security_mode=args.mode,
            certificate_path=args.cert,
            private_key_path=args.key,
        ) as client:
            browser: OpcUaBrowser = OpcUaBrowser(
                client=client.get_client(),
                max_depth=args.depth,
                include_values=False,
                namespaces_only=False,
            )

            result = await browser.browse(start_node_id=args.node_id)

            if result.success:
                browser.print_tree(result)
                return 0
            else:
                return 1

    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        return 130
    except Exception:
        return 1


async def execute_export(args: argparse.Namespace) -> int:
    """Execute export command to save OPC UA address space to file.

    Establishes connection to OPC UA server, performs recursive browsing,
    and exports nodes to specified format (CSV/JSON/XML).

    Args:
        args: Parsed command line arguments containing connection parameters,
            security settings, authentication credentials, export format,
            and output file path.

    Returns:
        Exit code: 0 for success, 1 for error, 130 for user cancellation.

    Examples:
        CSV export with values:
            args.format = "csv"
            args.output = Path("export.csv")
            args.include_values = True

        JSON export with security:
            args.format = "json"
            args.security = "Basic256Sha256"
            args.mode = "SignAndEncrypt"
    """
    try:
        parsed_url: ParseResult = urlparse(args.server_url)
        server_hostname: str = parsed_url.hostname or "unknown"
        port: int = parsed_url.port or 4840
    except Exception:
        server_hostname = "unknown"
        port = 4840

    client_hostname: str = socket.gethostname()

    # Smart format/output handling
    export_format: str = args.format
    output_path: Path | None = args.output

    # Deduce format from output filename if not explicitly specified
    if output_path and export_format == "csv":  # csv is the default
        file_extension = output_path.suffix.lstrip('.').lower()
        if file_extension in Exporter.get_supported_formats():
            # User specified output with extension but no --format
            # Use extension as format
            export_format = file_extension
            logger.debug(f"Format auto-detected from output filename: {export_format}")
        elif file_extension and file_extension not in Exporter.get_supported_formats():
            # User specified output with unsupported extension
            logger.error(
                f"❌ Unsupported file extension '.{file_extension}' in output path.\n"
                f"   Supported formats: {', '.join(Exporter.get_supported_formats())}\n"
                f"   Either:\n"
                f"   - Change extension to one of: {', '.join('.' + f for f in Exporter.get_supported_formats())}\n"
                f"   - Use --format to specify format explicitly"
            )
            return 1

    # Verify format/output extension consistency if both specified
    if output_path and args.format != "csv":  # User explicitly set --format
        file_extension = output_path.suffix.lstrip('.').lower()
        if file_extension and file_extension != export_format:
            logger.warning(
                f"⚠️  Format mismatch detected:\n"
                f"   --format={export_format} but output extension is '.{file_extension}'\n"
                f"   Using --format={export_format} (will override extension)"
            )
            # Fix extension to match format
            output_path = output_path.with_suffix(f".{export_format}")
            logger.info(f"   Corrected output path to: {output_path}")

    logger.info("=" * 80)
    logger.info("EXPORT OPERATION PARAMETERS")
    logger.info("=" * 80)
    logger.info(f"Server URL:       {args.server_url}")
    logger.info(f"Server Hostname:  {server_hostname}")
    logger.info(f"Server Port:      {port}")
    logger.info(f"Client Hostname:  {client_hostname}")
    logger.info(f"Start Node:       {args.node_id}")
    logger.info(f"Max Depth:        {args.depth}")
    logger.info(f"Export Format:    {export_format.upper()}")
    logger.info(f"Output File:      {output_path if output_path else 'Auto-generated'}")
    logger.info(f"Include Values:   {args.include_values}")
    logger.info(f"Namespaces Only:  {args.namespaces_only}")
    if hasattr(args, 'namespace_filter') and args.namespace_filter is not None:
        logger.info(f"Namespace Filter: {args.namespace_filter}")
    logger.info(f"Security Policy:  {args.security}")
    if args.security != "None":
        logger.info(f"Security Mode:    {args.mode}")
        logger.info(f"Certificate:      {args.cert}")
        logger.info(f"Private Key:      {args.key}")
    if args.user:
        logger.info(f"Username:         {args.user}")
        logger.info(
            f"Password:         {'*' * len(args.password) if args.password else 'Not set'}"
        )
    logger.info("=" * 80)

    try:
        async with OpcUaClient(
            server_url=args.server_url,
            username=args.user,
            password=args.password,
            security_policy=args.security,
            security_mode=args.mode,
            certificate_path=args.cert,
            private_key_path=args.key,
        ) as client:
            namespace_filter = getattr(args, 'namespace_filter', None)

            browser: OpcUaBrowser = OpcUaBrowser(
                client=client.get_client(),
                max_depth=args.depth,
                include_values=args.include_values,
                namespaces_only=args.namespaces_only,
                namespace_filter=namespace_filter,
            )

            logger.info("Starting address space browse...")
            result = await browser.browse(start_node_id=args.node_id)

            if not result.success:
                logger.error(f"❌ Browse failed: {result.error_message}")
                return 1

            if result.total_nodes == 0:
                logger.warning("⚠️  No nodes discovered - nothing to export")
                return 1

            logger.info(f"Browse completed: {result.total_nodes} nodes discovered")
            logger.info(f"Initializing {export_format.upper()} exporter...")

            try:
                exporter: Exporter = Exporter(export_format=export_format)
                final_output_path: Path = await exporter.export(result, output_path)

                file_size = final_output_path.stat().st_size

                logger.success("=" * 80)
                logger.success("✅ Export Completed Successfully!")
                logger.success("=" * 80)
                logger.success(f"Output File:      {final_output_path.absolute()}")
                logger.success(f"Format:           {export_format.upper()}")
                logger.success(f"File Size:        {file_size:,} bytes ({file_size / 1024:.2f} KB)")
                logger.success(f"Nodes Exported:   {result.total_nodes}")
                logger.success(f"Max Depth:        {result.max_depth_reached}")
                logger.success(f"Namespaces:       {len(result.namespaces)}")
                logger.success("=" * 80)

                return 0

            except ValueError as e:
                logger.error(f"❌ Export validation failed: {str(e)}")
                return 1
            except OSError as e:
                logger.error(f"❌ Export I/O error: {str(e)}")
                return 1
            except Exception as e:
                logger.error(f"❌ Export failed: {type(e).__name__}: {str(e)}")
                return 1

    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"❌ Operation failed: {type(e).__name__}: {str(e)}")
        return 1


async def execute_generate_cert(args: argparse.Namespace) -> int:
    """Execute generate-cert command to create self-signed OPC UA certificates.

    Generates a self-signed X.509 certificate and private key suitable
    for OPC UA client authentication with configurable parameters.

    Args:
        args: Parsed command line arguments containing certificate parameters
            such as common name, organization, validity period, and hostnames.

    Returns:
        Exit code: 0 for success, 1 for error.

    Examples:
        Basic certificate generation:
            args.dir = Path("certificates")
            args.common_name = "OPC UA Client"
            args.days = 365

        Custom certificate with multiple hostnames:
            args.hostnames = ["server1.local", "192.168.1.100"]
            args.application_uri = "urn:mycompany:opcua:client"
    """
    logger.info("=" * 80)
    logger.info("CERTIFICATE GENERATION PARAMETERS")
    logger.info("=" * 80)
    logger.info(f"Output Directory: {args.dir}")
    logger.info(f"Common Name:      {args.common_name}")
    logger.info(f"Organization:     {args.organization}")
    logger.info(f"Country:          {args.country}")
    logger.info(f"Validity Days:    {args.days}")
    logger.info(f"Application URI:  {args.application_uri}")

    if not args.hostnames:
        local_hostname: str = socket.gethostname()
        hostnames: list[str] = ["localhost", local_hostname]
        logger.info(f"Hostnames:        {', '.join(hostnames)} (auto-detected)")
    else:
        hostnames: list[str] = args.hostnames
        logger.info(f"Hostnames:        {', '.join(hostnames)}")

    logger.info("=" * 80)

    try:
        generate_self_signed_cert(
            cert_dir=args.dir,
            common_name=args.common_name,
            organization=args.organization,
            country=args.country,
            validity_days=args.days,
            application_uri=args.application_uri,
            hostnames=hostnames,
        )
        return 0
    except Exception:
        return 1


async def async_main() -> int:
    """Async main function that dispatches to appropriate command handler.

    Parses command-line arguments and routes to browse, export, or
    generate-cert command handlers.

    Returns:
        Exit code from command handler.
    """
    setup_logging()

    parser: argparse.ArgumentParser = create_parser()
    args: argparse.Namespace = parser.parse_args()

    if args.command == "browse":
        return await execute_browse(args)
    elif args.command == "export":
        return await execute_export(args)
    elif args.command == "generate-cert":
        return await execute_generate_cert(args)
    else:
        logger.error(f"Unknown command: {args.command}")
        return 1


def main() -> None:
    """Main entry point for CLI application.

    Handles async execution, keyboard interrupts, and exit codes.
    Sets up event loop and runs async_main().

    Raises:
        SystemExit: Always exits with appropriate code.
    """
    try:
        exit_code: int = asyncio.run(async_main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
