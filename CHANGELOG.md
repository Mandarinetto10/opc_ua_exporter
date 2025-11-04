# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-04-11

### Added
- Asynchronous OPC UA client based on `asyncua` for high performance and non-blocking operations.
- Recursive browsing of the OPC UA server address space with configurable depth and starting node.
- Multi-format export: CSV, JSON, XML (strategy pattern).
- Username/password and certificate-based authentication.
- Support for all major OPC UA security policies:
  - None (no encryption)
  - Basic128Rsa15 (legacy)
  - Basic256 (legacy)
  - Basic256Sha256 (recommended)
  - Aes128_Sha256_RsaOaep (modern)
  - Aes256_Sha256_RsaPss (maximum security)
- Security modes: `Sign` and `SignAndEncrypt`.
- Built-in command to generate self-signed X.509 certificates for secure client authentication.
- Logging with `loguru` and contextual error hints.
- Robust error handling with clear messages and troubleshooting guidance.
- Modular, SOLID architecture, testable and extensible.
- Full type hints for Python 3.10+.
- Visual tree display of the address space with emoji icons for node types.
- Namespace filtering for focused exports.
- Hierarchical OPC UA path reconstruction for each node.
- Export features:
  - CSV: Excel-friendly, UTF-8 BOM, auto-quoted fields
  - JSON: Pretty-printed, hierarchical, ISO timestamps
  - XML: Schema-compliant, indented, metadata sections
- Clean project structure: CLI, models, client logic, browser, exporter, strategies.
- Comprehensive documentation: README, setup guide, troubleshooting, usage examples.

[1.0.0]: https://github.com/Mandarinetto10/opc_ua_exporter/releases/tag/v1.0.0
