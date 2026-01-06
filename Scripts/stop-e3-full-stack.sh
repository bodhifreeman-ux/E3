#!/bin/bash
# E3 DevMind Full Stack Stop Script
# Stops ALL services started by start-e3-full-stack.sh:
# - CSDL-14B Server
# - E3 AG-UI Server
# - E3 DevMind UI
# - Archon (Docker)

echo "=============================================="
echo "  E3 DevMind Full Stack Shutdown"
echo "=============================================="
echo ""

E3_ROOT="/home/bodhifreeman/E3/E3"
ARCHON_DIR="$E3_ROOT/E3-DevMind-AI/Archon"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Function to stop a service by PID file
stop_service() {
    local pid_file=$1
    local service_name=$2

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
            sleep 1
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null
            fi
            print_status "Stopped $service_name (PID: $pid)"
        else
            print_warning "$service_name was not running"
        fi
        rm -f "$pid_file"
    else
        print_warning "No PID file found for $service_name"
    fi
}

# ============================================================================
# Stop E3 DevMind UI
# ============================================================================
echo "Stopping E3 DevMind UI..."
stop_service "/tmp/e3-ui.pid" "E3 DevMind UI"

# Also kill any orphaned Next.js processes on port 3000
pkill -f "next.*3000" 2>/dev/null || true

# ============================================================================
# Stop E3 AG-UI Server
# ============================================================================
echo "Stopping E3 AG-UI Server..."
stop_service "/tmp/e3-agui-server.pid" "E3 AG-UI Server"

# Also kill any orphaned processes on port 8100
pkill -f "agui_server" 2>/dev/null || true

# ============================================================================
# Stop CSDL Server
# ============================================================================
echo "Stopping CSDL-14B Server..."
stop_service "/tmp/csdl-server.pid" "CSDL-14B Server"

# Also kill any orphaned CSDL server processes
pkill -f "csdl-server.py" 2>/dev/null || true

# ============================================================================
# Stop Archon (Docker)
# ============================================================================
echo "Stopping Archon Services..."
if [ -d "$ARCHON_DIR" ]; then
    cd "$ARCHON_DIR"
    docker compose down 2>/dev/null && print_status "Stopped Archon containers" || print_warning "Archon containers may not have been running"
else
    print_warning "Archon directory not found"
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "=============================================="
echo "  E3 DevMind Full Stack Stopped"
echo "=============================================="
echo ""
print_status "All services have been stopped."
echo ""
