# OPC UA Exporter

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![asyncua](https://img.shields.io/badge/asyncua-latest-green.svg)](https://github.com/FreeOpcUa/opcua-asyncio)
[![Tests](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/tests.yml/badge.svg)](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/tests.yml)
[![Code Quality](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/code-quality.yml/badge.svg)](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/code-quality.yml)
[![Type Check](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/type-check.yml/badge.svg)](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/type-check.yml)

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
  - [Connection Errors](#connection-errors)
  - [Node ID Errors](#node-id-errors)
  - [Security Errors](#security-errors)
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
python -m opc_browser.cli browse -s opc.tcp://localhost:48010 -d 2
```

## Exported Fields Reference

All export formats contain the same information, organized differently based on the format.

### Node Fields

Each OPC UA node is exported with the following fields:

| Field | Type | Description | Example | Always Present |
|-------|------|-------------|---------|----------------|
| **NodeId** | String | Unique identifier for the node | `ns=2;s=Studio` | ✅ Yes |
| **BrowseName** | String | Qualified name used for browsing | `Studio` | ✅ Yes |
| **DisplayName** | String | Human-readable name for UI display | `Studio Control` | ✅ Yes |
| **FullPath** | String | Complete hierarchical path from root | `Studio/Tags/System/Date` | ✅ Yes |
| **NodeClass** | String | OPC UA node classification | `Object`, `Variable`, `Method` | ✅ Yes |
| **DataType** | String | Data type for Variable nodes | `String`, `Int32`, `Double` | ❌ Variables only |
| **Value** | Any | Current value (if `--include-values`) | `23.5`, `"Hello"`, `true` | ❌ Optional |
| **ParentId** | String | NodeId of parent node | `ns=2;s=Studio.Tags` | ❌ Root nodes = null |
| **Depth** | Integer | Hierarchy depth level (0 = root) | `0`, `1`, `2`, `3` | ✅ Yes |
| **NamespaceIndex** | Integer | Namespace index (0 = OPC UA base) | `0`, `1`, `2` | ✅ Yes |
| **IsNamespaceNode** | Boolean | True if node is namespace metadata | `true`, `false` | ✅ Yes |
| **Timestamp** | ISO 8601 | When the node data was captured | `2025-11-05T09:34:35.737218` | ✅ Yes |

### Metadata Fields

Export metadata included in all formats:

| Field | Description | Example |
|-------|-------------|---------|
| **TotalNodes** | Total number of nodes exported | `8931` |
| **MaxDepthReached** | Maximum hierarchy depth discovered | `5` |
| **Success** | Whether browse operation succeeded | `true` |
| **ErrorMessage** | Error details if browse failed | `null` or error text |
| **ExportTimestamp** | When the export was created | `2025-11-05T09:34:59.198601` |

### Namespace Fields

Namespace definitions included in all formats:

| Field | Description | Example |
|-------|-------------|---------|
| **Index** | Namespace numeric index | `0`, `1`, `2` |
| **URI** | Namespace URI identifier | `http://opcfoundation.org/UA/` |

---

## Format Examples

### CSV Format

**Structure:**
- UTF-8 with BOM for Excel compatibility
- Comma-delimited (`,`
- Auto-quoted fields containing special characters
- Summary section at bottom
- Namespace table at bottom

**Example:**
```csv
NodeId,BrowseName,DisplayName,FullPath,NodeClass,DataType,Value,ParentId,Depth,NamespaceIndex,IsNamespaceNode,Timestamp
"ns=2;s=Studio",Studio,Studio,Studio,Object,,,0,2,False,2025-11-05T09:34:35.737218
"ns=2;s=Studio.Tags",Tags,Tags,Studio/Tags,Object,,"ns=2;s=Studio",1,2,False,2025-11-05T09:34:35.738245
"ns=2;s=Studio.Tags.System.Date",Date,Date,Studio/Tags/System/Date,Variable,String,,"ns=2;s=Studio.Tags.System",3,2,False,2025-11-05T09:34:35.744225

# Summary
Total Nodes,8931
Max Depth,5
Namespaces,3

# Namespaces
Index,URI
0,http://opcfoundation.org/UA/
1,urn:WSM-01153:Studio:OpcUaServer
2,urn:Studio
```

**Best For:**
- ✅ Excel/LibreOffice Calc analysis
- ✅ SQL database import
- ✅ Simple text processing
- ✅ Quick data inspection

---

### JSON Format

**Structure:**
- Pretty-printed with 2-space indentation
- ISO 8601 timestamps
- Hierarchical object structure
- Arrays for nodes and namespaces

**Example:**
```json
{
  "metadata": {
    "total_nodes": 8931,
    "max_depth_reached": 5,
    "success": true,
    "error_message": null,
    "export_timestamp": "2025-11-05T09:34:59.198601"
  },
  "namespaces": [
    {
      "index": 0,
      "uri": "http://opcfoundation.org/UA/"
    },
    {
      "index": 2,
      "uri": "urn:Studio"
    }
  ],
  "nodes": [
    {
      "node_id": "ns=2;s=Studio",
      "browse_name": "Studio",
      "display_name": "Studio",
      "full_path": "Studio",
      "node_class": "Object",
      "data_type": null,
      "value": null,
      "parent_id": null,
      "depth": 0,
      "namespace_index": 2,
      "is_namespace_node": false,
      "timestamp": "2025-11-05T09:34:35.737218"
    },
    {
      "node_id": "ns=2;s=Studio.Tags.System.Date",
      "browse_name": "Date",
      "display_name": "Date",
      "full_path": "Studio/Tags/System/Date",
      "node_class": "Variable",
      "data_type": "String",
      "value": null,
      "parent_id": "ns=2;s=Studio.Tags.System",
      "depth": 3,
      "namespace_index": 2,
      "is_namespace_node": false,
      "timestamp": "2025-11-05T09:34:35.744225"
    }
  ]
}
```

**Best For:**
- ✅ Web applications and REST APIs
- ✅ JavaScript/TypeScript consumption
- ✅ NoSQL databases (MongoDB, CouchDB)
- ✅ Configuration files
- ✅ Easy parsing in any language

---

### XML Format

**Structure:**
- XML declaration with UTF-8 encoding
- 2-space indentation for readability
- Hierarchical element structure
- Separate sections for metadata, namespaces, and nodes

**Example:**
```xml
<?xml version='1.0' encoding='utf-8'?>
<OpcUaAddressSpace>
  <Metadata>
    <TotalNodes>8931</TotalNodes>
    <MaxDepthReached>5</MaxDepthReached>
    <Success>True</Success>
    <ExportTimestamp>2025-11-05T09:34:31.634634</ExportTimestamp>
  </Metadata>
  <Namespaces>
    <Namespace>
      <Index>0</Index>
      <URI>http://opcfoundation.org/UA/</URI>
    </Namespace>
    <Namespace>
      <Index>2</Index>
      <URI>urn:Studio</URI>
    </Namespace>
  </Namespaces>
  <Nodes>
    <Node>
      <NodeId>ns=2;s=Studio</NodeId>
      <BrowseName>Studio</BrowseName>
      <DisplayName>Studio</DisplayName>
      <FullPath>Studio</FullPath>
      <NodeClass>Object</NodeClass>
      <Depth>0</Depth>
      <NamespaceIndex>2</NamespaceIndex>
      <IsNamespaceNode>False</IsNamespaceNode>
      <Timestamp>2025-11-05T09:34:11.816635</Timestamp>
    </Node>
    <Node>
      <NodeId>ns=2;s=Studio.Tags.System.Date</NodeId>
      <BrowseName>Date</BrowseName>
      <DisplayName>Date</DisplayName>
      <FullPath>Studio/Tags/System/Date</FullPath>
      <NodeClass>Variable</NodeClass>
      <DataType>String</DataType>
      <ParentId>ns=2;s=Studio.Tags.System</ParentId>
      <Depth>3</Depth>
      <NamespaceIndex>2</NamespaceIndex>
      <IsNamespaceNode>False</IsNamespaceNode>
      <Timestamp>2025-11-05T09:34:11.821636</Timestamp>
    </Node>
  </Nodes>
</OpcUaAddressSpace>
```

**Best For:**
- ✅ Enterprise integration (SAP, Oracle)
- ✅ SOAP web services
- ✅ Schema validation (XSD)
- ✅ XSLT transformations
- ✅ Legacy systems requiring XML

---

## Field Value Examples

### NodeClass Values

| Value | Description | Typical Attributes |
|-------|-------------|-------------------|
| `Object` | Organizational container | BrowseName, DisplayName |
| `Variable` | Data holder with value | DataType, Value, AccessLevel |
| `Method` | Executable function | InputArguments, OutputArguments |
| `ObjectType` | Template for Objects | IsAbstract |
| `VariableType` | Template for Variables | DataType |
| `DataType` | Data type definition | IsAbstract |
| `ReferenceType` | Relationship definition | IsAbstract, Symmetric |
| `View` | Alternative organization | ContainsNoLoops |

### DataType Values

Common data types you'll see in exports:

| DataType | Description | Example Values |
|----------|-------------|----------------|
| `Boolean` | True/False | `true`, `false` |
| `Byte` | 8-bit unsigned | `0-255` |
| `Int16` | 16-bit signed integer | `-32768` to `32767` |
| `Int32` | 32-bit signed integer | `-2147483648` to `2147483647` |
| `Int64` | 64-bit signed integer | Large integers |
| `UInt16` | 16-bit unsigned | `0` to `65535` |
| `UInt32` | 32-bit unsigned | `0` to `4294967295` |
| `Float` | Single precision | `3.14`, `2.718` |
| `Double` | Double precision | `3.14159265359` |
| `String` | Text | `"Hello World"` |
| `DateTime` | ISO 8601 timestamp | `2025-11-05T09:34:35.737218` |
| `Guid` | UUID identifier | `{12345678-1234-5678-1234-567812345678}` |
| `ByteString` | Binary data | Base64 encoded |

### NamespaceIndex Values

| Index | Standard Meaning | Example URI |
|-------|------------------|-------------|
| `0` | OPC UA base namespace | `http://opcfoundation.org/UA/` |
| `1+` | Server-specific namespaces | `urn:Studio`, `urn:MyCompany:OPC` |

**Note:** Namespace indices are server-specific and may change between servers or restarts.

---

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

### Overview

The project includes a comprehensive test suite with **100% code coverage** for the browser module. Tests are organized using pytest with async support, mocking, and coverage reporting.

### Test Structure

```
tests/
├── __init__.py           # Test package initialization
├── conftest.py           # Shared pytest fixtures
└── test_browser.py       # Browser module tests (100% coverage)
```

### Running Tests

#### Quick Test Commands

```bash
# Run all tests with coverage
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_browser.py

# Run specific test class
pytest tests/test_browser.py::TestBrowseOperation

# Run specific test
pytest tests/test_browser.py::TestBrowseOperation::test_browse_success

# Run tests matching pattern
pytest -k "test_browse"

# Run only async tests
pytest -m asyncio

# Skip slow tests
pytest -m "not slow"
```

#### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov-report=html

# View coverage in browser
# Open htmlcov/index.html

# Generate terminal coverage report only
pytest --cov-report=term-missing

# Generate XML coverage report (for CI/CD)
pytest --cov-report=xml

# Run without coverage (faster)
pytest --no-cov
```

### Test Categories

#### 1. Initialization Tests (`TestOpcUaBrowserInit`)

Tests for browser initialization with various configurations.

```bash
# Run initialization tests
pytest tests/test_browser.py::TestOpcUaBrowserInit -v

# Example tests:
# - test_init_default_params: Default parameters
# - test_init_custom_params: Custom depth, values, filters
# - test_init_zero_depth: Edge case - zero depth
# - test_init_negative_depth: Edge case - negative depth
```

#### 2. Node Validation Tests (`TestNodeValidation`)

Tests for OPC UA Node ID validation logic.

```bash
# Run validation tests
pytest tests/test_browser.py::TestNodeValidation -v

# Example tests:
# - test_validate_node_id_numeric_ns0: i=84
# - test_validate_node_id_numeric_with_ns: ns=2;i=1000
# - test_validate_node_id_string: ns=2;s=MyNode
# - test_validate_node_id_guid: ns=2;g=UUID
# - test_validate_node_id_bytestring: ns=2;b=Base64
# - test_validate_node_id_invalid_formats: Invalid formats
```

#### 3. Namespace Tests (`TestNamespaceOperations`)

Tests for namespace retrieval and filtering.

```bash
# Run namespace tests
pytest tests/test_browser.py::TestNamespaceOperations -v

# Example tests:
# - test_get_namespaces_success: Successful retrieval
# - test_get_namespaces_failure: Connection failure handling
# - test_is_namespace_node_by_keyword: Keyword detection
# - test_is_namespace_node_by_object_id: ObjectId detection
```

#### 4. Browse Operation Tests (`TestBrowseOperation`)

Tests for main browse functionality with various scenarios.

```bash
# Run browse operation tests
pytest tests/test_browser.py::TestBrowseOperation -v

# Example tests:
# - test_browse_success: Successful browse
# - test_browse_custom_start_node: Custom starting node
# - test_browse_invalid_node_id_format: Invalid node ID
# - test_browse_node_not_found: Non-existent node
# - test_browse_with_namespace_filter_valid: Valid filter
# - test_browse_with_namespace_filter_invalid: Invalid filter
# - test_browse_namespaces_only_filter: Namespace-only mode
```

#### 5. Tree Printing Tests (`TestPrintTree`)

Tests for console tree visualization output.

```bash
# Run tree printing tests
pytest tests/test_browser.py::TestPrintTree -v

# Example tests:
# - test_print_tree_success: Successful tree display
# - test_print_tree_failed_browse: Failed browse handling
# - test_print_tree_no_nodes: Empty result handling
# - test_print_tree_node_types_distribution: Type statistics
# - test_print_tree_truncation_warning: Large tree truncation
```

#### 6. Edge Cases Tests (`TestEdgeCases`)

Tests for boundary conditions and error scenarios.

```bash
# Run edge case tests
pytest tests/test_browser.py::TestEdgeCases -v

# Example tests:
# - test_browse_max_depth_zero: Zero depth browsing
# - test_browse_very_deep_tree: Deep hierarchy (10+ levels)
# - test_variable_node_data_type_error: Data type read failure
# - test_variable_node_variant_without_type: Missing VariantType
```

### Code Quality Tools

#### Linting with Ruff

```bash
# Check code quality
ruff check src/ tests/

# Check code quality and auto-fix unsafe issues
ruff check src/ tests/ --unsafe-fixes

# Auto-fix issues
ruff check --fix src/ tests/

# Auto-fix issues including unsafe fixes
ruff check --unsafe-fixes --fix src/ tests/

# Check specific file
ruff check src/opc_browser/browser.py

# Show all violations
ruff check --output-format=full src/
```

#### Formatting with Black

```bash
# Check formatting
black --check src/ tests/

# Apply formatting
black src/ tests/

# Format specific file
black src/opc_browser/browser.py

# Show diff without applying
black --diff src/
```

#### Type Checking with MyPy

```bash
# Run type checking
mypy src/

# Check specific module
mypy src/opc_browser/browser.py

# Strict mode
mypy --strict src/

# Generate HTML report
mypy src/ --html-report mypy_report/
```

### Writing New Tests

#### Example: Testing a New Feature

```python
# filepath: tests/test_my_feature.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from opc_browser.browser import OpcUaBrowser


@pytest.mark.asyncio
async def test_my_new_feature(mock_client):
    """Test description."""
    # Arrange
    browser = OpcUaBrowser(client=mock_client)
    
    # Act
    result = await browser.my_new_method()
    
    # Assert
    assert result.success is True
    assert result.total_nodes > 0
```

#### Using Fixtures

```python
# Reuse existing fixtures from conftest.py
def test_with_fixtures(mock_client, mock_node, mock_variable_node):
    """Tests can use multiple fixtures."""
    browser = OpcUaBrowser(client=mock_client)
    # Test implementation
```

#### Async Test Best Practices

```python
@pytest.mark.asyncio
async def test_async_operation(mock_client):
    """Always mark async tests with @pytest.mark.asyncio."""
    # Await async calls properly
    result = await browser.browse(start_node_id="i=84")
    
    # Mock async methods with AsyncMock
    mock_node = AsyncMock()
    mock_node.read_browse_name = AsyncMock(return_value=browse_name)
    
    # Await mock calls to avoid warnings
    await mock_node.read_browse_name()
```

### Continuous Integration

#### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest
      - run: ruff check src/ tests/
      - run: black --check src/ tests/
      - run: mypy src/
```

### Test Best Practices

1. **Isolation**: Each test should be independent
2. **Naming**: Use descriptive test names (`test_browse_with_valid_node_id`)
3. **Arrange-Act-Assert**: Follow AAA pattern
4. **Mocking**: Mock external dependencies (OPC UA server, file I/O)
5. **Coverage**: Aim for 90%+ coverage for critical modules
6. **Performance**: Mark slow tests with `@pytest.mark.slow`
7. **Documentation**: Add docstrings to test functions

### Troubleshooting Tests

#### Common Issues

**Issue: AsyncIO warnings**
```python
# Fix: Await all async mocks
await mock_node.get_children()
mock_node.get_children = AsyncMock(return_value=[])
```

**Issue: Loguru output not captured**
```python
# Fix: Reconfigure loguru for tests
from loguru import logger
logger.remove()
logger.add(sys.stdout, format="{message}", level="INFO", colorize=False)
```

**Issue: Coverage not 100%**
```bash
# Check missing lines
pytest --cov-report=term-missing

# View detailed HTML report
pytest --cov-report=html
open htmlcov/index.html
```

---

## Troubleshooting

### Connection Errors

#### ❌ "Cannot connect to server"

**Possible Causes:**
- Server is not running
- Incorrect URL format
- Firewall blocking connection
- Wrong port number

**Solutions:**
```bash
# 1. Verify server is running
# 2. Check URL format: opc.tcp://hostname:port
# 3. Test network connectivity
ping hostname

# 4. Check firewall rules (common OPC UA ports: 4840, 48010)
# 5. Try basic connection without security
python -m opc_browser.cli browse -s opc.tcp://localhost:4840
```

---

#### ❌ "Authentication failed"

**Error Hints:**
- `BadIdentityTokenRejected`: Wrong username/password or user doesn't exist
- `BadUserAccessDenied`: User exists but lacks permissions

**Solutions:**
```bash
# 1. Verify credentials
# 2. Check user exists on server
# 3. Confirm user has required permissions
# 4. Try without username/password if server allows anonymous
python -m opc_browser.cli browse -s opc.tcp://server:4840
```

---

#### ❌ "BadSecurityChecksFailed"

**Meaning:** Server rejected the client certificate

**Solutions:**
1. **Generate compatible certificate:**
   ```bash
   python -m opc_browser.cli generate-cert --uri "urn:matching:server:uri"
   ```

2. **Add certificate to server trust list** (server-specific process)

3. **Verify Application URI matches:**
   ```bash
   # Check server requirements for Application URI
   # Generate certificate with matching URI
   python -m opc_browser.cli generate-cert --uri "urn:server:required:uri"
   ```

4. **Check certificate validity:**
   - Not expired
   - Proper format (PEM vs DER)
   - Correct file permissions

---

### Node ID Errors

#### ❌ "BadNodeIdUnknown"

**Meaning:** Specified node doesn't exist in server's address space

**Solutions:**
```bash
# 1. Browse from root to find valid nodes
python -m opc_browser.cli browse -s opc.tcp://server:4840 -d 2

# 2. Look for NodeId hints in output:
#    💡 NodeId: ns=2;i=1000

# 3. Use discovered NodeId
python -m opc_browser.cli browse -s opc.tcp://server:4840 -n "ns=2;i=1000"
```

---

#### ❌ "Invalid Node ID format"

**Valid Formats:**
- `i=84` - Numeric in namespace 0
- `ns=2;i=1000` - Numeric with namespace
- `ns=2;s=MyNode` - String identifier
- `ns=2;g=uuid` - GUID identifier
- `ns=2;b=base64` - Opaque identifier

**Common Mistakes:**
```bash
# ❌ Wrong: Missing identifier after ns=
-n "ns=2"

# ✅ Correct: Complete node ID
-n "ns=2;i=1000"

# ❌ Wrong: Missing ns= prefix for string IDs
-n "s=MyNode"

# ✅ Correct: String ID with namespace
-n "ns=2;s=MyNode"
```

---

### Security Errors

#### ❌ "Certificate and private key are required"

**Meaning:** Security policy requires certificates but none provided

**Solution:**
```bash
# Generate certificates first
python -m opc_browser.cli generate-cert

# Then use in command
python -m opc_browser.cli browse -s opc.tcp://server:4840 --security Basic256Sha256 --mode SignAndEncrypt --cert certificates/client_cert.pem --key certificates/client_key.pem
```

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

This project is licensed under the [MIT License](LICENSE).