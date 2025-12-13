# Changelog

All notable changes to SLS-AH will be documented in this file.

## [2.0d] - 2025-12-13 (Development Version)

### 🎉 Major Release - Complete Refactor

### Added
- **Encrypted Credential Storage**: Credentials are now encrypted using AES-256-GCM instead of plaintext .env files
  - Machine-specific encryption keys derived from system ID
  - Automatic migration from old `.env` format
  - Credentials stored in `~/.config/slsah/credentials.enc`
- **Game Search by Name**: Search Steam store by game name - no need to memorize App IDs!
  - Integrated Steam search API
  - Display up to 10 search results
  - Easy selection from search results
- **Retry Logic with Exponential Backoff**: API calls now automatically retry on failure
  - Configurable max retries (default: 3)
  - Exponential backoff strategy
  - Rate limit handling
- **Modular Architecture**: Code reorganized into clean, maintainable modules
  - `lib/credentials.py`: Encrypted credential management
  - `lib/steam_api.py`: Steam Web API with retry logic
  - `lib/config_manager.py`: SLSsteam YAML configuration
  - `lib/ui.py`: Rich library UI components
- **Comprehensive Online Fix Guide**: Built-in guide with known compatible games
  - Fighting games (Street Fighter V, Mortal Kombat 11, etc.)
  - Co-op games (Portal 2, Left 4 Dead 2, etc.)
  - Strategy games (Civilization VI, Age of Empires II, etc.)
  - Troubleshooting tips and disclaimers
- **Version Information**: New `--version` flag to display version info
- **Command Line Options**: 
  - `--version`: Display version information
  - `--clear-credentials`: Clear stored credentials

### Changed
- **Improved UI**: Enhanced visual feedback throughout the application
  - Better color coding for success/error/warning messages
  - Cleaner menu layouts
  - Progress spinners for long operations
- **Better Error Handling**: More graceful handling of edge cases
  - Internet connection checks
  - API key validation
  - Malformed YAML configs
- **Enhanced Documentation**: Comprehensive README updates
  - What's new section
  - Installation instructions
  - Usage examples
  - Troubleshooting guide

### Technical Improvements
- Separated concerns into dedicated modules
- Added docstrings throughout codebase
- Improved type hints
- Better separation between legacy and new code
- Rate limiting to avoid API throttling

### Security
- Credentials now encrypted at rest
- No more plaintext API keys in .env files
- Secure file permissions (0600) on sensitive files

### Migration
- Existing `.env` files are automatically detected and migrated
- Old files are backed up as `.env.bak`
- Seamless upgrade experience for existing users

---

## [1.0.0] - Previous Release

### Features
- Generate achievement schemas from Steam Web API
- Support for SLSsteam config integration
- Steam library scanning
- Manual App ID input
- Batch processing modes
- Schema merging and updating
- SLSsteam configuration management
- Online multiplayer fix (FakeAppIds)
- Backup and restore functionality

---

## Future Plans

### Planned for 2.1.0
- [ ] Batch API request optimization
- [ ] Progress bars for batch operations
- [ ] Export/import of AdditionalApps lists
- [ ] Achievement unlock tracking
- [ ] Auto-update check on startup

### Proposed for 3.0.0
- [ ] Optional web dashboard
- [ ] Community game compatibility database
- [ ] Built-in schema verification
- [ ] Multi-language UI support
