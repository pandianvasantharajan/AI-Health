# Migration from requirements.txt to Poetry

## What Changed

The AI Health Service has been migrated from using `requirements.txt` to Poetry for dependency management. All functionality remains exactly the same.

### Benefits of Poetry:

- **Dependency Resolution**: Automatic dependency conflict resolution
- **Lock File**: `poetry.lock` ensures reproducible builds
- **Virtual Environment Management**: Automatic virtual environment handling
- **Build System**: Integrated package building and publishing
- **Development Dependencies**: Separate dev dependencies from production
- **Script Management**: Define and run custom scripts

### Files Changed:

#### Added:
- ✅ `pyproject.toml` - Poetry configuration and dependencies
- ✅ `poetry.lock` - Lock file for reproducible builds (auto-generated)

#### Updated:
- ✅ `Dockerfile` - Now uses Poetry instead of pip
- ✅ `setup.sh` - Updated to install and use Poetry
- ✅ `README.md` - Updated installation and usage instructions
- ✅ `.dockerignore` - Updated to exclude Poetry-specific files

#### Kept (for compatibility):
- ✅ `requirements.txt` - Kept for reference, but no longer used

### Migration Commands:

If you want to export Poetry dependencies back to requirements.txt:
```bash
poetry export -f requirements.txt --output requirements.txt
```

### Usage Changes:

**Before (requirements.txt):**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

**After (Poetry):**
```bash
poetry install
poetry shell
python run.py
# or
poetry run python run.py
```

### Docker:

Docker builds now use Poetry but the final image and functionality remain identical.

All existing Docker commands work exactly the same:
```bash
docker-compose up --build
```

The migration is completely transparent to end users - all API endpoints, functionality, and behavior remain unchanged.