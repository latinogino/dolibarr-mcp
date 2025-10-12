# Changelog

All notable changes to the Dolibarr MCP Server are documented here. The project
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and adopts the
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

## [Unreleased]

### Added
- Restored README.md and CHANGELOG.md after merge conflicts while preserving the streamlined structure shared with `prestashop-mcp`.
- Documented platform-specific setup covering Linux/macOS shells, Windows Visual Studio `vsenv`, and the Docker workflow.

### Changed
- Reconciled feature and tool descriptions so they capture both the detailed ERP coverage and the new documentation bundle layout.
- Clarified configuration guidance around `pydantic-settings`, environment variables, and `.env` files.

### Removed
- Obsolete references to legacy helper scripts and superseded documentation variants that were dropped during the repository cleanup.

## [1.1.0] - 2024-05-22

### Removed
- Legacy helper scripts, installers, and manual test programs that duplicated the automated test-suite.
- Alternative server implementations (`simple_client`, `standalone_server`, `ultra_simple_server`) in favour of the single `dolibarr_mcp_server`.
- Redundant documentation fragments and variant requirements files that no longer reflected the current project layout.

### Changed
- Rewrote the README to highlight the streamlined structure and provide concise installation/run instructions.
- Clarified that `dolibarr_mcp_server.py` is the definitive MCP entry point.

## [Unreleased]

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
- Professional README.md with comprehensive documentation.
- Structured test suite in `tests/` directory.
- Clean configuration management.
- Docker support for easy deployment.
- Comprehensive CRUD operations for all Dolibarr entities.

### Changed
- Complete repository restructuring to match prestashop-mcp pattern.
- Simplified dependencies in requirements.txt.
- Cleaned up package structure in `src/dolibarr_mcp/`.
- Updated pyproject.toml with proper metadata.
- Streamlined .gitignore file.

### Removed
- Outdated prototype assets from the first public release.

### Technical Improvements
- Single, focused MCP server implementation.
- Clean separation of concerns.
- Better error handling.
- Improved logging.
- Async/await architecture throughout.

## [0.5.0] - 2024-01-20

### Added
- Initial Dolibarr API integration.
- Basic CRUD operations for customers, products, invoices.
- MCP server implementation.
- Docker configuration.

## [0.1.0] - 2024-01-15

### Added
- Initial project setup.
- Basic repository structure.
- License and documentation.

---

**Note**: Entries prior to v1.0.0 summarise the historical evolution of the project and are retained for context.
