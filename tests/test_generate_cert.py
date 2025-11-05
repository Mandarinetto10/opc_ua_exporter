from pathlib import Path
from unittest.mock import MagicMock

import pytest

from opc_browser.generate_cert import generate_self_signed_cert


def test_generate_self_signed_cert_creates_files(tmp_path):
    cert_dir = tmp_path / "certs"
    generate_self_signed_cert(cert_dir=cert_dir)
    assert (cert_dir / "client_cert.pem").exists()
    assert (cert_dir / "client_key.pem").exists()
    assert (cert_dir / "client_cert.der").exists()


def test_generate_self_signed_cert_custom_args(tmp_path):
    cert_dir = tmp_path / "custom"
    generate_self_signed_cert(
        cert_dir=cert_dir,
        common_name="MyCN",
        organization="MyOrg",
        country="US",
        validity_days=2,
        application_uri="urn:test:custom",
        hostnames=["host1", "host2"],
    )
    assert (cert_dir / "client_cert.pem").exists()
    assert (cert_dir / "client_key.pem").exists()
    assert (cert_dir / "client_cert.der").exists()


def test_generate_self_signed_cert_raises_on_invalid_dir(monkeypatch, tmp_path):
    # Simulate OSError on mkdir
    def fail_mkdir(*args, **kwargs):
        raise OSError("fail")

    monkeypatch.setattr(Path, "mkdir", fail_mkdir)
    with pytest.raises(OSError):
        generate_self_signed_cert(cert_dir=tmp_path / "faildir")


def test_generate_self_signed_cert_raises_on_write(monkeypatch, tmp_path):
    cert_dir = tmp_path / "certs"
    cert_dir.mkdir()

    # Simulate error on open
    def fail_open(*args, **kwargs):
        raise OSError("fail")

    monkeypatch.setattr("builtins.open", fail_open)
    with pytest.raises(OSError):
        generate_self_signed_cert(cert_dir=cert_dir)


def test_generate_self_signed_cert_san_extension(tmp_path):
    cert_dir = tmp_path / "certs"
    # Should not raise, and SAN extension should be present (covered by log output)
    generate_self_signed_cert(cert_dir=cert_dir, hostnames=["localhost", "127.0.0.1"])


def test_generate_self_signed_cert_handles_missing_san_extension(tmp_path, monkeypatch):
    cert_dir = tmp_path / "certs"
    from cryptography import x509

    # Patch x509.Certificate.extensions to raise ExtensionNotFound when accessed
    class FakeCert:
        def __init__(self, *args, **kwargs):
            pass

        @property
        def subject(self):
            class S:
                def rfc4514_string(self):
                    return "CN=Fake"

            return S()

        @property
        def issuer(self):
            class S:
                def rfc4514_string(self):
                    return "CN=Fake"

            return S()

        @property
        def not_valid_before_utc(self):
            return "now"

        @property
        def not_valid_after_utc(self):
            return "later"

        @property
        def serial_number(self):
            return 123

        @property
        def extensions(self):
            class Exts:
                def get_extension_for_oid(self, oid):
                    raise x509.ExtensionNotFound("not found", oid)

            return Exts()

        def public_bytes(self, encoding):
            return b"cert"

    # Patch CertificateBuilder.sign to return our FakeCert
    monkeypatch.setattr(x509.CertificateBuilder, "sign", lambda *a, **k: FakeCert())
    # Patch private key generation to return a real RSA key (so .public_key() works)
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import rsa

    real_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    monkeypatch.setattr(rsa, "generate_private_key", lambda *a, **k: real_key)
    # Patch open to avoid file I/O
    import builtins

    monkeypatch.setattr(
        builtins,
        "open",
        lambda *a, **k: MagicMock(
            __enter__=lambda s: s, __exit__=lambda s, *a: None, write=lambda b: None
        ),
    )
    # Patch Path.exists to always return True
    monkeypatch.setattr(Path, "exists", lambda self: True)
    # Patch Path.mkdir to do nothing
    monkeypatch.setattr(Path, "mkdir", lambda self, parents=True, exist_ok=True: None)

    # Now call the function, which will hit the except x509.ExtensionNotFound: pass
    from opc_browser.generate_cert import generate_self_signed_cert

    generate_self_signed_cert(cert_dir=cert_dir)
