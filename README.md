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

A professional, feature-rich CLI tool for browsing and exporting OPC UA server address spaces. Built with SOLID principles, asynchronous design, and comprehensive security support.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Quick Start](#quick-start)
  - [Detailed Setup](#detailed-setup)
- [Usage](#usage)
  - [Overview](#overview)
  - [Browse Command](#browse-command)
    - [Common Arguments](#common-arguments)
    - [Security](#security-1)
    - [Mode](#mode)
    - [Browse Examples](#browse-examples)
    - [Browse Output](#browse-output)
  - [Export Command](#export-command)
    - [Additional Export Arguments](#additional-export-arguments)
    - [Format](#format)
    - [Namespace Filter](#namespace-filter)
    - [Export Examples](#export-examples)
  - [Generate Certificate Command](#generate-certificate-command)
    - [Certificate Arguments](#certificate-arguments)
    - [Certificate Examples](#certificate-examples)
- [Project Structure](#project-structure)
- [Security](#security)
  - [Certificate Management](#certificate-management)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [References](#references)
- [Authors](#authors)
- [License](#license)

---

## Features

- 🌐 **Asynchronous OPC UA Client** - Built on `asyncua` for high performance
- 🔍 **Recursive Browsing** - Navigate address space with configurable depth control
- 📊 **Multi-Format Export** - CSV, JSON, XML via Strategy Pattern
- 🔐 **Complete Authentication** - Username/password + certificate-based security
- 🛡️ **Security Policies** - Support for all OPC UA security levels (Basic256Sha256, AES128/256, etc.)
- 📝 **Professional Logging** - `loguru` integration with contextual error hints
- ⚡ **Robust Error Handling** - Comprehensive exception management with troubleshooting guidance
- 🏗️ **Modular Architecture** - SOLID principles, testable, and extensible
- 🐍 **Type-Safe** - Full type hints for Python 3.10+
- Visual Tree Display - Console tree visualization with emoji icons
- Namespace Filtering - Filter nodes by namespace index
- Hierarchical Paths - Full OPC UA path reconstruction for each node

---

## Requirements

- **Python**: 3.10 or higher
- **OPC UA Server**: Access to a local or remote OPC UA server
- **SSL Certificates**: Required for secure connections (can be auto-generated)

---

## Installation

### Quick Start

```bash
# Clone repository
git clone https://github.com/Mandarinetto10/opc_ua_exporter.git
cd opc_ua_exporter

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate certificates
python -m opc_browser.cli generate-cert

# Verify installation
python -m opc_browser.cli --help
```

### Detailed Setup

For step-by-step installation instructions, see [SETUP.md](SETUP.md).

**Key Installation Steps:**
1. Python 3.10+ installation
2. Virtual environment creation
3. Dependency installation via `requirements.txt`
4. Certificate generation for secure connections
5. Verification of asyncua and cryptography packages

---

## Usage

### Overview

The CLI provides three main commands:

| Command | Description |
|---------|-------------|
| [`browse`](#browse-command) | Navigate and display OPC UA address space tree |
| [`export`](#export-command) | Export address space to file (CSV/JSON/XML) |
| [`generate-cert`](#generate-certificate-command) | Generate self-signed certificates for secure connections |

**General Syntax:**
```bash
python -m opc_browser.cli {browse|export|generate-cert} [OPTIONS]
```

**Important Notes:**
- ✅ All commands display a comprehensive parameter summary at startup
- ⚠️ Connection failures prevent tree display (errors logged with hints)
- 📝 All operations provide detailed logging for troubleshooting

---

## Browse Command

Browse the OPC UA address space and display a visual tree structure in the console.

### Syntax

```bash
python -m opc_browser.cli browse [OPTIONS]
```

### Common Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--server-url` | `-s` | **[Required]** OPC UA server endpoint URL | - |
| `--node-id` | `-n` | Starting node ID for browsing | `i=84` (RootFolder) |
| `--depth` | `-d` | Maximum recursion depth | `3` |
| `--security` | `-sec` | [Security policy](#security-1) | `None` |
| `--mode` | `-m` | [Security mode](#mode) (required if --security != None) | - |
| `--cert` | - | Client certificate path (required for security) | - |
| `--key` | - | Private key path (required for security) | - |
| `--user` | `-u` | Username for authentication | - |
| `--password` | `-p` | Password for authentication | - |

### Security

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

**Usage:**
```bash
python -m opc_browser.cli browse -s opc.tcp://server:4840 --security Basic256Sha256
```

### Mode

Security mode defines the level of protection when using encrypted communication.

**Available Modes:**

| Mode | Description | Use Case |
|------|-------------|----------|
| `Sign` | Digital signature only | Integrity verification without encryption |
| `SignAndEncrypt` | Signature + encryption | **Recommended** - Full protection |

**Usage:**
```bash
python -m opc_browser.cli browse -s opc.tcp://server:4840 --security Basic256Sha256 --mode SignAndEncrypt
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

**Features:**
- SHA256-based security policy
- Encrypted communication
- Certificate-based authentication
- Username/password credentials

#### Example 5: Maximum Security (AES256)

```bash
python -m opc_browser.cli browse -s opc.tcp://factory.com:4840 --security Aes256_Sha256_RsaPss --mode SignAndEncrypt --cert certs/factory_client.pem --key certs/factory_key.pem -u admin -p admin_pass -d 5
```

**Best For:**
- Critical infrastructure
- Regulated industries
- Maximum data protection

### Browse Output

The browse command displays:

1. **Parameter Summary** - All connection settings
2. **Summary Statistics** - Total nodes, depth, namespaces
3. **Node Type Distribution** - Count by type (Object, Variable, etc.)
4. **Namespace List** - All discovered namespaces with node counts
5. **Visual Tree** - Hierarchical structure with:
   - 📁 Objects
   - 📊 Variables with data types and values
   - ⚙️ Methods
   - 📦 Object Types
   - 🔗 References
6. **NodeID Hints** - IDs shown for root and depth-1 nodes

**Example Tree Output:**
```
└── 📁 Objects
    ├── 📁 Server
    │   ├── 📊 ServerStatus [ServerStatusDataType]
    │   ├── 📊 State [ServerState] = Running
    │   └── 📁 Namespaces
    │       💡 NodeId: ns=0;i=2253
    ├── 📁 DeviceSet [ns=2]
    │   ├── 📊 Temperature [Double] = 23.5
    │   └── 📊 Pressure [Double] = 101.3
    └── 👁️ Views
```

---

## Export Command

Export the OPC UA address space to structured file formats (CSV, JSON, XML).

### Syntax

```bash
python -m opc_browser.cli export [OPTIONS]
```

### Additional Export Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--format` | `-f` | [See export formats](#format) | `csv` |
| `--output` | `-o` | Output file path | `export/opcua_export_<timestamp>.<format>` |
| `--namespaces-only` | - | Export only namespace-related nodes | `False` |
| `--include-values` | - | Include current variable values | `False` |


### Format

Export format determines the structure and file type of the exported data.

**Available Formats:**

| Format | Best For | Features |
|--------|----------|----------|
| `csv` | Excel, data analysis | UTF-8 with BOM, comma-delimited, auto-quoted fields |
| `json` | Web apps, APIs | Pretty-printed, ISO timestamps, hierarchical structure |
| `xml` | Enterprise systems | Schema-compliant, indented, metadata sections |

---

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

## Export Examples

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
- Excel-compatible CSV with UTF-8 BOM
- Summary statistics at bottom
- Namespace table included
- Open directly in Excel without import wizard

### Example 3: Export to XML for enterprise integration

```bash
python -m opc_browser.cli export -s opc.tcp://server:4840 -f xml --include-values
```

**Result:**
- Auto-generated filename: `export/opcua_export_20251105_093459.xml`
- Schema-compliant XML structure
- Values included for all variables
- Ready for XSLT transformation or schema validation

---

## Generate Certificate Command

Generate self-signed X.509 certificates for OPC UA client authentication.

### Syntax

```bash
python -m opc_browser.cli generate-cert [OPTIONS]
```

### Certificate Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--dir` | Certificate output directory | `certificates` |
| `--cn`, `--common-name` | Certificate Common Name | `OPC UA Python Client` |
| `--org`, `--organization` | Organization Name | `My Organization` |
| `--country` | Country code (2 letters) | `IT` |
| `--days` | Certificate validity in days | `365` |
| `--uri`, `--application-uri` | OPC UA Application URI | `urn:example.org:FreeOpcUa:opcua-asyncio` |
| `--hostname` | Hostname/DNS (can be repeated) | `localhost` + auto-detected hostname |

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

**Use Case:** Server requires specific Application URI for client validation

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

## Project Structure

```
opc-ua-browser/
├── pyproject.toml              # Project configuration
├── requirements.lock           # Locked dependencies
├── requirements.txt            # Python dependencies
├── SETUP.md                   # Detailed setup guide
├── README.md                  # This file
├── LICENSE                    # MIT License
├── export/                    # Auto-created export directory
│   └── opcua_export_*.{csv,json,xml}
├── certificates/              # Generated certificates
│   ├── client_cert.pem
│   ├── client_key.pem
│   └── client_cert.der
└── src/
    └── opc_browser/
        ├── __init__.py        # Package initialization
        ├── cli.py             # CLI entry point (argparse)
        ├── models.py          # Data models (OpcUaNode, BrowseResult)
        ├── client.py          # OPC UA client wrapper
        ├── browser.py         # Recursive browsing logic
        ├── exporter.py        # Export context (Strategy Pattern)
        ├── generate_cert.py   # Certificate generation
        └── strategies/
            ├── __init__.py
            ├── base.py        # Abstract export strategy
            ├── csv_strategy.py
            ├── json_strategy.py
            └── xml_strategy.py
```

---

## Security

### Certificate Management

#### Automatic Generation (Recommended)

```bash
python -m opc_browser.cli generate-cert
```

**Advantages:**
- Works on Windows, Linux, macOS
- No external tools required
- Proper OPC UA extensions (Application URI in SAN)
- Multiple output formats (PEM, DER)

#### Manual Generation with OpenSSL (Alternative)

```bash
# Create certificates directory
mkdir certificates && cd certificates

# Generate private key (2048-bit RSA)
openssl genrsa -out client_key.pem 2048

# Generate self-signed certificate (365-day validity)
openssl req -new -x509 -key client_key.pem -out client_cert.pem -days 365

# Interactive prompts for certificate details:
# - Country Name (2 letter code): US
# - State or Province Name: California
# - Locality Name: San Francisco
# - Organization Name: My Company
# - Organizational Unit Name: Engineering
# - Common Name: OPC UA Client
# - Email Address: client@example.com
```

#### Server Trust Configuration

For servers requiring certificate trust:

1. **Export client certificate** (already done if using generate-cert)
2. **Add to server's trust list** (server-specific, consult documentation)
3. **Restart server** (if required)
4. **Test connection** with certificate

---

## Testing

Run the full test suite locally with:

```bash
pytest
```

Detailed guidance covering coverage targets, integration setup, and quality tooling lives in [docs/TESTING.md](docs/TESTING.md).

---

## Troubleshooting

Refer to [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for a full catalogue of connection, node ID, and security diagnostics.

---

## Contributing

Contributions are welcome!  
If you find a bug, want to suggest an enhancement, or wish to submit a pull request, please open an issue or PR on [GitHub](https://github.com/Mandarinetto10/opc_ua_exporter).  
Before submitting code, ensure it follows the project's coding standards and includes appropriate tests and documentation.

## References

- [OPC UA Specification](https://reference.opcfoundation.org/)
- [asyncua documentation](https://github.com/FreeOpcUa/opcua-asyncio)
- [Python cryptography](https://cryptography.io/)
- [OPC Foundation](https://opcfoundation.org/)
- [loguru](https://github.com/Delgan/loguru)

## Authors

- Mandarinetto10 - Initial work and ongoing maintenance

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.