# OPC UA Exporter

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![asyncua](https://img.shields.io/badge/asyncua-latest-green.svg)](https://github.com/FreeOpcUa/opcua-asyncio)
[![Tests](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/tests.yml/badge.svg)](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/tests.yml)
[![Code Quality](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/code-quality.yml/badge.svg)](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/code-quality.yml)
[![Type Check](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/type-check.yml/badge.svg)](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/type-check.yml)
[![Coverage](https://img.shields.io/codecov/c/github/Mandarinetto10/opc_ua_exporter?label=coverage&logo=codecov)](https://app.codecov.io/gh/Mandarinetto10/opc_ua_exporter)
[![Last Commit](https://img.shields.io/github/last-commit/Mandarinetto10/opc_ua_exporter?logo=github)](https://github.com/Mandarinetto10/opc_ua_exporter/commits/main)
[![Issues](https://img.shields.io/github/issues/Mandarinetto10/opc_ua_exporter?logo=github)](https://github.com/Mandarinetto10/opc_ua_exporter/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/Mandarinetto10/opc_ua_exporter?logo=github)](https://github.com/Mandarinetto10/opc_ua_exporter/pulls)
[![Repo Size](https://img.shields.io/github/repo-size/Mandarinetto10/opc_ua_exporter?logo=github)](https://github.com/Mandarinetto10/opc_ua_exporter)
[![Stars](https://img.shields.io/github/stars/Mandarinetto10/opc_ua_exporter?style=social)](https://github.com/Mandarinetto10/opc_ua_exporter/stargazers)
[![Forks](https://img.shields.io/github/forks/Mandarinetto10/opc_ua_exporter?style=social)](https://github.com/Mandarinetto10/opc_ua_exporter/network/members)
[![Contributors](https://img.shields.io/github/contributors/Mandarinetto10/opc_ua_exporter)](https://github.com/Mandarinetto10/opc_ua_exporter/graphs/contributors)
[![Commit Activity](https://img.shields.io/github/commit-activity/m/Mandarinetto10/opc_ua_exporter)](https://github.com/Mandarinetto10/opc_ua_exporter/graphs/commit-activity)
[![Open in Visual Studio Code](https://img.shields.io/badge/Open%20in-VS%20Code-blue?logo=visualstudiocode)](https://open.vscode.dev/Mandarinetto10/opc_ua_exporter)

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

The project includes a **comprehensive test suite with 100% code coverage** for all critical modules. Tests are organized using pytest with async support, extensive mocking, and detailed coverage reporting.

### Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared pytest fixtures (mocks, sample data)
├── test_browser.py             # Browser module tests (100% coverage)
├── test_client.py              # Client connection tests (96% coverage)
├── test_models.py              # Data models tests (100% coverage)
├── test_strategies.py          # Export strategies tests (100% coverage)
├── test_exporter.py            # Export context tests (94% coverage)
├── test_cli.py                 # CLI interface tests (90% coverage)
├── test_generate_cert.py       # Certificate generation tests (97% coverage)
└── test_integration.py         # Integration tests with real OPC UA server (optional)
```

### Quick Start Testing

```bash
# Install test dependencies (if not already installed)
pip install -r requirements.txt

# Run all tests with coverage - Complete test suite
pytest

# Run all tests with verbose output and detailed coverage
pytest -v --cov=src/opc_browser --cov-report=term-missing --cov-report=html --cov-branch

# Run tests and open HTML coverage report in browser
pytest --cov-report=html && open htmlcov/index.html  # macOS
pytest --cov-report=html && start htmlcov/index.html  # Windows
pytest --cov-report=html && xdg-open htmlcov/index.html  # Linux
```

### Running Tests - Basic Commands

#### Single-Line Test Execution Examples

```bash
# Complete test suite with coverage report
pytest -v --cov=src/opc_browser --cov-report=term-missing --cov-branch

# All unit tests (skip integration) with HTML coverage
pytest -v -m "not integration" --cov=src/opc_browser --cov-report=html --cov-report=term-missing

# Full test suite with XML + HTML + terminal coverage
pytest -v --cov=src/opc_browser --cov-report=xml --cov-report=html --cov-report=term-missing --cov-branch

# Quick test run (no coverage, just pass/fail)
pytest -v --no-cov -x

# Verbose tests with short traceback on failure
pytest -v --tb=short --cov-report=term-missing

# Run tests and show slowest 10 tests
pytest -v --durations=10 --cov-report=term-missing

# Parallel test execution (requires pytest-xdist)
pytest -v -n auto --cov=src/opc_browser --cov-report=html

# Watch mode - rerun tests on file changes (requires pytest-watch)
ptw -- -v --cov=src/opc_browser --cov-report=term-missing
```

#### Standard Testing Commands

```bash
# Run all tests
pytest

# Run all tests with verbose output
pytest -v

# Run tests with detailed coverage report
pytest --cov=src/opc_browser --cov-report=term-missing

# Run specific test file
pytest tests/test_browser.py

# Run only unit tests (skip integration tests)
pytest -m "not integration"

# Run only integration tests (requires OPC UA server)
pytest -m integration

# Run specific test class
pytest tests/test_browser.py::TestBrowseOperation

# Run specific test function
pytest tests/test_browser.py::TestBrowseOperation::test_browse_success

# Run tests matching pattern
pytest -k "test_browse"

# Run only async tests
pytest -m asyncio

# Skip slow tests
pytest -m "not slow"

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Quiet mode (less output)
pytest -q
```

### Coverage Reports

#### Generate Different Coverage Report Types

```bash
# Terminal report with missing lines
pytest --cov-report=term-missing

# HTML coverage report (open in browser)
pytest --cov-report=html
# Then open: htmlcov/index.html

# XML coverage report (for CI/CD, Codecov, SonarQube)
pytest --cov-report=xml

# Generate all report types at once
pytest --cov-report=term-missing --cov-report=html --cov-report=xml

# Coverage with branch analysis
pytest --cov-branch --cov-report=term-missing

# Detailed coverage with annotated source
pytest --cov-report=annotate

# Run without coverage (faster for debugging)
pytest --no-cov
```

### Module-Specific Testing

#### Test Individual Modules

```bash
# Browser module only
pytest tests/test_browser.py -v --cov=src/opc_browser/browser.py --cov-report=term-missing

# Client module only
pytest tests/test_client.py -v --cov=src/opc_browser/client.py --cov-report=term-missing

# All export strategies
pytest tests/test_strategies.py -v --cov=src/opc_browser/strategies --cov-report=term-missing

# Models data classes
pytest tests/test_models.py -v --cov=src/opc_browser/models.py --cov-report=term-missing

# CLI interface
pytest tests/test_cli.py -v --cov=src/opc_browser/cli.py --cov-report=term-missing

# Certificate generation
pytest tests/test_generate_cert.py -v --cov=src/opc_browser/generate_cert.py --cov-report=term-missing

# Exporter context
pytest tests/test_exporter.py -v --cov=src/opc_browser/exporter.py --cov-report=term-missing
```

### Integration Tests

Integration tests verify functionality against a **real OPC UA server** running on `opc.tcp://localhost:4840`.

#### Setup for Integration Tests

1. **Start OPC UA server** on default port 4840
2. **Verify server is running:**
   ```bash
   # Test server connectivity
   python -c "import asyncio; from asyncua import Client; asyncio.run(Client('opc.tcp://localhost:4840').connect())"
   ```
3. **Run integration tests:**
   ```bash
   pytest -m integration -v
   ```

#### Available Integration Tests

```bash
# Run ALL integration tests with coverage
pytest -m integration -v --cov=src/opc_browser --cov-report=term-missing

# Test basic browse operation
pytest tests/test_integration.py::test_real_browse_basic -v

# Test browse with value reading
pytest tests/test_integration.py::test_real_browse_with_values -v

# Test custom starting node
pytest tests/test_integration.py::test_real_browse_custom_node -v

# Test namespace filtering
pytest tests/test_integration.py::test_real_namespaces_only_filter -v

# Test deep browsing (max_depth=5)
pytest tests/test_integration.py::test_real_deep_browse -v

# Test full attribute export
pytest tests/test_integration.py::test_real_full_export_attributes -v

# Test connection lifecycle
pytest tests/test_integration.py::test_real_client_connection_lifecycle -v

# Test error handling
pytest tests/test_integration.py::test_real_invalid_node_id -v

# Run all integration tests in parallel (faster)
pytest -m integration -n auto -v
```

#### Integration Test Output Example

```bash
$ pytest -m integration -v --cov-report=term-missing

========================= test session starts ==========================
platform linux -- Python 3.10.12, pytest-7.4.3, pluggy-1.3.0
cachedir: .pytest_cache
rootdir: /home/user/opc_ua_exporter
configfile: pyproject.toml
plugins: asyncio-0.21.1, cov-4.1.0
collected 8 items / 199 deselected / 8 selected

tests/test_integration.py::test_real_browse_basic PASSED           [12%]
tests/test_integration.py::test_real_browse_with_values PASSED     [25%]
tests/test_integration.py::test_real_browse_custom_node PASSED     [37%]
tests/test_integration.py::test_real_namespaces_only_filter PASSED [50%]
tests/test_integration.py::test_real_deep_browse PASSED            [62%]
tests/test_integration.py::test_real_full_export_attributes PASSED [75%]
tests/test_integration.py::test_real_client_connection_lifecycle PASSED [87%]
tests/test_integration.py::test_real_invalid_node_id PASSED        [100%]

========================== 8 passed in 12.34s ==========================
```

#### No Server Available?

If no OPC UA server is running, integration tests are **automatically skipped**:

```bash
$ pytest -m integration -v

tests/test_integration.py::test_real_browse_basic SKIPPED          [12%]
reason: OPC UA server not available on localhost:4840

========================== 8 skipped in 0.12s ==========================
```

**This is expected behavior** - integration tests never fail due to missing server.

### Code Quality Tools

#### Linting with Ruff

```bash
# Check all code quality issues
ruff check src/ tests/

# Check and auto-fix safe issues
ruff check --fix src/ tests/

# Check and auto-fix including unsafe fixes
ruff check --unsafe-fixes --fix src/ tests/

# Check specific file
ruff check src/opc_browser/browser.py

# Show all violations with full details
ruff check --output-format=full src/ tests/

# Check only specific rules (e.g., imports)
ruff check --select I src/

# Complete quality check with auto-fix and verbose output
ruff check src/ tests/ --unsafe-fixes --fix --output-format=full
```

#### Formatting with Black

```bash
# Check if code needs formatting
black --check src/ tests/

# Apply formatting to all files
black src/ tests/

# Format specific file
black src/opc_browser/browser.py

# Show diff without applying changes
black --diff src/

# Format with verbose output
black -v src/ tests/

# Complete format check and application
black --check src/ tests/
black src/ tests/
```

#### Type Checking with MyPy

```bash
# Run type checking on source code
mypy src/

# Type check specific module
mypy src/opc_browser/browser.py

# Strict mode type checking
mypy --strict src/

# Type check with error summary
mypy src/ --error-summary

# Generate HTML type coverage report
mypy src/ --html-report mypy_report/

# Check without errors on missing imports
mypy src/ --ignore-missing-imports

# Complete type check with all reports
mypy src/ --ignore-missing-imports --html-report mypy_report/ --any-exprs-report mypy_coverage/
```

### Complete Quality Check Pipeline

Run all quality checks in one command (CI/CD simulation):

```bash
# Full quality check pipeline
pytest -v --cov=src/opc_browser --cov-report=term-missing --cov-report=html --cov-branch && \
ruff check src/ tests/ --output-format=full && \
black --check src/ tests/ && \
mypy src/ --ignore-missing-imports

# OR with auto-fix for linting and formatting
pytest -v --cov=src/opc_browser --cov-report=html && \
ruff check --fix src/ tests/ && \
black src/ tests/ && \
mypy src/
```

### Continuous Integration (CI/CD)

The project uses **GitHub Actions** for automated testing on every push and pull request.

#### CI Workflow Coverage

| Workflow | Python Versions | Operating Systems | What It Tests |
|----------|----------------|-------------------|---------------|
| **Tests** | 3.10, 3.11, 3.12 | Ubuntu, Windows, macOS | Unit tests, coverage, branch coverage |
| **Code Quality** | 3.10 | Ubuntu | Ruff linting, Black formatting |
| **Type Check** | 3.10, 3.11, 3.12 | Ubuntu | MyPy type checking (normal + strict) |

#### Viewing CI Results

1. **Go to GitHub repository**
2. **Click "Actions" tab**
3. **View workflow runs:**
   - ✅ Green checkmark = All tests passed
   - ❌ Red X = Tests failed (click for details)
   - 🟡 Yellow dot = In progress

#### Running CI Tests Locally

Simulate GitHub Actions environment:

```bash
# Run tests as CI would (Python 3.10, Ubuntu)
pytest -v --cov=src/opc_browser --cov-report=xml --cov-branch -m "not integration"

# Check Python version matches CI (3.10)
python --version

# Install exact dependencies from requirements.txt
pip install -r requirements.txt --force-reinstall
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
    """Test description with expected behavior."""
    # Arrange - Set up test data and mocks
    browser = OpcUaBrowser(client=mock_client)
    mock_client.get_namespace_array = AsyncMock(return_value=["http://opcfoundation.org/UA/"])
    
    # Act - Execute the feature being tested
    result = await browser.my_new_method()
    
    # Assert - Verify expected outcomes
    assert result.success is True
    assert result.total_nodes > 0
    mock_client.get_namespace_array.assert_called_once()
```

#### Using Fixtures

```python
# Reuse existing fixtures from conftest.py
def test_with_multiple_fixtures(mock_client, mock_node, mock_variable_node, sample_result):
    """Tests can combine multiple fixtures."""
    browser = OpcUaBrowser(client=mock_client)
    # Test implementation with pre-configured mocks
```

#### Async Test Best Practices

```python
@pytest.mark.asyncio
async def test_async_operation(mock_client):
    """Always mark async tests with @pytest.mark.asyncio."""
    # Create async mocks for async methods
    mock_node = AsyncMock()
    mock_node.read_browse_name = AsyncMock(return_value=browse_name)
    
    # Await all async calls
    result = await browser.browse(start_node_id="i=84")
    
    # Await mock verification
    await mock_node.read_browse_name()
    
    # Assertions
    assert result.success is True
```

### Test Coverage Goals

| Module | Current Coverage | Goal | Status |
|--------|-----------------|------|--------|
| `browser.py` | 100% | 100% | ✅ Achieved |
| `models.py` | 100% | 100% | ✅ Achieved |
| `strategies/` | 100% | 100% | ✅ Achieved |
| `client.py` | 96% | 95%+ | ✅ Achieved |
| `exporter.py` | 94% | 90%+ | ✅ Achieved |
| `generate_cert.py` | 97% | 95%+ | ✅ Achieved |
| `cli.py` | 90% | 90%+ | ✅ Achieved |
| **Overall** | **95%+** | **90%+** | ✅ Achieved |

### Test Best Practices

1. **Isolation** - Each test should be independent and not rely on others
2. **Naming** - Use descriptive names: `test_browse_with_valid_node_id_returns_success`
3. **AAA Pattern** - Arrange, Act, Assert structure for clarity
4. **Mocking** - Mock external dependencies (OPC UA server, file I/O, network)
5. **Coverage** - Aim for 90%+ coverage, 100% for critical paths
6. **Performance** - Mark slow tests with `@pytest.mark.slow`
7. **Documentation** - Add docstrings explaining what each test verifies
8. **Parametrization** - Use `@pytest.mark.parametrize` for testing multiple inputs
9. **Fixtures** - Share common setup via fixtures in `conftest.py`
10. **Assertions** - One logical assertion per test when possible

### Troubleshooting Tests

#### Common Issues and Solutions

**Issue: AsyncIO warnings about unawaited coroutines**
```python
# ❌ Problem
mock_node.get_children()  # Missing await

# ✅ Solution
await mock_node.get_children()
mock_node.get_children = AsyncMock(return_value=[])
await mock_node.get_children()
```

**Issue: Loguru output not captured in tests**
```python
# ✅ Solution: Reconfigure loguru for tests (in conftest.py)
from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, format="{message}", level="INFO", colorize=False)
```

**Issue: Coverage not showing 100% despite all tests passing**
```bash
# Check which lines are missing
pytest --cov-report=term-missing

# View detailed HTML report
pytest --cov-report=html
open htmlcov/index.html

# Check branch coverage
pytest --cov-branch --cov-report=term-missing
```

**Issue: Tests passing locally but failing in CI**
```bash
# Run tests exactly as CI does
pytest -v --cov=src/opc_browser --cov-report=xml --cov-branch -m "not integration"

# Check Python version matches CI (3.10)
python --version

# Install exact dependencies from requirements.txt
pip install -r requirements.txt --force-reinstall
```

**Issue: Integration tests failing**
```bash
# Verify OPC UA server is running
python -c "import asyncio; from asyncua import Client; asyncio.run(Client('opc.tcp://localhost:4840').connect())"

# Check server logs for connection errors
# Ensure server allows anonymous or test user connections
# Verify firewall isn't blocking port 4840
```

### Performance Testing

```bash
# Show 10 slowest tests
pytest --durations=10

# Show all test durations
pytest --durations=0

# Run only fast tests (skip slow ones)
pytest -m "not slow"

# Profile test execution
pytest --profile

# Benchmark specific test
pytest tests/test_browser.py::test_browse_deep -v --benchmark
```

### Test Reports

#### Generate Test Reports for Documentation

```bash
# JUnit XML report (for CI/CD integration)
pytest --junitxml=test-results.xml

# HTML test report (human-readable)
pytest --html=test-report.html --self-contained-html

# Combined coverage + test report
pytest --cov=src_opc_browser --cov-report=html --html=test-report.html
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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.