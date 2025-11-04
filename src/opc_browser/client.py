"""
OPC UA Client wrapper with connection and authentication management.

This module provides a high-level wrapper around the asyncua Client library,
implementing connection lifecycle management, authentication, and security
configuration using the async context manager pattern.
"""

from typing import Optional
from pathlib import Path
from asyncua import Client, ua
from asyncua.crypto.security_policies import (
    SecurityPolicyBasic256Sha256,
    SecurityPolicyBasic256,
    SecurityPolicyBasic128Rsa15,
    SecurityPolicyAes128Sha256RsaOaep,
    SecurityPolicyAes256Sha256RsaPss,
)
from asyncua.ua import MessageSecurityMode
from loguru import logger


class OpcUaClientError(Exception):
    """Base exception for OPC UA client errors."""
    pass


class SecurityConfigurationError(OpcUaClientError):
    """Raised when security configuration is invalid."""
    pass


class ConnectionError(OpcUaClientError):
    """Raised when connection to server fails."""
    pass


class OpcUaClient:
    """
    High-level wrapper for asyncua Client with enhanced connection management.
    
    This class handles:
    - Secure connection establishment with certificate-based authentication
    - Username/password authentication
    - Connection lifecycle management via async context manager
    - Comprehensive error handling and logging
    
    Attributes:
        server_url: OPC UA server endpoint URL
        client: Underlying asyncua Client instance
        
    Security Policies Supported:
        - None: No encryption (plain connection)
        - Basic256: Legacy RSA encryption (deprecated)
        - Basic128Rsa15: Legacy encryption (deprecated)
        - Basic256Sha256: Modern SHA256-based encryption
        - Aes128_Sha256_RsaOaep: AES-128 encryption
        - Aes256_Sha256_RsaPss: AES-256 encryption (highest security)
    """
    
    # Security policy mapping to asyncua native classes
    SECURITY_POLICY_MAP = {
        "None": None,
        "Basic256": SecurityPolicyBasic256,
        "Basic128Rsa15": SecurityPolicyBasic128Rsa15,
        "Basic256Sha256": SecurityPolicyBasic256Sha256,
        "Aes128_Sha256_RsaOaep": SecurityPolicyAes128Sha256RsaOaep,
        "Aes256_Sha256_RsaPss": SecurityPolicyAes256Sha256RsaPss,
    }
    
    # Security mode mapping to asyncua MessageSecurityMode enum
    SECURITY_MODE_MAP = {
        "Sign": MessageSecurityMode.Sign,
        "SignAndEncrypt": MessageSecurityMode.SignAndEncrypt,
    }
    
    def __init__(
        self,
        server_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        security_policy: str = "None",
        security_mode: Optional[str] = None,
        certificate_path: Optional[Path] = None,
        private_key_path: Optional[Path] = None,
    ) -> None:
        """
        Initialize OPC UA client with connection parameters.
        
        Args:
            server_url: OPC UA server endpoint (e.g., opc.tcp://localhost:4840)
            username: Optional username for authentication
            password: Optional password for authentication
            security_policy: Security policy name (default: "None")
            security_mode: Security mode - "Sign" or "SignAndEncrypt" (required if policy != "None")
            certificate_path: Path to client certificate PEM file (required for non-None policy)
            private_key_path: Path to private key PEM file (required for non-None policy)
            
        Raises:
            SecurityConfigurationError: If security configuration is invalid
        """
        self.server_url = server_url
        self.username = username
        self.password = password
        self.security_policy = security_policy
        self.security_mode = security_mode
        self.certificate_path = certificate_path
        self.private_key_path = private_key_path
        
        # Initialize asyncua client with connection timeout
        self.client = Client(url=server_url, timeout=30)
        
        logger.debug(f"OPC UA Client initialized for {server_url}")
    
    async def __aenter__(self) -> "OpcUaClient":
        """Async context manager entry - establishes connection to server."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit - disconnects from server."""
        await self.disconnect()
    
    async def connect(self) -> None:
        """
        Establish connection to OPC UA server with configured security and authentication.
        
        This method:
        1. Validates and configures security policy and mode
        2. Sets up certificate-based encryption if required
        3. Configures username/password authentication if provided
        4. Establishes connection to the server
        5. Verifies server is operational
        
        Raises:
            SecurityConfigurationError: If security configuration is invalid
            ConnectionError: If connection to server fails
        """
        try:
            logger.info(f"Connecting to {self.server_url}")
            
            # Configure security if not using plain connection
            if self.security_policy != "None":
                await self._configure_security()
            
            # Configure authentication
            if self.username and self.password:
                self.client.set_user(self.username)
                self.client.set_password(self.password)
                logger.debug(f"Authentication configured for user: {self.username}")
            
            # Establish connection
            await self.client.connect()
            
            # Verify server status
            server_node = self.client.get_server_node()
            server_info = await server_node.read_browse_name()
            
            # Attempt to read server state for detailed status
            try:
                server_status_node = self.client.get_node(ua.ObjectIds.Server_ServerStatus)
                server_state = await server_status_node.read_value()
                state_name = server_state.State.name if hasattr(server_state, 'State') else 'Running'
                logger.success(f"✅ Connected to '{server_info.Name}' (State: {state_name})")
            except Exception:
                logger.success(f"✅ Connected to '{server_info.Name}'")
                
        except ua.UaStatusCodeError as e:
            # Handle OPC UA specific errors with detailed messages
            error_msg = self._format_ua_error(e)
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e
            
        except Exception as e:
            # Handle general connection errors
            error_msg = f"Connection failed: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e
    
    async def _configure_security(self) -> None:
        """
        Configure security policy and certificates.
        
        This method MUST be async because set_security() is a coroutine.
        
        Raises:
            SecurityConfigurationError: If security configuration is invalid
        """
        # Validate security policy
        if self.security_policy not in self.SECURITY_POLICY_MAP:
            raise SecurityConfigurationError(
                f"Unknown security policy '{self.security_policy}'. "
                f"Supported: {', '.join(self.SECURITY_POLICY_MAP.keys())}"
            )
        
        # Validate security mode
        if not self.security_mode:
            raise SecurityConfigurationError(
                f"Security mode is required for policy '{self.security_policy}'. "
                f"Use: {', '.join(self.SECURITY_MODE_MAP.keys())}"
            )
        
        if self.security_mode not in self.SECURITY_MODE_MAP:
            raise SecurityConfigurationError(
                f"Unknown security mode '{self.security_mode}'. "
                f"Supported: {', '.join(self.SECURITY_MODE_MAP.keys())}"
            )
        
        # Validate certificates
        if not self.certificate_path or not self.private_key_path:
            raise SecurityConfigurationError(
                "Certificate (--cert) and private key (--key) are required for "
                f"security policy '{self.security_policy}'"
            )
        
        if not self.certificate_path.exists():
            raise SecurityConfigurationError(
                f"Certificate file not found: {self.certificate_path}"
            )
        
        if not self.private_key_path.exists():
            raise SecurityConfigurationError(
                f"Private key file not found: {self.private_key_path}"
            )
        
        # Apply security configuration using asyncua's native method
        # set_security() is a coroutine that MUST be awaited
        policy_class = self.SECURITY_POLICY_MAP[self.security_policy]
        mode = self.SECURITY_MODE_MAP[self.security_mode]
        
        try:
            await self.client.set_security(
                policy_class,
                certificate=str(self.certificate_path),
                private_key=str(self.private_key_path),
                mode=mode,
            )
            logger.debug(f"Security configured: {self.security_policy} with {self.security_mode}")
        except Exception as e:
            raise SecurityConfigurationError(
                f"Failed to configure security: {type(e).__name__}: {str(e)}"
            ) from e
    
    def _format_ua_error(self, error: ua.UaStatusCodeError) -> str:
        """
        Format OPC UA status code error into human-readable message.
        
        Args:
            error: UaStatusCodeError from asyncua
            
        Returns:
            Formatted error message
        """
        # Safely extract error code name
        try:
            if hasattr(error, 'code'):
                if hasattr(error.code, 'name'):
                    error_code = error.code.name
                else:
                    # code is an integer
                    error_code = f"0x{error.code:08X}" if isinstance(error.code, int) else str(error.code)
            else:
                error_code = "Unknown"
        except Exception:
            error_code = "Unknown"
        
        error_desc = str(error)
        
        # Comprehensive hints for OPC UA errors (following OPC UA specification)
        hints = {
            # Authentication & Authorization Errors
            "BadIdentityTokenRejected": "Check username/password and server user permissions",
            "BadUserAccessDenied": "User doesn't have permission to access this resource",
            "BadIdentityTokenInvalid": "Identity token is malformed or invalid",
            
            # Security & Certificate Errors
            "BadCertificateUriInvalid": "Certificate Application URI doesn't match client configuration",
            "BadSecurityChecksFailed": "Server rejected the certificate - ensure it's in server's trust list",
            "BadCertificateInvalid": "Certificate is invalid, expired, or not trusted",
            "BadSecurityModeRejected": "Server doesn't support the requested security mode",
            
            # Connection & Session Errors
            "BadSessionIdInvalid": "Session expired or was closed by server",
            "BadSessionClosed": "Session was closed - reconnection required",
            "BadTimeout": "Connection timeout - check network connectivity and server status",
            "BadConnectionClosed": "Connection was closed unexpectedly",
            "BadTcpEndpointUrlInvalid": "Server URL format is invalid",
            
            # Node & Browse Errors
            "BadNodeIdUnknown": "Node does not exist in the server address space",
            "BadNodeIdInvalid": "Node ID format is invalid",
            "BadBrowseDirectionInvalid": "Browse direction is not supported",
            
            # Server Errors
            "BadUnexpectedError": "Server encountered an unexpected error - check server logs",
            "BadServerNotConnected": "Not connected to server",
            "BadServerHalted": "Server is halted or shutting down",
            
            # Request Errors
            "BadTooManyOperations": "Too many operations requested - reduce batch size",
            "BadNothingToDo": "No operations to perform",
        }
        
        hint = hints.get(error_code, "")
        message = f"{error_desc}"
        if hint:
            message += f" | Hint: {hint}"
            
        return message
    
    async def disconnect(self) -> None:
        """
        Gracefully disconnect from OPC UA server.
        
        This method ensures clean disconnection even if errors occur.
        """
        try:
            await self.client.disconnect()
            logger.debug("Disconnected from server")
        except Exception as e:
            logger.warning(f"Disconnect warning: {type(e).__name__}: {str(e)}")
    
    def get_client(self) -> Client:
        """
        Get the underlying asyncua Client instance.
        
        Returns:
            asyncua.Client: The configured client instance
        """
        return self.client
    
    @classmethod
    def get_supported_policies(cls) -> list[str]:
        """Get list of supported security policy names."""
        return list(cls.SECURITY_POLICY_MAP.keys())
    
    @classmethod
    def get_supported_modes(cls) -> list[str]:
        """Get list of supported security mode names."""
        return list(cls.SECURITY_MODE_MAP.keys())