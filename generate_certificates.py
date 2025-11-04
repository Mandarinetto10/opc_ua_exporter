"""
Script to generate self-signed certificates for OPC UA client.
Uses cryptography library to create certificate and private key.
"""

from pathlib import Path
from datetime import datetime, timedelta, timezone
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import sys
import ipaddress


def generate_self_signed_cert(
    cert_dir: Path = Path("certificates"),
    common_name: str = "OPC UA Python Client",
    organization: str = "My Organization",
    country: str = "IT",
    validity_days: int = 365,
    application_uri: str = "urn:example.org:FreeOpcUa:python-opcua-client",
    hostnames: list[str] = None,
):
    """
    Generate self-signed certificate and private key for OPC UA.
    
    Args:
        cert_dir: Directory to save certificates
        common_name: Common Name for certificate
        organization: Organization name
        country: Country code (2 letters)
        validity_days: Certificate validity in days
        application_uri: OPC UA Application URI (must match client configuration)
        hostnames: List of hostnames/DNS names to include in certificate
    """
    if hostnames is None:
        hostnames = ["localhost"]
    
    # Create certificates directory if it doesn't exist
    cert_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Creating certificates in: {cert_dir.absolute()}")
    print(f"🔖 Application URI: {application_uri}")
    
    # Generate private key
    print("🔐 Generating RSA private key (2048 bits)...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Save private key
    key_path = cert_dir / "client_key.pem"
    with open(key_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )
    print(f"✅ Private key saved: {key_path}")
    
    # Create certificate
    print("📜 Generating self-signed certificate...")
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])
    
    # Build Subject Alternative Names with Application URI
    san_list = [x509.UniformResourceIdentifier(application_uri)]
    
    # Add DNS names
    for hostname in hostnames:
        san_list.append(x509.DNSName(hostname))
    
    # Add IP addresses
    san_list.extend([
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        x509.IPAddress(ipaddress.IPv6Address("::1")),
    ])
    
    # Use timezone-aware datetime (fix deprecation warning)
    now = datetime.now(timezone.utc)
    
    # Generate certificate
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        now
    ).not_valid_after(
        now + timedelta(days=validity_days)
    ).add_extension(
        x509.SubjectAlternativeName(san_list),
        critical=False,
    ).add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True,
    ).add_extension(
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
    ).add_extension(
        x509.ExtendedKeyUsage([
            x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
            x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256(), backend=default_backend())
    
    # Save certificate
    cert_path = cert_dir / "client_cert.pem"
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    print(f"✅ Certificate saved: {cert_path}")
    
    # Also save in DER format (some OPC UA servers prefer this)
    cert_der_path = cert_dir / "client_cert.der"
    with open(cert_der_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.DER))
    print(f"✅ Certificate (DER) saved: {cert_der_path}")
    
    # Print certificate info
    print("\n📋 Certificate Information:")
    print(f"   • Subject: {cert.subject.rfc4514_string()}")
    print(f"   • Issuer: {cert.issuer.rfc4514_string()}")
    # Use timezone-aware properties (fix deprecation warning)
    print(f"   • Valid From: {cert.not_valid_before_utc}")
    print(f"   • Valid Until: {cert.not_valid_after_utc}")
    print(f"   • Serial Number: {cert.serial_number}")
    
    # Print Subject Alternative Names
    try:
        san_ext = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        print(f"\n📌 Subject Alternative Names:")
        for name in san_ext.value:
            if isinstance(name, x509.UniformResourceIdentifier):
                print(f"   • URI: {name.value}")
            elif isinstance(name, x509.DNSName):
                print(f"   • DNS: {name.value}")
            elif isinstance(name, x509.IPAddress):
                print(f"   • IP:  {name.value}")
    except x509.ExtensionNotFound:
        pass
    
    print("\n🎉 Certificates generated successfully!")
    print("\n📝 Usage Example:")
    print(f"   python -m opc_browser.cli browse \\")
    print(f"     -s opc.tcp://server:4840 \\")
    print(f"     --security Basic256Sha256 \\")
    print(f"     --mode SignAndEncrypt \\")
    print(f"     --cert {cert_path} \\")
    print(f"     --key {key_path} \\")
    print(f"     -u username -p password")
    
    print("\n💡 Note:")
    print(f"   Application URI: {application_uri}")
    print(f"   This URI must match the client's application description.")
    print(f"   If the server rejects the certificate, you may need to:")
    print(f"   1. Add the certificate to the server's trusted certificates")
    print(f"   2. Modify the Application URI to match server expectations")


def main():
    """Main entry point with command line argument support."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate OPC UA self-signed client certificates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate with default settings
  python generate_certificates.py
  
  # Generate with custom Application URI
  python generate_certificates.py --uri "urn:mycompany:opcua:client"
  
  # Generate with custom organization and hostnames
  python generate_certificates.py \\
    --org "My Company" \\
    --cn "My OPC UA Client" \\
    --hostname server.local \\
    --hostname 192.168.1.100
        """
    )
    
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("certificates"),
        help="Directory to save certificates (default: certificates)",
    )
    parser.add_argument(
        "--cn",
        "--common-name",
        dest="common_name",
        default="OPC UA Python Client",
        help="Common Name for certificate (default: OPC UA Python Client)",
    )
    parser.add_argument(
        "--org",
        "--organization",
        dest="organization",
        default="My Organization",
        help="Organization name (default: My Organization)",
    )
    parser.add_argument(
        "--country",
        default="IT",
        help="Country code (2 letters, default: IT)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Certificate validity in days (default: 365)",
    )
    parser.add_argument(
        "--uri",
        "--application-uri",
        dest="application_uri",
        default="urn:example.org:FreeOpcUa:python-opcua-client",
        help="OPC UA Application URI (default: urn:example.org:FreeOpcUa:python-opcua-client)",
    )
    parser.add_argument(
        "--hostname",
        action="append",
        dest="hostnames",
        help="Hostname/DNS name to include (can be used multiple times)",
    )
    
    args = parser.parse_args()
    
    # Default hostnames if none provided
    hostnames = args.hostnames if args.hostnames else ["localhost"]
    
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
    except Exception as e:
        print(f"\n❌ Error generating certificates: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
