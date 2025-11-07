# Hot Reload Configuration Guide

## Why Changes Weren't Reflecting Immediately

The AI Health service wasn't reflecting changes immediately due to missing development configuration in Docker. Here are the issues that were fixed:

### 🔧 **Issues Fixed:**

#### 1. **Missing Volume Mount in Development**
- **Problem**: `docker-compose.dev.yml` was missing volume mount for the backend service
- **Solution**: Added volume mount to sync local code with container

```yaml
# Before (missing volume mount)
ai-health-service:
  build: ./ai-health-service
  # No volume mount = no hot reload

# After (with hot reload)
ai-health-service:
  volumes:
    - ./ai-health-service:/app  # ✅ Hot reload enabled
    - /app/.venv                # ✅ Preserve virtual env
```

#### 2. **FastAPI Hot Reload Not Enabled**
- **Problem**: Production Dockerfile didn't include `--reload` flag
- **Solution**: Created `Dockerfile.dev` with hot reload enabled

```dockerfile
# Before (production command)
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# After (development command with hot reload)
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app"]
```

#### 3. **Missing Development Environment Setup**
- **Problem**: Using production Docker configuration for development
- **Solution**: Separate development Dockerfile and compose configuration

### 🚀 **Hot Reload Now Works For:**

#### **Backend Service (FastAPI)**
- ✅ **Python files** (`.py`) - Auto-reloads FastAPI server
- ✅ **Route changes** - New endpoints available immediately  
- ✅ **Module imports** - New modules detected automatically
- ✅ **Configuration changes** - Settings updated on save

#### **Frontend Service (React)**
- ✅ **JavaScript/TypeScript files** - Hot module replacement
- ✅ **CSS changes** - Styles updated instantly
- ✅ **Component changes** - React components re-render
- ✅ **Asset changes** - Images/static files updated

### 📁 **File Structure for Hot Reload**

```
AI-Health/
├── docker-compose.yml          # Production config
├── docker-compose.dev.yml      # Development config (✅ with hot reload)
├── setup-docker-dev.sh         # New development script
├── ai-health-service/
│   ├── Dockerfile              # Production image
│   ├── Dockerfile.dev          # Development image (✅ with --reload)
│   └── app/
│       ├── routes/
│       │   └── s3_routes.py    # 🔥 Hot reload on changes
│       └── modules/
│           └── *.py            # 🔥 Hot reload on changes
└── ai-health-ui/
    ├── Dockerfile              # Production image  
    ├── Dockerfile.dev          # Development image
    └── src/                    # 🔥 Hot reload on changes
```

### 🏃‍♂️ **How to Use Hot Reload:**

#### **Option 1: Docker Development (Recommended)**
```bash
# Start with hot reload enabled
./setup-docker-dev.sh

# Or manually:
docker-compose -f docker-compose.dev.yml up --build
```

#### **Option 2: Local Development**
```bash
# Traditional local development
./setup-dev.sh
```

### 🔍 **Verification Steps:**

1. **Start development environment:**
   ```bash
   ./setup-docker-dev.sh
   ```

2. **Make a change to the API:**
   - Edit `ai-health-service/app/routes/s3_routes.py`
   - Add a simple print statement or modify a response

3. **Check logs for reload:**
   ```bash
   docker-compose -f docker-compose.dev.yml logs -f ai-health-service
   ```
   
   You should see:
   ```
   INFO:     Waiting for changes...
   INFO:     Detected changes in 's3_routes.py'. Reloading...
   INFO:     Server restarted
   ```

4. **Test the change:**
   - The API should reflect your changes immediately
   - No need to rebuild or restart containers

### 🛠 **Troubleshooting Hot Reload:**

#### **If changes still don't reflect:**

1. **Check volume mounts:**
   ```bash
   docker-compose -f docker-compose.dev.yml config
   ```

2. **Verify file permissions:**
   ```bash
   ls -la ai-health-service/app/routes/s3_routes.py
   ```

3. **Check container logs:**
   ```bash
   docker-compose -f docker-compose.dev.yml logs ai-health-service
   ```

4. **Force rebuild if needed:**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build --force-recreate
   ```

#### **Common Issues:**

- **File permissions**: Ensure files are readable by Docker
- **Volume sync**: On some systems, file watchers may need polling enabled
- **Port conflicts**: Ensure ports 8000 and 3000 are available
- **Container rebuild**: Sometimes a fresh build is needed after major changes

### 🎯 **Performance Tips:**

- **Use `.dockerignore`** to exclude unnecessary files from build context
- **Enable file system polling** if on Windows/WSL2:
  ```yaml
  environment:
    - PYTHONUNBUFFERED=1
    - WATCHDOG_POLLING=true  # For file system polling
  ```
- **Exclude large directories** from volume mounts (like `node_modules`, `.venv`)

### ✅ **Confirmation:**

With these changes, your development workflow should now be:

1. **Edit code** in your IDE/editor
2. **Save file** (Ctrl+S / Cmd+S)  
3. **See changes immediately** in browser/API
4. **No manual restarts needed** 🎉

The enhanced `/upload/extract-medical-data` API changes should now reflect immediately when you modify `s3_routes.py` or related files!