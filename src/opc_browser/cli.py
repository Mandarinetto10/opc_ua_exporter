"""
Command Line Interface for OPC UA Browser/Exporter.
Main entry point for the application.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from loguru import logger
import socket
from urllib.parse import urlparse

from .client import OpcUaClient
from .browser import OpcUaBrowser
from .exporter import Exporter
from .models import BrowseResult


def setup_logging() -> None:
    """Configure loguru logger."""
    logger.remove()  # Remove default handler
    
    # Add custom handler with format
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
        colorize=True,
    )


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure argument parser.
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
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
        """,
    )
    
    # Create subparsers for browse and export commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.required = True
    
    # Common arguments for both commands
    def add_common_arguments(subparser: argparse.ArgumentParser) -> None:
        """Add common arguments to a subparser."""
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
        
        # Security configuration
        security_group = subparser.add_argument_group('Security Options')
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
        
        # Authentication
        auth_group = subparser.add_argument_group('Authentication Options')
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
    
    # Browse command
    browse_parser = subparsers.add_parser(
        "browse",
        help="Browse OPC UA address space and display tree structure",
    )
    add_common_arguments(browse_parser)
    
    # Export command
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
    
    return parser


async def execute_browse(args: argparse.Namespace) -> int:
    """
    Execute browse command to display OPC UA address space tree.
    
    This function:
    1. Logs all input parameters
    2. Establishes connection to OPC UA server
    3. Browses the address space recursively
    4. Displays results as a formatted tree
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    # Extract hostname from server URL
    try:
        parsed_url = urlparse(args.server_url)
        hostname = parsed_url.hostname or "unknown"
        port = parsed_url.port or 4840
        server_display = f"{args.server_url} ({hostname}:{port})"
    except Exception:
        server_display = args.server_url
    
    # Log operation parameters
    logger.info("=" * 80)
    logger.info("BROWSE OPERATION PARAMETERS")
    logger.info("=" * 80)
    logger.info(f"Server URL:      {server_display}")
    logger.info(f"Start Node:      {args.node_id}")
    logger.info(f"Max Depth:       {args.depth}")
    logger.info(f"Security Policy: {args.security}")
    if args.security != "None":
        logger.info(f"Security Mode:   {args.mode}")
        logger.info(f"Certificate:     {args.cert}")
        logger.info(f"Private Key:     {args.key}")
    if args.user:
        logger.info(f"Username:        {args.user}")
        logger.info(f"Password:        {'*' * len(args.password) if args.password else 'Not set'}")
    logger.info("=" * 80)
    
    try:
        # Create and connect client
        async with OpcUaClient(
            server_url=args.server_url,
            username=args.user,
            password=args.password,
            security_policy=args.security,
            security_mode=args.mode,
            certificate_path=args.cert,
            private_key_path=args.key,
        ) as client:
            # Create browser instance
            browser = OpcUaBrowser(
                client=client.get_client(),
                max_depth=args.depth,
                include_values=False,
                namespaces_only=False,
            )
            
            # Execute browse operation
            result = await browser.browse(start_node_id=args.node_id)
            
            # Display results only if browse was successful
            if result.success:
                browser.print_tree(result)
                return 0
            else:
                # Error already logged by browser.browse()
                # Just show the tree with error message
                browser.print_tree(result)
                return 1
            
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        return 130
    except Exception:
        # Connection error - already logged by client
        # Don't show redundant error message
        return 1


async def execute_export(args: argparse.Namespace) -> int:
    """
    Execute export command to save OPC UA address space to file.
    
    This function:
    1. Logs all input parameters
    2. Establishes connection to OPC UA server
    3. Browses the address space recursively
    4. Exports nodes to specified format (CSV/JSON/XML)
    5. Saves to output file
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    # Extract hostname from server URL
    try:
        parsed_url = urlparse(args.server_url)
        hostname = parsed_url.hostname or "unknown"
        port = parsed_url.port or 4840
        server_display = f"{args.server_url} ({hostname}:{port})"
    except Exception:
        server_display = args.server_url
    
    # Log operation parameters
    logger.info("=" * 80)
    logger.info("EXPORT OPERATION PARAMETERS")
    logger.info("=" * 80)
    logger.info(f"Server URL:       {server_display}")
    logger.info(f"Start Node:       {args.node_id}")
    logger.info(f"Max Depth:        {args.depth}")
    logger.info(f"Export Format:    {args.format.upper()}")
    logger.info(f"Output File:      {args.output if args.output else 'Auto-generated'}")
    logger.info(f"Include Values:   {args.include_values}")
    logger.info(f"Namespaces Only:  {args.namespaces_only}")
    logger.info(f"Security Policy:  {args.security}")
    if args.security != "None":
        logger.info(f"Security Mode:    {args.mode}")
        logger.info(f"Certificate:      {args.cert}")
        logger.info(f"Private Key:      {args.key}")
    if args.user:
        logger.info(f"Username:         {args.user}")
        logger.info(f"Password:         {'*' * len(args.password) if args.password else 'Not set'}")
    logger.info("=" * 80)
    
    try:
        # Create and connect client
        async with OpcUaClient(
            server_url=args.server_url,
            username=args.user,
            password=args.password,
            security_policy=args.security,
            security_mode=args.mode,
            certificate_path=args.cert,
            private_key_path=args.key,
        ) as client:
            # Create browser
            browser = OpcUaBrowser(
                client=client.get_client(),
                max_depth=args.depth,
                include_values=args.include_values,
                namespaces_only=args.namespaces_only,
            )
            
            # Perform browse
            logger.info("Starting address space browse...")
            result = await browser.browse(start_node_id=args.node_id)
            
            if not result.success:
                logger.error(f"❌ Browse failed: {result.error_message}")
                return 1
            
            # Create exporter and save to file
            logger.info(f"Exporting {result.total_nodes} nodes to {args.format.upper()}...")
            exporter = Exporter(export_format=args.format)
            output_path = await exporter.export(result, args.output)
            
            logger.success(f"✅ Export completed: {output_path.absolute()}")
            logger.info(f"   Total nodes exported: {result.total_nodes}")
            logger.info(f"   File size: {output_path.stat().st_size / 1024:.2f} KB")
            
            return 0
            
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        return 130
    except Exception:
        logger.error(f"❌ Export operation failed")
        return 1


async def async_main() -> int:
    """
    Async main function.
    
    Returns:
        Exit code
    """
    # Setup logging
    setup_logging()
    
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Execute command
    if args.command == "browse":
        return await execute_browse(args)
    elif args.command == "export":
        return await execute_export(args)
    else:
        logger.error(f"Unknown command: {args.command}")
        return 1


def main() -> None:
    """
    Main entry point.
    Handles async execution and exit code.
    """
    try:
        exit_code = asyncio.run(async_main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()