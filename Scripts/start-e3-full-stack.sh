#!/bin/bash
# E3 DevMind Full Stack Startup Script
# Starts ALL services needed for the complete AI development environment:
# - CSDL-14B Server (local LLM)
# - Archon (Knowledge Base + RAG)
# - E3 AG-UI Server (CopilotKit backend)
# - E3 DevMind UI (CopilotKit frontend)

set -e

echo "=============================================="
echo "  E3 DevMind Full Stack Launcher"
echo "=============================================="
echo ""

# Load environment variables
E3_ROOT="/home/bodhifreeman/E3"
source "$E3_ROOT/.env" 2>/dev/null || true

ARCHON_DIR="$E3_ROOT/E3-DevMind-AI/Archon"
CSDL_DIR="$E3_ROOT/CSDL-ANLT"
DEVMIND_DIR="$E3_ROOT/E3-DevMind-AI"
UI_DIR="$DEVMIND_DIR/ui"
CSDL_VENV="$CSDL_DIR/csdl-venv"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# Function to check if a service is running
check_port() {
    local port=$1
    nc -z localhost $port 2>/dev/null
    return $?
}

# Function to wait for a port
wait_for_port() {
    local port=$1
    local name=$2
    local max_wait=30
    local count=0

    while ! check_port $port && [ $count -lt $max_wait ]; do
        sleep 1
        count=$((count + 1))
    done

    if check_port $port; then
        print_status "$name is running on port $port"
        return 0
    else
        print_warning "$name not responding on port $port after ${max_wait}s"
        return 1
    fi
}

# ============================================================================
# Step 1: Check prerequisites
# ============================================================================
echo "Step 1: Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker."
    exit 1
fi
print_status "Docker is available"

if ! command -v node &> /dev/null; then
    print_warning "Node.js not found. UI will not start."
fi

# ============================================================================
# Step 2: Start CSDL Server (if not running)
# ============================================================================
echo ""
echo "Step 2: Starting CSDL-14B Server..."

if check_port ${CSDL_SERVER_PORT:-5000}; then
    print_status "CSDL Server already running on port ${CSDL_SERVER_PORT:-5000}"
else
    print_info "Starting CSDL-14B Server in background..."
    cd "$CSDL_DIR"

    # Start CSDL server in background
    (
        source "$CSDL_VENV/bin/activate" 2>/dev/null || source "/home/bodhifreeman/pytorch-build/pytorch-venv/bin/activate"
        pip install -q fastapi uvicorn pydantic accelerate 2>/dev/null
        python3 csdl-server.py > /tmp/csdl-server.log 2>&1
    ) &
    CSDL_PID=$!
    echo $CSDL_PID > /tmp/csdl-server.pid

    print_info "CSDL Server starting (PID: $CSDL_PID)..."
    print_info "Log file: /tmp/csdl-server.log"
    sleep 5

    if check_port ${CSDL_SERVER_PORT:-5000}; then
        print_status "CSDL Server started successfully"
    else
        print_warning "CSDL Server may still be loading model..."
    fi
fi

# ============================================================================
# Step 3: Start Archon Services (Docker)
# ============================================================================
echo ""
echo "Step 3: Starting Archon Services..."
cd "$ARCHON_DIR"

# Start Archon with Docker Compose
if ! docker compose up -d --build 2>&1 | tail -5; then
    print_error "Docker Compose failed!"
    echo ""
    echo "If you see 'permission denied', run this command and then log out/in:"
    echo "  sudo usermod -aG docker \$USER"
    exit 1
fi

echo ""
print_info "Waiting for Archon services..."
sleep 5

# Check Archon services
check_port 8181 && print_status "Archon API Server (8181)" || print_warning "Archon API not ready"
check_port 8051 && print_status "Archon MCP Server (8051)" || print_warning "Archon MCP not ready"
check_port 3737 && print_status "Archon UI (3737)" || print_warning "Archon UI not ready"

# ============================================================================
# Step 4: Start E3 AG-UI Server (Python backend for CopilotKit)
# ============================================================================
echo ""
echo "Step 4: Starting E3 AG-UI Server..."

