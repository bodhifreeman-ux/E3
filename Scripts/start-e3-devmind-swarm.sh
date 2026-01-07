#!/bin/bash
# E3 DevMind Swarm Startup Script
# Starts the 32-Agent AI Swarm + AG-UI Server + CopilotKit UI
# Prerequisites: CSDL and Archon should be running (use Start E3 Full Stack first)

set -e

echo "=============================================="
echo "  E3 DevMind Swarm + AG-UI Launcher"
echo "=============================================="
echo ""

E3_ROOT="/home/bodhifreeman/E3"
source "$E3_ROOT/.env" 2>/dev/null || true

DEVMIND_DIR="$E3_ROOT/E3-DevMind-AI"
UI_DIR="$DEVMIND_DIR/ui"
CSDL_VENV="$E3_ROOT/CSDL-ANLT/csdl-venv"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_info() { echo -e "${BLUE}[i]${NC} $1"; }

check_port() {
    nc -z localhost $1 2>/dev/null
    return $?
}

# ============================================================================
# Check if Full Stack services are running
# ============================================================================
echo "Checking prerequisites..."

if ! check_port ${CSDL_SERVER_PORT:-5000}; then
    print_warning "CSDL Server not running on port ${CSDL_SERVER_PORT:-5000}"
    print_info "Run 'Start E3 Full Stack' first, or start CSDL manually"
fi

if ! check_port 8181; then
    print_warning "Archon API not running on port 8181"
    print_info "Run 'Start E3 Full Stack' first"
fi

# ============================================================================
# Start E3 AG-UI Server
# ============================================================================
echo ""
echo "Starting E3 AG-UI Server..."

if check_port ${E3_AGUI_PORT:-8100}; then
    print_status "E3 AG-UI Server already running on port ${E3_AGUI_PORT:-8100}"
else
    print_info "Starting E3 AG-UI Server in background..."
    (
        source "$CSDL_VENV/bin/activate" 2>/dev/null || source "/home/bodhifreeman/pytorch-build/pytorch-venv/bin/activate"
        pip install -q -r "$DEVMIND_DIR/requirements-agui.txt" 2>/dev/null || true
        cd "$DEVMIND_DIR"
        E3_AGUI_PORT=${E3_AGUI_PORT:-8100} python3 -m agents.agui_server > /tmp/e3-agui-server.log 2>&1
    ) &
    AGUI_PID=$!
    echo $AGUI_PID > /tmp/e3-agui-server.pid
    print_info "AG-UI Server starting (PID: $AGUI_PID)..."
    sleep 2
fi

# ============================================================================
# Start E3 DevMind UI (CopilotKit)
# ============================================================================
echo ""
echo "Starting E3 DevMind UI (CopilotKit)..."

if check_port ${E3_UI_PORT:-3000}; then
    print_status "E3 DevMind UI already running on port ${E3_UI_PORT:-3000}"
else
    if [ -d "$UI_DIR" ] && command -v pnpm &> /dev/null; then
        print_info "Starting E3 DevMind UI in background..."
        
        if [ ! -d "$UI_DIR/node_modules" ]; then
            print_info "Installing UI dependencies..."
            cd "$UI_DIR"
            pnpm install 2>/dev/null || npm install 2>/dev/null
        fi
        
        (
            cd "$UI_DIR"
            PORT=${E3_UI_PORT:-3000} pnpm run dev > /tmp/e3-ui.log 2>&1 || npm run dev > /tmp/e3-ui.log 2>&1
        ) &
        UI_PID=$!
        echo $UI_PID > /tmp/e3-ui.pid
        print_info "DevMind UI starting (PID: $UI_PID)..."
        sleep 3
    else
        print_warning "UI directory not found or pnpm not installed"
        print_info "Install with: npm install -g pnpm && cd $UI_DIR && pnpm install"
    fi
fi

# ============================================================================
# Wait for services and open browser
# ============================================================================
echo ""
echo "Waiting for services to start..."
sleep 3

# Check final status
echo ""
echo "=============================================="
echo "  E3 DevMind Services Status"
echo "=============================================="
echo ""

if check_port ${E3_AGUI_PORT:-8100}; then
    print_status "AG-UI Server:    http://localhost:${E3_AGUI_PORT:-8100}"
else
    print_warning "AG-UI Server not responding yet - check /tmp/e3-agui-server.log"
fi

if check_port ${E3_UI_PORT:-3000}; then
    print_status "DevMind UI:      http://localhost:${E3_UI_PORT:-3000}"
else
    print_warning "DevMind UI not responding yet - check /tmp/e3-ui.log"
fi

echo ""
echo "Opening E3 DevMind UI in browser..."
sleep 2
xdg-open "http://localhost:${E3_UI_PORT:-3000}" 2>/dev/null || true

echo ""
print_status "E3 DevMind Swarm started!"
echo ""
echo "To run the inter-agent demo simulation separately:"
echo "  cd $DEVMIND_DIR && python3 -m agents.demo_swarm_simulation"
echo ""
