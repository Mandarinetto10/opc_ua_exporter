<p align="center">
  <h1 align="center" style="font-size:2.5em;"><strong>OPC UA Exporter</strong></h1>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/" target="_blank">
    <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python Version" />
  </a>
  <a href="LICENSE" target="_blank">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" />
  </a>
  <a href="https://github.com/FreeOpcUa/opcua-asyncio" target="_blank">
    <img src="https://img.shields.io/badge/asyncua-latest-green.svg" alt="asyncua" />
  </a>
</p>

<p align="center">
  <a href="https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/tests.yml" target="_blank">
    <img src="https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/tests.yml/badge.svg?branch=main" alt="Tests" />
  </a>
  <a href="https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/code-quality.yml" target="_blank">
    <img src="https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/code-quality.yml/badge.svg?branch=main" alt="Code Quality" />
  </a>
  <a href="https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/type-check.yml" target="_blank">
    <img src="https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/type-check.yml/badge.svg?branch=main" alt="Type Check" />
  </a>
  <a href="https://codecov.io/gh/Mandarinetto10/opc_ua_exporter" target="_blank">
    <img src="https://codecov.io/gh/Mandarinetto10/opc_ua_exporter/branch/main/graph/badge.svg" alt="Coverage" />
  </a>
</p>

<p align="center">
  <a href="https://github.com/Mandarinetto10/opc_ua_exporter/issues" target="_blank">
    <img src="https://img.shields.io/github/issues/Mandarinetto10/opc_ua_exporter?logo=github" alt="Issues" />
  </a>
  <a href="https://github.com/Mandarinetto10/opc_ua_exporter/graphs/contributors" target="_blank">
    <img src="https://img.shields.io/github/contributors/Mandarinetto10/opc_ua_exporter" alt="Contributors" />
  </a>
  <a href="https://github.com/Mandarinetto10/opc_ua_exporter/stargazers" target="_blank">
    <img src="https://img.shields.io/github/stars/Mandarinetto10/opc_ua_exporter?style=social" alt="Stars" />
  </a>
  <a href="https://github.com/Mandarinetto10/opc_ua_exporter/network/members" target="_blank">
    <img src="https://img.shields.io/github/forks/Mandarinetto10/opc_ua_exporter?style=social" alt="Forks" />
  </a>
</p>

<p align="center">
  <em>A professional, feature-rich CLI for browsing and exporting OPC UA server address spaces.<br>
  Embraces SOLID principles, asynchronous design, and first-class security support to operate safely in production environments.</em>
