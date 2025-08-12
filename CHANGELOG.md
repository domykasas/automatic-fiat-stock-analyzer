# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enhanced rate limiting and session management for Yahoo Finance
- Better error handling and retry logic for network requests
- Session rotation to prevent rate limiting

### Changed
- Improved project structure and documentation
- Better version control and release management

## [1.0.6] - 2024-12-19

### Added
- Integrated version.py into calculator.py for centralized version management
- Enhanced rate limiting system with adaptive delays
- Session rotation mechanism to prevent Yahoo Finance rate limiting
- Better error detection and handling for rate limit scenarios
- Adaptive delay system based on consecutive failures

### Fixed
- Yahoo Finance rate limit issues causing all stocks to be skipped
- "No listed options on Yahoo Finance or data fetch failed (rate limit)" errors
- Inefficient request timing leading to API throttling
- Session exhaustion from repeated requests

### Changed
- Increased base delays between requests (1.0s instead of 0.35s)
- Implemented exponential backoff with jitter for retries
- Added session pool rotation to distribute load
- Enhanced retry logic with rate limit detection
- Improved error handling and user feedback

## [1.0.5] - 2024-12-19

### Added
- Centralized version management with `version.py` file
- Comprehensive CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) guidelines
- Enhanced project documentation and README.md
- Dynamic version reading in GitHub Actions workflow
- Better project structure and organization

### Changed
- Updated README.md with comprehensive project information
- Centralized version number in single source of truth
- Enhanced workflow to read version from version.py
- Improved project documentation and user experience

## [1.0.4] - 2024-12-19

### Added
- Enhanced PyInstaller spec file with comprehensive dependency collection
- Extensive hidden imports for yfinance, curl_cffi, and related libraries
- Better debugging and error handling for macOS builds
- Enhanced macOS packaging with .dmg file creation verification

### Fixed
- Missing .dmg file creation on macOS builds
- Rate limit errors in packaged binaries
- Incomplete dependency bundling causing stock data fetch failures
- Version consistency across all workflow steps

### Changed
- Updated PyInstaller configuration to include all necessary dependencies
- Enhanced build process with better error reporting
- Improved macOS packaging reliability

## [1.0.3] - 2024-12-19

### Fixed
- Versioning logic in GitHub Actions workflow
- Release tag naming to use actual version numbers instead of "latest"
- Main branch to use proper semantic versioning

### Changed
- Updated release step to create proper version tags (v1.0.3)
- Fixed main branch version from 'latest' to actual version number
- Ensured proper versioning throughout the entire workflow

## [1.0.2] - 2024-12-19

### Fixed
- Binary file naming to include actual version numbers
- Release tag naming consistency
- Workflow version variable usage

### Changed
- Binary names now reflect actual versions (e.g., FiatTradeCalculator-1.0.2-Windows-x64.exe)
- Release tags use proper semantic versioning

## [1.0.1] - 2024-12-19

### Fixed
- PyInstaller binary renaming errors
- Linux packaging file path issues
- Workflow artifact upload path mismatches

### Changed
- Updated PyInstaller spec file to generate versioned names directly
- Enhanced packaging steps with better file detection
- Improved error handling in build process

## [1.0.0] - 2024-12-19

### Added
- Version numbering to binary file names
- Enhanced PyInstaller configuration
- Better cross-platform compatibility

### Changed
- Bumped version to v1.0.0
- Updated PyInstaller spec file with versioned naming
- Enhanced workflow reliability

## [0.1.9] - 2024-12-19

### Fixed
- macOS app bundle path issues
- ditto command errors during packaging
- Workflow file path inconsistencies

### Changed
- Enhanced macOS packaging steps
- Better error handling for app bundle detection
- Improved workflow robustness

## [0.1.8] - 2024-12-19

### Fixed
- Infinite loading bug in Windows test executable step
- Start-Process parameter errors
- Timeout mechanism implementation

### Changed
- Implemented robust timeout mechanisms for executable testing
- Separated Windows and Linux test steps
- Enhanced error handling in test procedures

## [0.1.7] - 2024-12-19

### Fixed
- Spec file not found errors during PyInstaller execution
- Workflow fallback mechanisms for missing spec files
- Build process reliability

### Changed
- Added spec file verification steps
- Implemented fallback to command-line PyInstaller
- Enhanced debugging output

## [0.1.6] - 2024-12-19

### Fixed
- Clean previous builds errors on Windows workflows
- rm -rf command compatibility issues
- Cross-platform command differences

### Changed
- Implemented OS-specific cleanup commands
- Added Windows PowerShell compatibility
- Enhanced workflow cross-platform support

## [0.1.5] - 2024-12-19

### Fixed
- Rate limit errors in compiled binaries
- PyInstaller dependency bundling issues
- yfinance and curl_cffi import problems

### Added
- Hidden import flags for PyInstaller
- Collect-all flags for critical dependencies
- Enhanced dependency management

### Changed
- Updated PyInstaller build commands
- Enhanced dependency collection
- Improved binary reliability

## [0.1.4] - 2024-12-19

### Added
- Initial PyInstaller configuration
- Basic GitHub Actions workflow
- Cross-platform build support

### Changed
- Project structure for binary distribution
- Build process automation
- Release management

## [0.1.3] - 2024-12-19

### Added
- Basic stock analysis functionality
- Yahoo Finance integration
- GUI interface with PySimpleGUI

### Changed
- Core application features
- User interface improvements
- Data fetching capabilities

## [0.1.2] - 2024-12-19

### Added
- Initial project setup
- Basic requirements and dependencies
- Project documentation

## [0.1.1] - 2024-12-19

### Added
- Project initialization
- Basic file structure
- Development environment setup

## [0.1.0] - 2024-12-19

### Added
- Initial project creation
- Basic project structure
- Version control setup
