# SLS-AH Version 2.0 - Testing Guide

## What's Been Changed

This document provides a testing guide for the new v2.0 features.

### New Architecture

The codebase has been refactored into a modular structure:

```
SLSah-1/
├── slsah.py                 # New main entry point
├── __version__.py           # Version information
├── lib/
│   ├── __init__.py
│   ├── credentials.py       # Encrypted credential management
│   ├── steam_api.py         # Steam API with retry logic
│   ├── config_manager.py    # YAML config handling
│   └── ui.py                # Rich UI components
├── generate_schema_from_api.py  # Legacy (still used)
└── sls_manager.py               # Legacy (still used)
```

## Testing Checklist

### 1. Installation Testing
- [ ] Fresh install on dev branch
- [ ] Existing installation upgrade path
- [ ] Dependencies install correctly (including new `tenacity`)

### 2. Credential Management Testing

#### New User Flow
```bash
python slsah.py
# Should prompt for credentials and encrypt them
```

#### Migration Flow
```bash
# If you have an existing .env file, it should:
# 1. Detect the old .env
# 2. Migrate to encrypted storage
# 3. Backup .env as .env.bak
```

#### Credential Commands
```bash
# Show version
python slsah.py --version

# Clear credentials
python slsah.py --clear-credentials
```

### 3. Game Search Feature

**How to Test:**
1. Run `python slsah.py`
2. Select option `4` (Search for game by name)
3. Enter a game name (e.g., "Portal 2")
4. Should display up to 10 results
5. Select a game by number
6. Should proceed to generate schema

**Test Cases:**
- [ ] Search for common game (e.g., "Portal 2")
- [ ] Search for obscure game
- [ ] Search with typos
- [ ] Cancel search with 'b'

### 4. Retry Logic Testing

The API client now automatically retries failed requests. To test:

**Simulate Network Issues:**
```python
# You can temporarily disable network, then:
python slsah.py
# Select option to generate schema
# Should see retry messages with exponential backoff
```

**What to Look For:**
- Retry messages show delay time
- Exponential backoff (1s, 2s, 4s, etc.)
- Maximum 3 retries before giving up
- Graceful error handling

### 5. Online Fix Guide

**How to Test:**
1. Run `python slsah.py`
2. Select option `8` (View Online Fix Guide)
3. Should display comprehensive guide with:
   - What it is and how it works
   - List of known compatible games by category
   - Troubleshooting tips
   - Disclaimers

### 6. UI Improvements

**Visual Feedback:**
- [ ] Success messages in green with ✓
- [ ] Error messages in red with ✗
- [ ] Warning messages in yellow with ⚠
- [ ] Info messages in blue with ℹ
- [ ] Clean menu layouts
- [ ] Progress spinners during operations

### 7. Security Testing

**Credential Storage:**
```bash
# After setting up credentials, check:
ls -la ~/.config/slsah/

# Should see:
# credentials.enc (permissions 600)
# salt.bin (permissions 600)
```

**Verify Encryption:**
```bash
# Credentials file should not be readable as plaintext
cat ~/.config/slsah/credentials.enc
# Should show encrypted gibberish

# Old .env should be backed up or removed
ls .env*
# Should show .env.bak if migration occurred
```

### 8. Backward Compatibility

**Legacy Features Should Still Work:**
- [ ] Generate from SLSsteam config (option 1)
- [ ] Scan Steam library (option 2)
- [ ] Manual App ID input (option 3)
- [ ] Manage SLSsteam App List (option 6)
- [ ] Purge generated schemas (option 7)

### 9. Error Handling

**Test Error Scenarios:**
- [ ] Invalid App ID
- [ ] No internet connection
- [ ] Invalid API key
- [ ] Rate limiting (make many quick requests)
- [ ] Corrupted config files
- [ ] Missing permissions

## Expected Behavior Changes

### Credential Storage Location

**Before v2.0:**
```
.env file in project directory (plaintext)
```

**After v2.0:**
```
~/.config/slsah/credentials.enc (encrypted)
~/.config/slsah/salt.bin (encryption salt)
```

### First Run Experience

**Before v2.0:**
- Prompted for credentials
- Saved to .env in plaintext

**After v2.0:**
- Prompted for credentials
- Encrypted and saved to ~/.config/slsah/
- API key verified before saving
- Clear success feedback

### Entry Point

**Before v2.0:**
```bash
python generate_schema_from_api.py
```

**After v2.0:**
```bash
python slsah.py  # New modular entry point
# OR
./run.sh         # Updated to use slsah.py
```

## Known Issues / Limitations

1. **Gradual Migration**: The new code uses the old modules for some functionality - this is intentional for a smooth transition
2. **Backward Compatibility**: Old .env files are supported but will be migrated on first run
3. **Python Version**: Requires Python 3.7+ (check with `python --version`)

## Reporting Issues

If you find any bugs or issues:

1. Check the CHANGELOG.md for known issues
2. Try `python slsah.py --clear-credentials` to reset
3. Check logs and error messages
4. Report on GitHub with:
   - Python version
   - OS version
   - Steps to reproduce
   - Error messages

## Success Criteria

Version 2.0 is working correctly if:

✅ Credentials are encrypted (can't read them in plaintext)
✅ Old .env files are migrated automatically  
✅ Game search returns relevant results
✅ API failures trigger automatic retries
✅ Online fix guide displays properly
✅ All legacy features still work
✅ UI is clean and informative
✅ Version flag works (`--version`)

## Performance Notes

The new retry logic may make operations slightly slower on poor connections, but this is intentional for reliability. Each retry has:
- 1st retry: ~2 second delay
- 2nd retry: ~4 second delay  
- 3rd retry: ~8 second delay

This ensures transient network issues don't cause failures.