</p>

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
  - [Common Arguments](#common-arguments)
  - [Security Policies](#security-policies)
  - [Browse Command](#browse-command)
  - [Browse Examples](#browse-examples)
  - [Export Command](#export-command)
  - [Export Extra Arguments](#export-extra-arguments)
  - [Extended Attributes](#extended-attributes)
  - [Export Examples](#export-examples)
  - [Generate Certificate Command](#generate-certificate-command)
  - [Certificate Examples](#certificate-examples)
  - [Using Generated Certificates](#using-generated-certificates)
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
python -m opc_browser.cli "$@" --server-url opc.tcp://prod-server:4840 --security Basic256Sha256 --mode SignAndEncrypt --cert certificates/prod_client_cert.pem --key certificates/prod_client_key.pem
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

### Common Arguments

| Argument | Short | Applies to | Description | Default |
|----------|-------|------------|-------------|---------|
| `--server-url` | `-s` | browse, export | **Required.** OPC UA endpoint URL (`opc.tcp://host:port`). | - |
| `--node-id` | `-n` | browse, export | Starting node ID for browsing (e.g. `ns=2;i=1000`) | `i=84` (RootFolder) |
| `--depth` | `-d` | browse, export | Maximum recursion depth. Use `0` for only the start node. | `3` |
| `--security` | `-sec` | browse, export | Security policy (see [Security Policies](#security-policies)). | `None` |
| `--mode` | `-m` | browse, export | Security mode (`Sign`, `SignAndEncrypt`). Mandatory when --security ≠ `None`. | - |
| `--cert` | - | browse, export | Client certificate path (required for security) | - |
| `--key` | - | browse, export | Private key path (required for security) | - |
| `--user` | `-u` | browse, export | Username for authentication | - |
| `--password` | `-p` | browse, export | Password for authentication - never logged. | - |

### Security Policies

Security policy for encrypted communication with the OPC UA server.

**Available Policies:**

| Policy | Encryption | Recommendation | OPC UA Version |
|--------|------------|----------------|----------------|
| `None` | No encryption | Testing only, trusted networks | All |
| `Basic128Rsa15` | RSA 1024-bit | **Deprecated** - Legacy only | 1.0 |
| `Basic256` | RSA 2048-bit | **Deprecated** - Legacy only | 1.0 |
| `Basic256Sha256` | RSA 2048-bit + SHA256 | **Recommended** for general use | 1.02+ |
| `Aes128_Sha256_RsaOaep` | AES-128 + SHA256 | Modern, good performance | 1.04+ |
| `Aes256_Sha256_RsaPss` | AES-256 + SHA256 | **Maximum security** | 1.04+ |

### Browse Command

**Usage:**

```bash
python -m opc_browser.cli browse --server-url opc.tcp://localhost:4840 --depth 3 --security Basic256Sha256 --mode SignAndEncrypt --cert certificates/client_cert.pem --key certificates/client_key.pem
```

**Note:** `--mode` is required when `--security` is not `None`.

### Browse Examples

#### Example 1: Basic Connection (No Authentication)

```bash
python -m opc_browser.cli browse --server-url opc.tcp://localhost:4840
```

**Output:**
- Connects to server without credentials
- Browses from RootFolder (i=84)
- Maximum depth of 3 levels
- Displays tree with node types, names, and IDs

#### Example 2: Custom Starting Node with Depth

```bash
python -m opc_browser.cli browse -s opc.tcp://localhost:4840 -n "ns=2;i=1000" -d 5
```

**Behavior:**
- Starts from custom node `ns=2;i=1000`
- Explores up to 5 levels deep
- Shows namespace prefix for non-standard namespaces

#### Example 3: Username/Password Authentication

```bash
python -m opc_browser.cli browse -s opc.tcp://192.168.1.100:4840 -u admin -p password123
```

**Use Case:**
- Server requires user authentication
- No encryption (suitable for trusted networks)

#### Example 4: Secure Connection with Certificates

```bash
python -m opc_browser.cli browse -s opc.tcp://secure-server.com:4840 --security Basic256Sha256 --mode SignAndEncrypt --cert certificates/client_cert.pem --key certificates/client_key.pem -u operator -p secure_pass
```

Sample output excerpt:

```
📊 SUMMARY:
   • Total Nodes: 33
   • Max Depth: 3
   • Namespaces: 3

📈 NODE TYPES:
   🔢 DataType: 1
   ⚙️ Method: 2
   📁 Object: 20
   📦 ObjectType: 3
   🔗 ReferenceType: 1
   📊 Variable: 5
   📈 VariableType: 1

🌐 NAMESPACES:
   [0] http://opcfoundation.org/UA/
       └─ 31 nodes
   [1] urn:WSM-01153:Studio:OpcUaServer
   [2] urn:Studio
       └─ 2 nodes

🌳 NODE TREE:
----------------------------------------------------------------------------------------------------
📁 Root
   💡 NodeId: i=84
│  └─ 📁 Views
│     💡 NodeId: i=87
│  └─ 📁 Objects
│     💡 NodeId: i=85
│  │  └─ 📁 Server
│  │  │  └─ 📊 ServerArray [String]
│  │  │  └─ 📊 NamespaceArray [String]
│  │  │  └─ 📊 ServerStatus [Type862]
│  │  │  └─ 📊 ServiceLevel [Byte]
│  │  │  └─ 📁 Namespaces
│  │  │  └─ 📊 Auditing [Boolean]
│  │  │  └─ 📁 ServerCapabilities
│  │  │  └─ 📁 ServerDiagnostics
│  │  │  └─ 📁 VendorServerInfo
│  │  │  └─ 📁 ServerRedundancy
│  │  │  └─ ⚙️ GetMonitoredItems
│  │  │  └─ ⚙️ ResendData
│  │  └─ 📁 Studio [ns=2;s=Studio]
│  │  │  └─ 📁 Tags [ns=2;s=Studio.Tags]
│  └─ 📁 Types
│     💡 NodeId: i=86
│  │  └─ 📁 DataTypes
│  │  │  └─ 📁 OPC Binary
│  │  │  └─ 📁 XML Schema
│  │  │  └─ 🔢 BaseDataType
│  │  └─ 📁 EventTypes
│  │  │  └─ 📦 BaseEventType
│  │  └─ 📁 InterfaceTypes
│  │  │  └─ 📦 BaseInterfaceType
│  │  └─ 📁 ObjectTypes
│  │  │  └─ 📦 BaseObjectType
│  │  └─ 📁 ReferenceTypes
│  │  │  └─ 🔗 References
│  │  └─ 📁 VariableTypes
│  │  │  └─ 📈 BaseVariableType
----------------------------------------------------------------------------------------------------
```

### Export Command

Persist the address space to structured files suitable for analytics, dashboards, or archival.

```bash
python -m opc_browser.cli export --server-url opc.tcp://localhost:4840 --format json --include-values --full-export --output export/my_space.json
```

### Export Extra Arguments

| Extra Argument | Short | Description | Default |
|----------------|-------|-------------|---------|
| `--format`     | `-f` | Target format (`csv`, `json`, `xml`). Auto-detected from `--output` if omitted. | `csv` |
| `--output`     | `-o` | Output file path | `export/opcua_export_<timestamp>.<format>` |
| `--namespaces-only` | - | Export only namespace-related nodes | `False` |
| `--include-values` | - | Include current variable values | `False` |
| `--full-export` | - | Include extended attributes (see [Extended Attributes](#extended-attributes)). | `False` |

### Extended Attributes

When `--full-export` is specified, the exporter captures additional node attributes:

| Attribute Name | Description |
|----------------|-------------|
| Description | A human-readable description of the node. |
| AccessLevel | The access level of the node (e.g., `CurrentRead`, `CurrentWrite`). |
| UserAccessLevel | The user-specific access level. |
| WriteMask | The write mask for the node, indicating which attributes can be written. |
| UserWriteMask | The user-specific write mask. |
| EventNotifier | Indicates if the node can be used to generate events. |
| Executable | Indicates if the node is executable (for methods). |
| UserExecutable | The user-specific executable flag. |
| MinimumSamplingInterval | The minimum sampling interval for the node. |
| Historizing | Indicates if the node is historized. |

See [docs/EXPORT_FORMATS.md](docs/EXPORT_FORMATS.md) (generated from
[`docs/EXPORT_FORMATS.py`](docs/EXPORT_FORMATS.py)) for the exhaustive field
reference.

**Usage:**
```bash
# Export as JSON
python -m opc_browser.cli export -s opc.tcp://server:4840 --format json

# Export as XML
python -m opc_browser.cli export -s opc.tcp://server:4840 --format xml -o mydata.xml
```

### Filtering by Namespace

**Use `--node-id` to start browsing from a specific namespace node:**

#### Step 1: Identify the Namespace Node

```bash
# Browse with depth 2 to see namespace structure
python -m opc_browser.cli browse -s opc.tcp://localhost:4840 -d 2
```

> Detailed field mappings, format-specific examples, and value reference tables are documented in
> [docs/EXPORT_FORMATS.md](docs/EXPORT_FORMATS.md).

### Export Examples

### Example 1: Export to JSON with values

```bash
python -m opc_browser.cli export -s opc.tcp://localhost:4840 -f json --include-values -o mydata.json
```

**Result:**
- All nodes exported to `mydata.json`
- Current values included for Variable nodes
- Full metadata and namespace information

### Example 2: Export to CSV for Excel analysis

```bash
python -m opc_browser.cli export -s opc.tcp://server:4840 -f csv -o analysis.csv
```

**Result:**
- UTF-8 CSV with BOM for spreadsheet compatibility
- One row per node with base attributes (add `--full-export` for extended fields)
- Ideal for quick filtering and pivot tables in Excel or LibreOffice

### Example 3: Export to XML for enterprise integration

```bash
python -m opc_browser.cli export -s opc.tcp://server:4840 -f xml --include-values
```

**Result:**
- Auto-generated filename (unless `--output` is provided)
- XML document containing metadata, namespaces, and nodes
- Includes values for variables when `--include-values` is set
- Suitable for downstream XML tooling or validation workflows

### Generate Certificate Command

Create self-signed client certificates aligned with OPC UA security policies.

```bash
python -m opc_browser.cli generate-cert --dir certificates --application-uri "urn:example.org:FreeOpcUa:opcua-asyncio" --hostname localhost --hostname my-workstation --days 365
```

| Argument | Description | Default |
|----------|-------------|---------|
| `--dir` | Certificate output directory | `certificates` |
| `--cn`, `--common-name` | Certificate Common Name | `OPC UA Python Client` |
| `--org`, `--organization` | Organization Name | `My Organization` |
| `--country` | Country code (2 letters) | `IT` |
| `--hostname` | Hostname/DNS (can be repeated) | `localhost` + auto-detected hostname |
| `--uri`, `--application-uri` | OPC UA Application URI | `urn:example.org:FreeOpcUa:opcua-asyncio` |
| `--days` | Certificate validity in days | `365` |

### Important Notes

✅ **All arguments are optional** with sensible defaults  
🔄 **Auto-detection**: `--hostname` automatically includes `localhost` and local computer name  
🔖 **Default URI**: Matches asyncua's internal Application URI  
📌 **Custom URI**: Use `--uri` if server requires specific Application URI  
🏷️ **Multiple Hostnames**: Use `--hostname` multiple times for multi-host certificates

### Certificate Examples

#### Example 1: Default Certificate Generation (Recommended)

```bash
python -m opc_browser.cli generate-cert
```

**Output:**
- `certificates/client_cert.pem` - Client certificate (PEM format)
- `certificates/client_key.pem` - Private key (PEM format)
- `certificates/client_cert.der` - Certificate (DER format for some servers)

**Features:**
- 2048-bit RSA key
- 365-day validity
- Default Application URI compatible with asyncua
- Localhost + local hostname in SAN

#### Example 2: Custom Application URI

```bash
python -m opc_browser.cli generate-cert --uri "urn:mycompany:opcua:client"
```

**Best For:**
- Aligning the certificate with server-side Application URI validation
- Interoperability with servers enforcing strict URI matching

#### Example 3: Production Certificate

```bash
python -m opc_browser.cli generate-cert --uri "urn:factory:scada:client" --hostname production-server --hostname backup-server --hostname 192.168.1.100 --cn "Factory SCADA Client" --org "ACME Corporation" --country "US" --days 730
```

**Features:**
- 2-year validity
- Multiple hostnames for failover
- Custom organization details
- Production-grade configuration

#### Example 4: Testing Environment

```bash
python -m opc_browser.cli generate-cert --dir test_certs --cn "Test Client" --days 30
```

**Best For:**
- Short-lived test certificates
- Isolated test directory
- Development environments

### Using Generated Certificates

Apply certificates in browse/export commands:

```bash
python -m opc_browser.cli browse --server-url opc.tcp://server:4840 --security Basic256Sha256 --mode SignAndEncrypt --cert certificates/client_cert.pem --key certificates/client_key.pem
```

### Certificate Information

Generated certificates include:
- **Subject Alternative Names (SAN)**: Application URI, DNS names, IP addresses
- **Key Usage**: Digital signature, key encipherment, data encipherment
- **Extended Key Usage**: Client authentication, server authentication
- **Formats**: PEM (for asyncua) and DER (for some servers)

---

## Testing and Quality Assurance

The repository bundles an opinionated test and linting pipeline:

| Command | Scope |
|---------|-------|
| `pytest -v` | Async integration tests covering browse and export flows. |
| `pytest --cov=src/opc_browser` | Coverage report (XML/HTML) for CI visibility. |
| `ruff check src tests` | Linting with auto-fixes for style and correctness issues. |
| `black src tests` | Code formatting with 88-character lines. |
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
