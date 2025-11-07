# OPC UA Exporter

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![asyncua](https://img.shields.io/badge/asyncua-latest-green.svg)](https://github.com/FreeOpcUa/opcua-asyncio)
[![Tests](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/tests.yml)
[![Code Quality](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/code-quality.yml/badge.svg?branch=main)](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/code-quality.yml)
[![Type Check](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/type-check.yml/badge.svg?branch=main)](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/type-check.yml)
[![codecov](https://codecov.io/gh/Mandarinetto10/opc_ua_exporter/branch/main/graph/badge.svg)](https://codecov.io/gh/Mandarinetto10/opc_ua_exporter)
[![Issues](https://img.shields.io/github/issues/Mandarinetto10/opc_ua_exporter?logo=github)](https://github.com/Mandarinetto10/opc_ua_exporter/issues)
[![Contributors](https://img.shields.io/github/contributors/Mandarinetto10/opc_ua_exporter)](https://github.com/Mandarinetto10/opc_ua_exporter/graphs/contributors)
[![Stars](https://img.shields.io/github/stars/Mandarinetto10/opc_ua_exporter?style=social)](https://github.com/Mandarinetto10/opc_ua_exporter/stargazers)
[![Forks](https://img.shields.io/github/forks/Mandarinetto10/opc_ua_exporter?style=social)](https://github.com/Mandarinetto10/opc_ua_exporter/network/members)

A professional, feature-rich CLI for browsing and exporting OPC UA server address spaces. The tool embraces SOLID principles, asynchronous design, and first-class security support to operate safely in production environments.

---

## Table of Contents

- [Overview](#overview)
- [Feature Highlights](#feature-highlights)
- [Architecture at a Glance](#architecture-at-a-glance)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Certificate Management](#certificate-management)
  - [Connection Profiles](#connection-profiles)
  - [Logging](#logging)
- [Command Reference](#command-reference)
  - [Common Options](#common-options)
  - [Browse Command](#browse-command)
  - [Export Command](#export-command)
  - [Generate Certificate Command](#generate-certificate-command)
- [Export Output Summary](#export-output-summary)
- [Security Hardening Checklist](#security-hardening-checklist)
- [Observability and Monitoring](#observability-and-monitoring)
- [Testing and Quality Assurance](#testing-and-quality-assurance)
- [Troubleshooting Quick Wins](#troubleshooting-quick-wins)
- [Project Layout](#project-layout)
- [Documentation Hub](#documentation-hub)
- [Contributing](#contributing)
- [References](#references)
- [Authors](#authors)
- [License](#license)

---

## Overview

The exporter gives operators and integrators a single CLI entry point to explore an OPC UA server, understand its address space, and export the data in formats suitable for analytics and system integration. Security-conscious defaults, observability-friendly logging, and detailed documentation make it easy to deploy in regulated or mission-critical environments.

> **When to use it?**
> - During commissioning to validate namespace design and data point consistency.
> - For generating snapshots of the address space to feed historians, data lakes, or CMDBs.
> - For troubleshooting interoperability issues with third-party OPC UA stacks.

## Feature Highlights

- 🌐 **Asynchronous OPC UA client** powered by [`asyncua`](https://github.com/FreeOpcUa/opcua-asyncio) for responsive browsing.
- 🔍 **Recursive browsing** with configurable depth, namespace filtering, and human-readable tree output.
- 📊 **Multi-format export** (CSV, JSON, XML) implemented via the Strategy pattern for easy extension.
- 🔐 **Authentication coverage** for anonymous, username/password, and certificate-based flows.
- 🛡️ **Security policy support** for all OPC UA policies (Basic256Sha256, AES128/256, etc.) with explicit mode selection.
- 📝 **Structured logging** using `loguru`, including actionable troubleshooting hints on failure.
- 🏗️ **Modular architecture** with SOLID-inspired separation of concerns to simplify maintenance and testing.
- 🧪 **Comprehensive tests and type hints** to ensure long-term reliability on Python 3.10+.
- 🧰 **Certificate generation utility** that produces ready-to-use credentials with hardened file permissions.
- 📦 **Export metadata enrichment** including namespace indexes, browse paths, and node class indicators.

## Architecture at a Glance

| Layer | Responsibility | Key Modules |
|-------|----------------|-------------|
| CLI | Argument parsing, logging setup, command dispatch | [`src/opc_browser/cli.py`](src/opc_browser/cli.py) |
| Client | Connection lifecycle, security policy handling, authentication | [`src/opc_browser/client.py`](src/opc_browser/client.py) |
| Browser | Recursive traversal, aggregation of namespaces and statistics | [`src/opc_browser/browser.py`](src/opc_browser/browser.py) |
| Exporter | Format orchestration, file management, validation | [`src/opc_browser/exporter.py`](src/opc_browser/exporter.py) |
| Strategies | Format-specific serialization (CSV/JSON/XML) | [`src/opc_browser/strategies/`](src/opc_browser/strategies) |
| Models | Typed dataclasses for browse/export results | [`src/opc_browser/models.py`](src/opc_browser/models.py) |
| Certificates | Self-signed certificate generation, permission hardening | [`src/opc_browser/generate_cert.py`](src/opc_browser/generate_cert.py) |

The modules communicate through strongly typed dataclasses (`BrowseResult`, `NodeMetadata`, etc.), ensuring predictable data contracts across the stack.

## Requirements

- **Python** 3.10 or later (3.11+ recommended for performance improvements).
- **OPC UA server** reachable over the network (on-prem or cloud).
- **OpenSSL 1.1+** (optional) if you plan to inspect certificates externally.
- **Client certificates** for secure connections (generate with the CLI if none are available).

## Installation

```bash
# Clone repository
git clone https://github.com/Mandarinetto10/opc_ua_exporter.git
cd opc_ua_exporter

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies (runtime + tooling)
pip install -r requirements.txt
```

> Need a reproducible setup? Use `pip install -r requirements.lock` to pin exact versions or consult [SETUP.md](SETUP.md) for Docker-based workflows and advanced environment preparation.

## Configuration

### Certificate Management

1. Generate client credentials (PEM + DER + private key) using the dedicated command:
   ```bash
   python -m opc_browser.cli generate-cert --dir certificates --cn "My OPC UA Client"
   ```
2. Import the generated certificate into the OPC UA server trust list.
3. Preserve file permissions: the generator sets `600` on private keys by default. Avoid committing keys to version control and prefer dedicated secrets storage.
4. If you reuse existing certificates, ensure the **Application URI** and **hostname SAN entries** align with the server’s trust requirements.

### Connection Profiles

You can model different environments (development, staging, production) by saving commonly used arguments into shell aliases or scripts. Example profile script:

```bash
#!/usr/bin/env bash
python -m opc_browser.cli "$@" \
  --server-url opc.tcp://prod-server:4840 \
  --security Basic256Sha256 \
  --mode SignAndEncrypt \
  --cert certificates/prod_client_cert.pem \
  --key certificates/prod_client_key.pem
```

Place the script under `profiles/browse-prod.sh`, mark it executable, and call `./profiles/browse-prod.sh browse --depth 5`.

### Logging

The CLI configures [loguru](https://github.com/Delgan/loguru) with colorized, timestamped output. Logs highlight the command parameters (without leaking secrets) and provide success/failure banners.

- Add `--log-level DEBUG` via the `LOGURU_LEVEL` environment variable for deeper diagnostics: `LOGURU_LEVEL=DEBUG python -m opc_browser.cli browse ...`.
- Redirect logs to file using `LOGURU_SINK=file.log` or wrap the command with `python -m opc_browser.cli ... 2>&1 | tee session.log` for later inspection.

## Command Reference

All functionality is exposed through the module entry point:

```bash
python -m opc_browser.cli {browse|export|generate-cert} [OPTIONS]
```

### Common Options

| Option | Applies to | Description |
|--------|------------|-------------|
| `--server-url/-s` | browse, export | **Required.** OPC UA endpoint URL (`opc.tcp://host:port`). |
| `--node-id/-n` | browse, export | Starting node ID. Defaults to `i=84` (RootFolder). |
| `--depth/-d` | browse, export | Maximum recursion depth. Use `0` for only the start node. |
| `--security/-sec` | browse, export | Security policy (see [Security Hardening Checklist](#security-hardening-checklist)). |
| `--mode/-m` | browse, export | Security mode (`Sign`, `SignAndEncrypt`). Mandatory when policy ≠ `None`. |
| `--cert/--key` | browse, export | Paths to client certificate and private key for secure sessions. |
| `--user/-u` & `--password/-p` | browse, export | Username/password credentials. Password is never logged. |

### Browse Command

Visualise the address space by walking the server recursively.

```bash
python -m opc_browser.cli browse \
  --server-url opc.tcp://localhost:4840 \
  --depth 3 \
  --security Basic256Sha256 \
  --mode SignAndEncrypt \
  --cert certificates/client_cert.pem \
  --key certificates/client_key.pem
```

| Extra Option | Description |
|--------------|-------------|
| `--namespaces-only` | Focus output on namespace nodes for quick inventory checks. |
| `--include-values` | Display live variable values (may increase browse time). |

Sample output excerpt:

```
📁 RootFolder (Object, NodeId=i=84)
├── 📁 Objects (Object, NodeId=i=85)
│   ├── 📁 MyDevice (Object, NodeId="ns=2;s=Devices.MyDevice")
│   │   ├── 🔧 Status (Variable, Value="Running", DataType=String)
│   │   └── 🌡️ Temperature (Variable, Value=24.7, DataType=Double)
│   └── 📁 Diagnostics (Object, NodeId="ns=2;s=Diagnostics")
└── 📁 Types (Object, NodeId=i=86)
```

### Export Command

Persist the address space to structured files suitable for analytics, dashboards, or archival.

```bash
python -m opc_browser.cli export \
  --server-url opc.tcp://localhost:4840 \
  --format json \
  --include-values \
  --full-export \
  --output export/my_space.json
```

| Export Option | Description |
|---------------|-------------|
| `--format/-f` | Target format (`csv`, `json`, `xml`). Auto-detected from `--output` if omitted. |
| `--output/-o` | Output file path. Defaults to `export/opcua_export_<timestamp>.<format>`. |
| `--namespaces-only` | Export only namespace metadata and references (no variables). |
| `--include-values` | Capture variable values at browse time. Useful for baselines or documentation. |
| `--full-export` | Include extended attributes (`Description`, `DataType`, `AccessLevel`, etc.). |

The exporter validates file extensions, corrects mismatches, and prints a completion banner with statistics (node count, namespaces, file size). Detailed field mapping tables and examples live in [docs/EXPORT_FORMATS.md](docs/EXPORT_FORMATS.md).

### Generate Certificate Command

Create self-signed client certificates aligned with OPC UA security policies.

```bash
python -m opc_browser.cli generate-cert \
  --dir certificates \
  --application-uri "urn:example.org:FreeOpcUa:opcua-asyncio" \
  --hostname localhost --hostname my-workstation \
  --days 365
```

| Option | Purpose |
|--------|---------|
| `--dir` | Destination directory for generated artifacts (defaults to `certificates/`). |
| `--common-name/--cn` | Certificate subject common name. |
| `--organization/--org` | Organization attribute for the certificate subject. |
| `--country` | Two-letter ISO country code. |
| `--application-uri/--uri` | Application URI placed into the subject alternative name. |
| `--hostname` | Repeatable flag adding hostnames/IPs to the certificate SAN. |
| `--days` | Validity period in days. |

The command emits PEM and DER files plus the private key, enforcing user-only permissions and logging the resulting paths.

## Export Output Summary

| Format | File(s) | Highlights |
|--------|---------|------------|
| CSV | Single UTF-8 CSV with BOM | Excel-friendly; includes hierarchy columns (`namespace`, `browse_path`, `display_name`). |
| JSON | Pretty-printed JSON | Nested tree mirroring browse output; includes timestamps and metadata sections. |
| XML | Indented XML document | Schema-aligned with OPC UA concepts; includes namespaces, references, and values. |

Need to integrate exports into another system? Reuse the strategy classes under [`src/opc_browser/strategies/`](src/opc_browser/strategies) or create your own format strategy by extending `BaseStrategy`.

## Security Hardening Checklist

- ✅ Prefer `SignAndEncrypt` mode with modern policies such as `Basic256Sha256` or `Aes256_Sha256_RsaPss` when connecting to production servers.
- ✅ Generate certificates with hostnames/IPs matching the client machine; mismatches often cause trust failures.
- ✅ Store private keys outside of shared folders and enforce owner-only permissions (`chmod 600`).
- ✅ Validate endpoint URLs before connecting to avoid SSRF-style misdirection to untrusted hosts.
- ✅ Limit recursion depth and namespaces during exports when working with untrusted or very large servers to reduce DoS risk.
- ✅ Rotate credentials periodically and audit server trust lists to remove unused certificates.

Manual OpenSSL instructions remain available in [docs/TESTING.md](docs/TESTING.md#integration-environments) for lab or offline scenarios.

## Observability and Monitoring

- Logs are structured with consistent prefixes, enabling ingestion into centralized logging platforms.
- Export completion banners report the absolute output path, node counts, namespace statistics, and file sizes.
- Combine with shell wrappers to emit Prometheus-friendly metrics (e.g., wrap command execution in a script that records duration).

## Testing and Quality Assurance

The repository bundles an opinionated test and linting pipeline:

| Command | Scope |
|---------|-------|
| `pytest -v` | Async integration tests covering browse and export flows. |
| `pytest --cov=src/opc_browser` | Coverage report (XML/HTML) for CI visibility. |
| `ruff check src/ tests/` | Linting with auto-fixes for style and correctness issues. |
| `black src/ tests/` | Code formatting with 88-character lines. |
| `mypy src/` | Static typing across the entire client and CLI stack. |

Refer to [docs/TESTING.md](docs/TESTING.md) for expanded guidance, including CI matrix details, troubleshooting flaky tests, and interpreting coverage artifacts.

## Troubleshooting Quick Wins

- **Connection refused / timeout** – Confirm the endpoint, firewall rules, and whether security policies match the server configuration.
- **BadSecurityChecksFailed** – Revisit certificate trust lists on both client and server, ensure hostnames and Application URI align.
- **Empty export** – Increase `--depth`, verify the starting node ID, or disable `--namespaces-only`.
- **Unicode issues** – CSV exports include a BOM for Excel compatibility; verify downstream tooling expects UTF-8.

A comprehensive troubleshooting matrix with error code lookups and remediation scripts is provided in [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Project Layout

```
opc_ua_exporter/
├── pyproject.toml             # Project configuration (build, lint, tests)
├── requirements.txt           # Runtime dependencies
├── requirements.lock          # Locked dependency set
├── SETUP.md                   # Extended setup walkthrough
├── README.md                  # High-level overview (this file)
├── docs/                      # Detailed guides and references
├── export/                    # Auto-generated export files
├── certificates/              # Generated certificates and keys
└── src/opc_browser/           # Application source code
    ├── cli.py                 # CLI entry point and argument parsing
    ├── browser.py             # Recursive browsing logic
    ├── client.py              # OPC UA client helpers
    ├── exporter.py            # Export orchestration
    ├── generate_cert.py       # Certificate generation utilities
    └── strategies/            # Format-specific export strategies
```

## Documentation Hub

- 📘 **Testing Guide** – workflows, coverage, and quality tooling: [docs/TESTING.md](docs/TESTING.md)
- 🛠️ **Troubleshooting Playbook** – diagnostics for connection, security, and NodeId issues: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- 📄 **Export Reference** – field mappings and sample payloads: [docs/EXPORT_FORMATS.md](docs/EXPORT_FORMATS.md)
- 🧭 **Setup Guide** – environment provisioning and tooling: [SETUP.md](SETUP.md)

## Contributing

Contributions are welcome! If you uncover bugs, have feature ideas, or want to submit a pull request, please open an issue on [GitHub](https://github.com/Mandarinetto10/opc_ua_exporter). Ensure submissions include relevant tests, documentation updates, and follow the existing coding standards.

## References

- [OPC UA Specification](https://reference.opcfoundation.org/)
- [asyncua documentation](https://github.com/FreeOpcUa/opcua-asyncio)
- [Python cryptography](https://cryptography.io/)
- [OPC Foundation](https://opcfoundation.org/)
- [loguru](https://github.com/Delgan/loguru)

## Authors

- Mandarinetto10 — Initial work and ongoing maintenance

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
