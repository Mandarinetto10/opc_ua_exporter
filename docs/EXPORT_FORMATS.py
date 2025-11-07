"""Structured definition of export fields for documentation tooling.

This module centralises the list of fields emitted by the exporter so
`docs/EXPORT_FORMATS.md` and other documentation can stay in sync with the
implementation.  Run the module directly to emit ready-to-copy Markdown
fragments.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Field:
    """Describe an exported field."""

    name: str
    type: str
    description: str
    always_present: bool | None = None


BASE_NODE_FIELDS: tuple[Field, ...] = (
    Field("NodeId", "String", "Unique identifier for the node", True),
    Field("BrowseName", "String", "Qualified name used for browsing", True),
    Field("DisplayName", "String", "Human-readable name for UI display", True),
    Field("FullPath", "String", "Complete hierarchical path from RootFolder", True),
    Field("NodeClass", "String", "OPC UA node classification", True),
    Field("DataType", "String", "Data type for Variable nodes", False),
    Field("Value", "Any", "Current value when `--include-values` is set", False),
    Field("ParentId", "String", "NodeId of the parent node", False),
    Field("Depth", "Integer", "Hierarchy depth level (0 = RootFolder)", True),
    Field("NamespaceIndex", "Integer", "Namespace index (0 = OPC UA base)", True),
    Field("IsNamespaceNode", "Boolean", "Whether the node contains namespace metadata", True),
    Field("Timestamp", "ISO 8601", "Collection timestamp for the node payload", True),
)

FULL_EXPORT_FIELDS: tuple[Field, ...] = (
    Field("Description", "String", "Localized description of the node"),
    Field("AccessLevel", "String", "Bitmask representing the current access level"),
    Field("UserAccessLevel", "String", "Access level resolved for the authenticated user"),
    Field("WriteMask", "Integer", "Bitmask describing writable attributes"),
    Field("UserWriteMask", "Integer", "User-specific writable attribute mask"),
    Field("EventNotifier", "Integer", "Event subscription capabilities"),
    Field("Executable", "Boolean", "Whether a Method node is executable"),
    Field("UserExecutable", "Boolean", "Executable flag for the authenticated user"),
    Field("MinimumSamplingInterval", "Float", "Recommended minimum sampling interval in ms"),
    Field("Historizing", "Boolean", "Indicates whether the server historises values"),
)

METADATA_FIELDS: tuple[Field, ...] = (
    Field("TotalNodes", "Integer", "Total number of exported nodes"),
    Field("MaxDepthReached", "Integer", "Maximum hierarchy depth discovered"),
    Field("Success", "Boolean", "Whether browsing completed without errors"),
    Field("ErrorMessage", "String", "Error description when `Success` is false"),
    Field("ExportTimestamp", "ISO 8601", "Timestamp of the export operation"),
    Field("FullExport", "Boolean", "Indicates whether `--full-export` was enabled"),
)

NAMESPACE_FIELDS: tuple[Field, ...] = (
    Field("Index", "Integer", "Namespace numeric index"),
    Field("URI", "String", "Namespace URI"),
)


def _format_table(fields: Iterable[Field], include_presence: bool = False) -> str:
    rows: list[str] = []
    if include_presence:
        header = "| Field | Type | Description | Always Present |"
        separator = "|-------|------|-------------|----------------|"
        for field in fields:
            presence = "✅ Yes" if field.always_present else "❌ No"
            rows.append(
                f"| **{field.name}** | {field.type} | {field.description} | {presence} |"
            )
    else:
        header = "| Field | Type | Description |"
        separator = "|-------|------|-------------|"
        for field in fields:
            rows.append(f"| **{field.name}** | {field.type} | {field.description} |")

    body = "\n".join(rows)
    return f"{header}\n{separator}\n{body}"


def main() -> None:
    """Print Markdown tables for documentation authors."""

    print("# Node Fields\n")
    print(_format_table(BASE_NODE_FIELDS, include_presence=True))
    print("\n# Extended Attributes ( --full-export )\n")
    print(_format_table(FULL_EXPORT_FIELDS))
    print("\n# Metadata Fields (JSON & XML)\n")
    print(_format_table(METADATA_FIELDS))
    print("\n# Namespace Fields (JSON & XML)\n")
    print(_format_table(NAMESPACE_FIELDS))


if __name__ == "__main__":
    main()
