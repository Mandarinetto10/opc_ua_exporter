## Exported Fields Reference

All export formats contain the same information, organized differently based on the format.

### Node Fields

Each OPC UA node is exported with the following fields (generated from
[`docs/EXPORT_FORMATS.py`](EXPORT_FORMATS.py)):

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

### Extended Attributes (`--full-export`)

When `--full-export` is enabled, the exporter appends these OPC UA attributes to
each node:

| Field | Type | Description |
|-------|------|-------------|
| **Description** | String | Localized text describing the node |
| **AccessLevel** | String | Bitmask describing current access level |
| **UserAccessLevel** | String | Access level resolved for the authenticated user |
| **WriteMask** | Integer | Bitmask of writable attributes |
| **UserWriteMask** | Integer | User-specific writable attributes |
| **EventNotifier** | Integer | Event subscription capabilities |
| **Executable** | Boolean | Whether a Method node is executable |
| **UserExecutable** | Boolean | Whether a Method node is executable for the authenticated user |
| **MinimumSamplingInterval** | Float | Recommended minimum sampling interval in milliseconds |
| **Historizing** | Boolean | Indicates whether the server historizes values |

### Metadata Fields (JSON & XML)

JSON and XML exports include an additional metadata object describing the
operation:

| Field | Description | Example |
|-------|-------------|---------|
| **TotalNodes** | Total number of nodes exported | `8931` |
| **MaxDepthReached** | Maximum hierarchy depth discovered | `5` |
| **Success** | Whether browse operation succeeded | `true` |
| **ErrorMessage** | Error details if browse failed | `null` or error text |
| **ExportTimestamp** | When the export was created | `2025-11-05T09:34:59.198601` |
| **FullExport** | Whether `--full-export` was enabled | `true` |

### Namespace Fields (JSON & XML)

JSON and XML exports include a dedicated namespace list. CSV embeds the
namespace index on each node row instead of a separate section.

| Field | Description | Example |
|-------|-------------|---------|
| **Index** | Namespace numeric index | `0`, `1`, `2` |
| **URI** | Namespace URI identifier | `http://opcfoundation.org/UA/` |

---

## Format Examples

### CSV Format

**Structure:**
- UTF-8 with BOM for Excel compatibility
- Comma-delimited (`,`) with automatic quoting
- One header row describing the exported fields
- Additional columns appear when `--full-export` is enabled

**Example:**
```csv
NodeId,BrowseName,DisplayName,FullPath,NodeClass,DataType,Value,ParentId,Depth,NamespaceIndex,IsNamespaceNode,Timestamp
"ns=2;s=Studio",Studio,Studio,Studio,Object,,,0,2,False,2025-11-05T09:34:35.737218
"ns=2;s=Studio.Tags",Tags,Tags,Studio/Tags,Object,,"ns=2;s=Studio",1,2,False,2025-11-05T09:34:35.738245
"ns=2;s=Studio.Tags.System.Date",Date,Date,Studio/Tags/System/Date,Variable,String,,"ns=2;s=Studio.Tags.System",3,2,False,2025-11-05T09:34:35.744225
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

