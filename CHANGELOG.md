# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-22

### Added
- Temperature tracking for perishable items (Meat, Dairy, Prepared)
- Modal dialog for temperature data entry (pickup and dropoff temps)
- Clickable scale icon for manual refresh
- Source-filtered history table (last 15 entries per source)
- Source-filtered daily totals showing all food types
- Temperature ranges in CSV reports (min/max combined)
- "lbs" suffix on weight display
- Database migration scripts
- Comprehensive test suite
- CLI tool for manual operations

### Changed
- Removed auto-refresh for smoother UI experience
- Reorganized CSV summary format with temperature items at end
- Updated database schema with temp_pickup_f and temp_dropoff_f columns
- Daily totals now show all food types (0.0 if none logged)
- History table filters by current source only

### Fixed
- Dialog interaction issues caused by auto-refresh
- Temperature dialog now closes properly on save/cancel
- Duplicate selectbox error in report_utils

## [0.1.0] - 2024-XX-XX

### Added
- Initial release
- Basic weight tracking with Dymo scale
- Source and type management
- CSV report generation
- Email delivery of reports
- Undo/redo functionality
- Keyboard shortcuts (Ctrl-Z, Ctrl-Y)
- Streamlit-based UI
- SQLite database backend

[1.0.0]: https://github.com/wyojustin/weighit/releases/tag/v1.0.0
[0.1.0]: https://github.com/wyojustin/weighit/releases/tag/v0.1.0
