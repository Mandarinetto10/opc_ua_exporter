# Certificates Directory

This directory stores client certificates and private keys created by the
[Generate Certificate Command](../README.md#generate-certificate-command).

## Usage

- Run `python -m opc_browser.cli generate-cert` to populate this folder with
  PEM/DER certificates and the corresponding private key.
- Share only the public certificate (`*.pem` / `*.der`) with the OPC UA server.
- Keep private keys secret — **never** commit them to version control.
- You may safely delete the contents when rotating credentials; rerun the
  generator to obtain new files.

_The CLI creates the directory automatically if it is missing._
