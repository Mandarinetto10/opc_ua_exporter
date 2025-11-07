"""Certificate generation module for OPC UA client authentication.

This module provides functionality to generate self-signed X.509 certificates
suitable for OPC UA client authentication with configurable security parameters,
including proper Subject Alternative Names and key usage extensions.
"""

from __future__ import annotations

import ipaddress
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import cast

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtensionOID, NameOID
from loguru import logger


def generate_self_signed_cert(
    cert_dir: Path = Path("certificates"),
    common_name: str = "OPC UA Python Client",
    organization: str = "My Organization",
    country: str = "IT",
    validity_days: int = 365,
    application_uri: str = "urn:example.org:FreeOpcUa:opcua-asyncio",
    hostnames: list[str] | None = None,
) -> None:
    """Generate self-signed X.509 certificate and private key for OPC UA client.

    Creates a complete certificate with OPC UA-specific extensions including:
    - Application URI in Subject Alternative Names (required by OPC UA spec)
    - DNS names and IP addresses for hostname validation
    - Proper key usage and extended key usage flags
    - Both PEM and DER formats for compatibility

    The generated certificate is suitable for use with asyncua-based OPC UA
    clients and supports both Sign and SignAndEncrypt security modes.

    Args:
        cert_dir: Directory where certificate files will be saved. Created if missing.
        common_name: Certificate Common Name (CN field in subject).
        organization: Certificate Organization (O field in subject).
        country: Two-letter ISO country code (C field in subject).
        validity_days: Number of days the certificate remains valid.
        application_uri: OPC UA Application URI. Must match the URI used by the
            asyncua client. This is added to Subject Alternative Names.
        hostnames: List of DNS names to include in SAN. Defaults to ["localhost"]
            if None. IPv4 (127.0.0.1) and IPv6 (::1) loopback addresses are
            automatically included.

    Raises:
        OSError: If certificate directory cannot be created or files cannot be written.
        Exception: If certificate generation fails for cryptographic reasons.

    Examples:
        Basic usage with defaults:
            >>> generate_self_signed_cert()

        Custom certificate for production environment:
            >>> generate_self_signed_cert(
            ...     cert_dir=Path("/etc/opcua/certs"),
            ...     common_name="Production SCADA Client",
            ...     organization="ACME Corporation",
            ...     validity_days=730,
            ...     application_uri="urn:acme:scada:client",
            ...     hostnames=["scada-client.acme.local", "192.168.1.100"]
            ... )
    """
    if hostnames is None:
        hostnames = ["localhost"]

    try:
        cert_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Certificate directory: {cert_dir.absolute()}")
        logger.info(f"Application URI: {application_uri}")

        # RSA key size of 2048 bits is minimum recommended by OPC UA specification
        logger.info("Generating RSA private key (2048 bits)...")
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )

        key_path: Path = cert_dir / "client_key.pem"
        with open(key_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
        # SECURITY: restrict file permissions so the private key is not world-readable
        if os.name != "nt":
            try:
                os.chmod(key_path, 0o600)
            except FileNotFoundError:
                logger.debug("Skipped chmod for private key because the file is mocked or missing")
            except OSError as exc:
                logger.warning(f"Could not harden private key permissions automatically: {exc}")
        logger.success(f"✅ Private key saved: {key_path}")

        logger.info("Generating self-signed X.509 certificate...")
        subject: x509.Name = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, country),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            ]
        )
        issuer: x509.Name = subject

        # Build Subject Alternative Names - OPC UA requires Application URI
        san_list: list[x509.GeneralName] = [x509.UniformResourceIdentifier(application_uri)]
        for hostname in hostnames:
            san_list.append(x509.DNSName(hostname))
        # Add loopback addresses for local testing
        san_list.extend(
            [
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                x509.IPAddress(ipaddress.IPv6Address("::1")),
            ]
        )

        now: datetime = datetime.now(timezone.utc)
        cert: x509.Certificate = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now)
            .not_valid_after(now + timedelta(days=validity_days))
            .add_extension(
                x509.SubjectAlternativeName(san_list),
                critical=False,
            )
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
            .add_extension(
                # Key usage appropriate for OPC UA client/server authentication
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    content_commitment=False,
                    data_encipherment=True,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .add_extension(
                # Extended key usage for both client and server authentication
                x509.ExtendedKeyUsage(
                    [
                        x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
                        x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                    ]
                ),
                critical=False,
            )
            .sign(private_key, hashes.SHA256(), backend=default_backend())
        )

        cert_path: Path = cert_dir / "client_cert.pem"
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        if os.name != "nt":
            try:
                os.chmod(cert_path, 0o644)
            except FileNotFoundError:
                logger.debug("Skipped chmod for certificate because the file is mocked or missing")
            except OSError as exc:
                logger.warning(f"Could not adjust certificate permissions automatically: {exc}")
        logger.success(f"✅ Certificate (PEM) saved: {cert_path}")

        # DER format required by some OPC UA servers
        cert_der_path: Path = cert_dir / "client_cert.der"
        with open(cert_der_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.DER))
        logger.success(f"✅ Certificate (DER) saved: {cert_der_path}")

        logger.info("=" * 80)
        logger.info("CERTIFICATE INFORMATION")
        logger.info("=" * 80)
        logger.info(f"Subject:      {cert.subject.rfc4514_string()}")
        logger.info(f"Issuer:       {cert.issuer.rfc4514_string()}")
        logger.info(f"Valid From:   {cert.not_valid_before_utc}")  # type: ignore[attr-defined]
        logger.info(f"Valid Until:  {cert.not_valid_after_utc}")  # type: ignore[attr-defined]
        logger.info(f"Serial:       {cert.serial_number}")

        try:
            san_ext: x509.Extension[x509.SubjectAlternativeName] = cast(
                x509.Extension[x509.SubjectAlternativeName],
                cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME),
            )
            logger.info("Subject Alternative Names:")
            for name in san_ext.value:
                if isinstance(name, x509.UniformResourceIdentifier):
                    logger.info(f"  • URI: {name.value}")
                elif isinstance(name, x509.DNSName):
                    logger.info(f"  • DNS: {name.value}")
                elif isinstance(name, x509.IPAddress):
                    logger.info(f"  • IP:  {name.value}")
        except x509.ExtensionNotFound:
            pass

        logger.info("=" * 80)
        logger.success("✅ Certificate generation completed successfully!")

    except Exception as e:
        logger.error(f"Certificate generation failed: {type(e).__name__}: {str(e)}")
        raise
