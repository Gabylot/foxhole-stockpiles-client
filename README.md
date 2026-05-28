# Foxhole Stockpiles Client

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Windows](https://img.shields.io/badge/platform-windows-blue.svg)](https://www.microsoft.com/windows)

A lightweight desktop client for parsing Foxhole stockpile SAV files and submitting them to an API endpoint.

## Features

- 📂 **SAV File Parsing**: Reads Foxhole `MapData.sav` files using `fs-sav`
- 📋 **Stockpile Filtering**: Automatically filters reserve stockpiles and public base types
- 🚀 **API Submission**: Sends parsed stockpiles to a configurable endpoint with `X-API-TOKEN` auth
- 🖥️ **GUI Configuration**: All settings configurable through the settings window — no manual config editing
- 🔍 **Auto Detection**: Automatically finds your Foxhole `MapData.sav` file
- 🌐 **Multi-language**: Supports English, German, Spanish, French, Portuguese, Russian, Turkish, Chinese

## Requirements

- **Python 3.12 or higher** (for running from source)
- **Windows 10 or 11**
- **[fs-sav](https://github.com/Gabylot/foxhole-stockpiles-client)** executable for parsing SAV files

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Gabylot/foxhole-stockpiles-client.git
   cd foxhole-stockpiles-client
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e .
   ```

## Usage

Run the application from the project root:

```bash
python -m foxhole_stockpiles.main
```

### First Setup

1. The "Process SAV" button starts greyed out
2. Go to **Settings → Configure**
3. Fill in the required fields in the **SAV Watcher** tab:
   - **SAV File Path** — click "Auto Detect" to find your `MapData.sav`, or "Browse" to select it manually
   - **fs-sav Executable** — path to the `fs-sav.exe` parser
   - **Endpoint URL** — the API endpoint to submit stockpiles to
   - **API Token** — the `X-API-TOKEN` for authentication
4. Click **Save** — the button becomes enabled
5. Click **Process SAV** to parse and submit all stockpiles

### Settings Tabs

| Tab | Description |
|-----|-------------|
| **SAV Watcher** | Configure SAV file path, fs-sav executable, endpoint, and API token |
| **Language** | Select your preferred language |

## Project Structure

```
foxhole-stockpiles-client/
├── foxhole_stockpiles/
│   ├── core/              # Configuration and settings
│   ├── i18n/              # Translation files
│   ├── ui/                # User interface (main window + settings)
│   ├── __init__.py        # Package metadata
│   └── main.py            # Application entry point
├── pyproject.toml         # Project configuration
└── README.md
```

## Configuration

All configuration is done through the GUI settings window and saved to `config.json` in the project root.

### SAV Settings

| Field | Description |
|-------|-------------|
| SAV File Path | Path to your Foxhole `MapData.sav` file (auto-detectable) |
| fs-sav Executable | Path to the `fs-sav.exe` parser binary |
| Endpoint URL | API endpoint that accepts stockpile JSON via POST |
| API Token | Token sent as `X-API-TOKEN` header for authentication |

## Building Standalone Executable

```bash
build.cmd
```

The executable will be created in the `dist/` directory.

## Related Projects

- [foxhole-stockpiles](https://github.com/Gabylot/foxhole-stockpiles-client) - The main project repository

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.