if check_port ${E3_AGUI_PORT:-8100}; then
    print_status "E3 AG-UI Server already running on port ${E3_AGUI_PORT:-8100}"
else
    print_info "Starting E3 AG-UI Server in background..."
    cd "$DEVMIND_DIR"

    # Install dependencies and start AG-UI server
    (
        source "$CSDL_VENV/bin/activate" 2>/dev/null || source "/home/bodhifreeman/pytorch-build/pytorch-venv/bin/activate"
        pip install -q -r requirements-agui.txt 2>/dev/null || true
        cd "$DEVMIND_DIR"
        E3_AGUI_PORT=${E3_AGUI_PORT:-8100} python3 -m agents.agui_server > /tmp/e3-agui-server.log 2>&1
    ) &
    AGUI_PID=$!
    echo $AGUI_PID > /tmp/e3-agui-server.pid

    print_info "E3 AG-UI Server starting (PID: $AGUI_PID)..."
    print_info "Log file: /tmp/e3-agui-server.log"
    sleep 3

    if check_port ${E3_AGUI_PORT:-8100}; then
        print_status "E3 AG-UI Server started successfully"
    else
        print_warning "E3 AG-UI Server may still be starting..."
    fi
fi

# ============================================================================
# Step 5: Start E3 DevMind UI (Next.js frontend)
# ============================================================================
echo ""
echo "Step 5: Starting E3 DevMind UI..."

if check_port ${E3_UI_PORT:-3000}; then
    print_status "E3 DevMind UI already running on port ${E3_UI_PORT:-3000}"
else
    if [ -d "$UI_DIR" ] && command -v pnpm &> /dev/null; then
        print_info "Starting E3 DevMind UI in background..."
        cd "$UI_DIR"

        # Install dependencies if needed
        if [ ! -d "node_modules" ]; then
            print_info "Installing UI dependencies..."
            pnpm install 2>/dev/null || npm install 2>/dev/null
        fi

        # Start UI
        (
            cd "$UI_DIR"
            PORT=${E3_UI_PORT:-3000} pnpm run dev > /tmp/e3-ui.log 2>&1 || npm run dev > /tmp/e3-ui.log 2>&1
        ) &
        UI_PID=$!
        echo $UI_PID > /tmp/e3-ui.pid

        print_info "E3 DevMind UI starting (PID: $UI_PID)..."
        print_info "Log file: /tmp/e3-ui.log"
        sleep 5

        if check_port ${E3_UI_PORT:-3000}; then
            print_status "E3 DevMind UI started successfully"
        else
            print_warning "E3 DevMind UI may still be compiling..."
        fi
    else
        print_warning "UI directory not found or pnpm not installed"
        print_info "To install: npm install -g pnpm"
        print_info "Then run: cd $UI_DIR && pnpm install"
    fi
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "=============================================="
echo "  E3 DevMind Full Stack Status"
echo "=============================================="
echo ""
echo "Services:"
echo "  - CSDL-14B Server:   http://localhost:${CSDL_SERVER_PORT:-5000}"
echo "  - Archon API:        http://localhost:8181"
echo "  - Archon MCP:        http://localhost:8051"
echo "  - Archon UI:         http://localhost:3737"
echo "  - E3 AG-UI Server:   http://localhost:${E3_AGUI_PORT:-8100}"
echo "  - E3 DevMind UI:     http://localhost:${E3_UI_PORT:-3000}"
echo ""
echo "Log files:"
echo "  - CSDL Server:       /tmp/csdl-server.log"
echo "  - E3 AG-UI Server:   /tmp/e3-agui-server.log"
echo "  - E3 DevMind UI:     /tmp/e3-ui.log"
echo "  - Archon:            docker compose logs -f"
echo ""
echo "To stop all services:"
echo "  $E3_ROOT/Scripts/stop-e3-full-stack.sh"
echo ""
print_status "Full stack startup complete!"
echo ""
echo "Opening E3 DevMind UI in browser..."
sleep 2
xdg-open "http://localhost:${E3_UI_PORT:-3000}" 2>/dev/null || true
