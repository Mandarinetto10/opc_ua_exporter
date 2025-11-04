# Setup Guide - OPC UA Exporter

This guide provides detailed instructions for setting up the development environment and installing all necessary dependencies for the OPC UA Exporter project.

## Prerequisites

- **Python 3.10 or higher** installed on your system
- **pip** (Python package installer)
- **git** (optional, for cloning the repository)

### Verify Python Version

```bash
python --version
# or
python3 --version
```

If your version is lower than 3.10, upgrade Python before proceeding.

## Step 1: Clone or Download the Project

### Option A: Clone with Git

```bash
git clone https://github.com/Mandarinetto10/opc_ua_exporter.git
cd opc_ua_exporter
```

### Option B: Download and Extract

Download the project as a ZIP archive and extract it to a local directory.

## Step 2: Create Virtual Environment

Creating a virtual environment isolates the project dependencies from the global Python system.

### On Linux/macOS

```bash
python3 -m venv .venv
```

### On Windows

```cmd
python -m venv .venv
```

## Step 3: Activate Virtual Environment

### On Linux/macOS

```bash
source .venv/bin/activate
```

### On Windows (Command Prompt)

```cmd
.venv\Scripts\activate.bat
```

### On Windows (PowerShell)

```powershell
.venv\Scripts\Activate.ps1
```

**Note:** If you receive a policy error on Windows PowerShell, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Once activated, you should see `(.venv)` at the beginning of your shell prompt.

## Step 4: Upgrade pip

```bash
pip install --upgrade pip
```

## Step 5: Install Dependencies

### Basic Installation

```bash
pip install -r requirements.txt
```

### Development Mode Installation (with optional dependencies)

```bash
pip install -e ".[dev]"
```

This command installs the package in "editable" mode, allowing you to modify the code without reinstalling.

## Step 6: Verify Installation

Check that all dependencies have been installed correctly:

```bash
pip list
```

You should see the following libraries listed:
- `asyncua`
- `loguru`
- `cryptography`

## Step 7: Test Installation

Verify that the CLI is accessible:

```bash
python -m opc_browser.cli --help
```

You should see the help output with all available commands and options.

## Step 8: Generate Certificates (Optional but Recommended)

Generate self-signed certificates for secure OPC UA connections:

```bash
python -m opc_browser.cli generate-cert
```

This creates certificates in the `certificates/` directory.

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution:** Make sure the virtual environment is activated and all dependencies have been installed correctly.

### Issue: Permission Errors During Installation

**Solution on Linux/macOS:**
```bash
pip install --user -r requirements.txt
```

### Issue: Dependency Conflicts

**Solution:** Recreate the virtual environment from scratch:

```bash
deactivate
rm -rf .venv  # Linux/macOS
# or
rmdir /s .venv  # Windows

python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: OpenSSL Errors on Windows

**Solution:** Ensure you have the latest version of Python 3.10+ which includes updated OpenSSL libraries.

## Deactivate Virtual Environment

When you're done working on the project:

```bash
deactivate
```

## Support

For issues or questions:
- Check the documentation in [README.md](README.md)
- Verify system requirements
- Consult the official [asyncua documentation](https://github.com/FreeOpcUa/opcua-asyncio)
- Open an issue on [GitHub](https://github.com/Mandarinetto10/opc_ua_exporter/issues)