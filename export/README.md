# Export Directory

This directory contains the files produced by the
[Export Command](../README.md#export-command).

## Usage

- Each invocation of `python -m opc_browser.cli export ...` writes the
  selected format (`csv`, `json`, or `xml`) into this folder unless a custom
  `--output` path is provided.
- Files are safe to delete once they have been archived or processed.
- Large exports can be redirected elsewhere using the `--output` flag.

_The CLI creates the directory automatically if it is missing._
