# Changelog

All notable changes to the Dolibarr MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Clarified cross-platform installation instructions, including Visual Studio developer shell usage on Windows.
- Trimmed runtime dependencies to match the actual imports and exposed developer extras for the test tooling.

## [1.1.0] - 2024-05-22

### Removed
- Legacy helper scripts, installers and manual test programs that duplicated the automated test-suite
- Alternative server implementations (`simple_client`, `standalone_server`, `ultra_simple_server`) in favour of the single `dolibarr_mcp_server`
- Redundant documentation fragments and variant requirements files that no longer reflected the current project layout

### Changed
- Rewrote the README to highlight the streamlined structure and provide concise installation/run instructions
- Clarified that `dolibarr_mcp_server.py` is the definitive MCP entry point

## [1.0.0] - 2024-01-26

### 🎯 Major Restructuring

This release represents a complete restructuring of the Dolibarr MCP Server to match the clean architecture of prestashop-mcp.

### Added
- Professional README.md with comprehensive documentation
- Structured test suite in `tests/` directory
- Clean configuration management
- Docker support for easy deployment
- Comprehensive CRUD operations for all Dolibarr entities

### Changed
- Complete repository restructuring to match prestashop-mcp pattern
- Simplified dependencies in requirements.txt
- Cleaned up package structure in `src/dolibarr_mcp/`
- Updated pyproject.toml with proper metadata
- Streamlined .gitignore file

### Removed
- Outdated prototype assets from the first public release

### Technical Improvements
- Single, focused MCP server implementation
- Clean separation of concerns
- Better error handling
- Improved logging
- Async/await architecture throughout

## [0.5.0] - 2024-01-20

### Added
- Initial Dolibarr API integration
- Basic CRUD operations for customers, products, invoices
- MCP server implementation
- Docker configuration

## [0.1.0] - 2024-01-15

### Added
- Initial project setup
- Basic repository structure
- License and documentation

---

**Note**: This changelog focuses on the major restructuring in v1.0.0 to align with prestashop-mcp's clean architecture.
