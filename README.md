# Fiat Trade Calculator

A powerful stock analysis tool that provides automated analysis of stock options and trading strategies using Yahoo Finance data.

## Features

- **Automated Stock Analysis**: Analyze multiple stocks simultaneously with intelligent filtering
- **Yahoo Finance Integration**: Real-time data fetching with rate limit handling
- **Options Analysis**: Comprehensive options chain analysis and filtering
- **Cross-Platform**: Available for Windows, macOS, and Linux
- **User-Friendly GUI**: Built with PySimpleGUI for easy interaction

## Installation

### From Source

1. Clone the repository:
```bash
git clone https://github.com/domykasas/automatic-fiat-stock-analyzer.git
cd automatic-fiat-stock-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python calculator.py
```

### Pre-built Binaries

Download the latest release binaries from the [Releases page](https://github.com/domykasas/automatic-fiat-stock-analyzer/releases):

- **Windows**: `FiatTradeCalculator-{version}-Windows-x64.exe`
- **macOS**: `FiatTradeCalculator-{version}-macOS-x64.dmg`
- **Linux**: `FiatTradeCalculator-{version}-Linux-x64.tar.gz`

## Usage

1. Launch the application
2. Click "Start Auto Analysis" to begin
3. The tool will automatically:
   - Fetch stock data from Yahoo Finance
   - Analyze options chains
   - Filter for profitable opportunities
   - Display results in an organized format

## Requirements

- Python 3.11+
- Internet connection for Yahoo Finance data
- Sufficient RAM for large datasets

## Dependencies

- `yfinance`: Yahoo Finance data fetching
- `curl_cffi`: HTTP requests with browser impersonation
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations
- `scipy`: Scientific computing functions
- `PySimpleGUI`: User interface
- `lxml`, `bs4`, `html5lib`: HTML parsing

## Development

### Building from Source

The project uses PyInstaller for creating standalone executables:

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller FiatTradeCalculator.spec
```

### Version Management

The project uses a centralized version system:
- **`version.py`**: Single source of truth for version information
- **`CHANGELOG.md`**: Comprehensive change history following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) guidelines
- **Semantic Versioning**: Follows [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html) specification

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Update the CHANGELOG.md if needed
5. Submit a pull request

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes and improvements.

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues:
1. Check the [CHANGELOG.md](CHANGELOG.md) for known issues
2. Review the [Issues](https://github.com/domykasas/automatic-fiat-stock-analyzer/issues) page
3. Create a new issue with detailed information about your problem

## Current Version

**Version**: 1.0.5

For the latest updates and release notes, see the [Releases page](https://github.com/domykasas/automatic-fiat-stock-analyzer/releases).
