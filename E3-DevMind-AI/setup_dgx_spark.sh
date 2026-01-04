#!/bin/bash

################################################################################
# E3 DevMind AI - Complete DGX Spark Setup Script
#
# This script installs EVERYTHING needed to run E3 DevMind AI on DGX Spark:
# - System dependencies
# - Docker & NVIDIA Container Toolkit
# - Python environment
# - CSDL-vLLM
# - E3 DevMind AI
# - All databases and services
#
# Usage:
#   wget https://raw.githubusercontent.com/E3-Consortium/e3-devmind-ai/main/setup_dgx_spark.sh
#   chmod +x setup_dgx_spark.sh
#   sudo ./setup_dgx_spark.sh
#
# Or one-liner:
#   curl -fsSL https://raw.githubusercontent.com/E3-Consortium/e3-devmind-ai/main/setup_dgx_spark.sh | sudo bash
#
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/e3-devmind-ai"
USER="devmind"
GROUP="devmind"

# Logging
LOG_FILE="/var/log/e3-devmind-setup.log"
exec > >(tee -a "$LOG_FILE")
exec 2>&1

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_dgx_spark() {
    print_info "Checking if this is a DGX Spark..."

    # Check for NVIDIA Grace Blackwell
    if lspci | grep -i nvidia | grep -i grace &> /dev/null; then
        print_success "DGX Spark detected!"
        return 0
    fi

    print_warning "Not a DGX Spark, but continuing anyway..."
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
}

################################################################################
# Installation Steps
################################################################################

step1_system_update() {
    print_header "STEP 1: System Update"

    print_info "Updating package lists..."
    apt-get update -qq

    print_info "Upgrading system packages..."
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq

    print_success "System updated"
}

step2_install_dependencies() {
    print_header "STEP 2: Installing System Dependencies"

    print_info "Installing essential packages..."
    apt-get install -y -qq \
        build-essential \
        curl \
        wget \
        git \
        vim \
        htop \
        tmux \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release

    print_success "System dependencies installed"
}

step3_install_docker() {
    print_header "STEP 3: Installing Docker"

    if command -v docker &> /dev/null; then
        print_warning "Docker already installed, skipping..."
        docker --version
        return 0
    fi

    print_info "Adding Docker GPG key..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    print_info "Adding Docker repository..."
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    print_info "Installing Docker..."
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    print_info "Starting Docker service..."
    systemctl start docker
    systemctl enable docker

    print_success "Docker installed: $(docker --version)"
}

step4_install_nvidia_toolkit() {
    print_header "STEP 4: Installing NVIDIA Container Toolkit"

    if command -v nvidia-ctk &> /dev/null; then
        print_warning "NVIDIA Container Toolkit already installed, skipping..."
        return 0
    fi

    print_info "Adding NVIDIA Container Toolkit repository..."
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

    print_info "Installing NVIDIA Container Toolkit..."
    apt-get update -qq
    apt-get install -y -qq nvidia-container-toolkit

    print_info "Configuring Docker for NVIDIA GPUs..."
    nvidia-ctk runtime configure --runtime=docker
    systemctl restart docker

    print_success "NVIDIA Container Toolkit installed"

    # Test GPU access
    print_info "Testing GPU access..."
    if docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
        print_success "GPU access verified!"
    else
        print_warning "GPU access test failed, but continuing..."
    fi
}

step5_install_python() {
    print_header "STEP 5: Installing Python & Tools"

    print_info "Installing Python 3.11..."
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get update -qq
    apt-get install -y -qq \
        python3.11 \
        python3.11-venv \
        python3.11-dev \
        python3-pip

    # Set Python 3.11 as default
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
    update-alternatives --set python3 /usr/bin/python3.11

    print_info "Upgrading pip..."
    python3 -m pip install --upgrade pip setuptools wheel

    print_success "Python installed: $(python3 --version)"
}

step6_create_user() {
    print_header "STEP 6: Creating DevMind User"

    if id "$USER" &>/dev/null; then
        print_warning "User $USER already exists, skipping..."
        return 0
    fi

    print_info "Creating user and group..."
    groupadd -f "$GROUP"
    useradd -m -s /bin/bash -g "$GROUP" "$USER"

    print_info "Adding user to docker group..."
    usermod -aG docker "$USER"

    print_success "User $USER created"
}

step7_setup_directories() {
    print_header "STEP 7: Setting Up Directories"

    print_info "Creating installation directory..."
    mkdir -p "$INSTALL_DIR"

    print_info "Creating data directories..."
    mkdir -p "$INSTALL_DIR/data/qdrant"
    mkdir -p "$INSTALL_DIR/data/postgres"
    mkdir -p "$INSTALL_DIR/data/redis"
    mkdir -p "$INSTALL_DIR/logs"
    mkdir -p "$INSTALL_DIR/knowledge"
    mkdir -p "$INSTALL_DIR/models"

    print_info "Setting permissions..."
    chown -R "$USER:$GROUP" "$INSTALL_DIR"
    chmod -R 755 "$INSTALL_DIR"

    print_success "Directories created"
}

step8_clone_repositories() {
    print_header "STEP 8: Cloning Repositories"

    cd "$INSTALL_DIR"

    # Clone CSDL-vLLM
    if [ ! -d "CSDL-vLLM" ]; then
        print_info "Cloning CSDL-vLLM..."
        sudo -u "$USER" git clone https://github.com/LUBTFY/CSDL-vLLM.git
        print_success "CSDL-vLLM cloned"
    else
        print_warning "CSDL-vLLM already exists, updating..."
        cd CSDL-vLLM
        sudo -u "$USER" git pull
        cd ..
    fi

    # Clone E3 DevMind AI
    if [ ! -d "e3-devmind-ai" ]; then
        print_info "Cloning E3 DevMind AI..."
        sudo -u "$USER" git clone https://github.com/LUBTFY/E3-DevMind-AI.git e3-devmind-ai
        print_success "E3 DevMind AI cloned"
    else
        print_warning "E3 DevMind AI already exists, updating..."
        cd e3-devmind-ai
        sudo -u "$USER" git pull
        cd ..
    fi

    # Clone ANLT Compiler
    if [ ! -d "agent-native-language-compiler" ]; then
        print_info "Cloning ANLT Compiler..."
        sudo -u "$USER" git clone https://github.com/LUBTFY/agent-native-language-compiler.git
        print_success "ANLT Compiler cloned"
    else
        print_warning "ANLT Compiler already exists, updating..."
        cd agent-native-language-compiler
        sudo -u "$USER" git pull
        cd ..
    fi
}

step9_configure_environment() {
    print_header "STEP 9: Configuring Environment"

    cd "$INSTALL_DIR/e3-devmind-ai"

    if [ ! -f ".env" ]; then
        print_info "Creating .env file..."

        # Create .env with defaults
        cat > .env << 'EOF'
# E3 DevMind AI Configuration

# Database Configuration
POSTGRES_USER=devmind
POSTGRES_DB=devmind
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Qdrant Configuration
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# CSDL-vLLM Configuration
CSDL_VLLM_URL=http://csdl-vllm:8002
VLLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# API Keys (REPLACE THESE!)
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here

# Optional Integration Keys
GITHUB_TOKEN=your-github-token
SLACK_BOT_TOKEN=your-slack-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-token

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
WEBSOCKET_PORT=8001

# Logging
LOG_LEVEL=INFO
EOF

        # Generate secure password for PostgreSQL
        POSTGRES_PASSWORD=$(openssl rand -base64 32)
        echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >> .env

        print_success ".env file created"
        print_warning "⚠️  IMPORTANT: You need to configure API keys in .env file!"
        print_info "Edit: $INSTALL_DIR/e3-devmind-ai/.env"
        print_info ""
        print_info "Required API keys:"
        print_info "  - OPENAI_API_KEY (for multimodal)"
        print_info "  - GITHUB_TOKEN (optional)"
        print_info "  - SLACK_BOT_TOKEN (optional)"
        print_info "  - JIRA_API_TOKEN (optional)"
    else
        print_warning ".env already exists, skipping..."
    fi

    chown "$USER:$GROUP" .env
    chmod 600 .env
}

step10_build_docker_images() {
    print_header "STEP 10: Building Docker Images"

    # Build CSDL-vLLM
    print_info "Building CSDL-vLLM image (this may take 15-20 minutes)..."
    cd "$INSTALL_DIR/CSDL-vLLM"
    sudo -u "$USER" docker build -t csdl-vllm:latest .
    print_success "CSDL-vLLM image built"

    # Build E3 DevMind AI
    print_info "Building E3 DevMind AI images..."
    cd "$INSTALL_DIR/e3-devmind-ai"
    sudo -u "$USER" docker compose build
    print_success "E3 DevMind AI images built"
}

step11_initialize_databases() {
    print_header "STEP 11: Initializing Databases"

    cd "$INSTALL_DIR/e3-devmind-ai"

    print_info "Starting database services..."
    sudo -u "$USER" docker compose up -d postgres qdrant redis

    print_info "Waiting for databases to be ready..."
    sleep 10

    # Wait for PostgreSQL
    print_info "Waiting for PostgreSQL..."
    for i in {1..30}; do
        if docker compose exec -T postgres pg_isready -U devmind &> /dev/null; then
            print_success "PostgreSQL ready"
            break
        fi
        sleep 2
    done

    # Wait for Qdrant
    print_info "Waiting for Qdrant..."
    for i in {1..30}; do
        if curl -f http://localhost:6333/collections &> /dev/null; then
            print_success "Qdrant ready"
            break
        fi
        sleep 2
    done

    # Wait for Redis
    print_info "Waiting for Redis..."
    for i in {1..30}; do
        if docker compose exec -T redis redis-cli ping &> /dev/null; then
            print_success "Redis ready"
            break
        fi
        sleep 2
    done
}

step12_start_services() {
    print_header "STEP 12: Starting All Services"

    cd "$INSTALL_DIR/e3-devmind-ai"

    print_info "Starting CSDL-vLLM..."
    sudo -u "$USER" docker compose up -d csdl-vllm

    print_info "Waiting for CSDL-vLLM to be ready (this may take a few minutes)..."
    sleep 15

    # Wait for CSDL-vLLM
    for i in {1..60}; do
        if curl -f http://localhost:8002/health &> /dev/null; then
            print_success "CSDL-vLLM ready"
            break
        fi
        print_info "Still waiting for CSDL-vLLM... ($i/60)"
        sleep 5
    done

    print_info "Starting E3 DevMind AI..."
    sudo -u "$USER" docker compose up -d

    print_info "Waiting for services to start..."
    sleep 10
}

step13_verify_installation() {
    print_header "STEP 13: Verifying Installation"

    cd "$INSTALL_DIR/e3-devmind-ai"

    print_info "Checking service status..."
    docker compose ps

    echo ""
    print_info "Running health checks..."
    echo ""

    # Check API
    if curl -f http://localhost:8000/api/health &> /dev/null; then
        print_success "REST API: Healthy"
    else
        print_error "REST API: Unhealthy"
    fi

    # Check CSDL-vLLM
    if curl -f http://localhost:8002/health &> /dev/null; then
        print_success "CSDL-vLLM: Healthy"
    else
        print_error "CSDL-vLLM: Unhealthy"
    fi

    # Check Qdrant
    if curl -f http://localhost:6333/collections &> /dev/null; then
        print_success "Qdrant: Healthy"
    else
        print_error "Qdrant: Unhealthy"
    fi

    # Check PostgreSQL
    if docker compose exec -T postgres pg_isready -U devmind &> /dev/null; then
        print_success "PostgreSQL: Healthy"
    else
        print_error "PostgreSQL: Unhealthy"
    fi

    # Check Redis
    if docker compose exec -T redis redis-cli ping &> /dev/null; then
        print_success "Redis: Healthy"
    else
        print_error "Redis: Unhealthy"
    fi
}

step14_install_cli() {
    print_header "STEP 14: Installing CLI Tools"

    cd "$INSTALL_DIR/e3-devmind-ai"

    print_info "Installing Python package in development mode..."
    sudo -u "$USER" python3 -m pip install -e .

    print_info "Creating CLI symlink..."
    ln -sf "$INSTALL_DIR/e3-devmind-ai/cli/main.py" /usr/local/bin/devmind
    chmod +x /usr/local/bin/devmind

    print_success "CLI installed: devmind --help"
}

step15_setup_systemd() {
    print_header "STEP 15: Setting Up Systemd Service"

    print_info "Creating systemd service..."
    cat > /etc/systemd/system/e3-devmind.service << EOF
[Unit]
Description=E3 DevMind AI
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$INSTALL_DIR/e3-devmind-ai
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=$USER
Group=$GROUP

[Install]
WantedBy=multi-user.target
EOF

    print_info "Enabling service..."
    systemctl daemon-reload
    systemctl enable e3-devmind.service

    print_success "Systemd service created"
    print_info "Control service with:"
    print_info "  sudo systemctl start e3-devmind"
    print_info "  sudo systemctl stop e3-devmind"
    print_info "  sudo systemctl status e3-devmind"
}

step16_final_configuration() {
    print_header "STEP 16: Final Configuration"

    print_info "Setting up bash aliases..."
    cat >> /home/$USER/.bashrc << 'EOF'

# E3 DevMind AI Aliases
alias devmind-start='cd /opt/e3-devmind-ai/e3-devmind-ai && docker compose up -d'
alias devmind-stop='cd /opt/e3-devmind-ai/e3-devmind-ai && docker compose down'
alias devmind-logs='cd /opt/e3-devmind-ai/e3-devmind-ai && docker compose logs -f'
alias devmind-status='cd /opt/e3-devmind-ai/e3-devmind-ai && docker compose ps'
alias devmind-health='cd /opt/e3-devmind-ai/e3-devmind-ai && ./deployment/scripts/health_check.sh'
EOF

    print_info "Setting up firewall rules..."
    if command -v ufw &> /dev/null; then
        ufw allow 8000/tcp comment "E3 DevMind API"
        ufw allow 8001/tcp comment "E3 DevMind WebSocket"
        print_success "Firewall configured"
    else
        print_warning "UFW not installed, skipping firewall configuration"
    fi

    print_success "Final configuration complete"
}

################################################################################
# Main Installation Flow
################################################################################

main() {
    print_header "E3 DEVMIND AI - DGX SPARK SETUP"

    print_info "Starting installation at $(date)"
    print_info "Installation directory: $INSTALL_DIR"
    print_info "User: $USER"
    print_info "Log file: $LOG_FILE"

    # Pre-checks
    check_root
    check_dgx_spark

    # Installation steps
    step1_system_update
    step2_install_dependencies
    step3_install_docker
    step4_install_nvidia_toolkit
    step5_install_python
    step6_create_user
    step7_setup_directories
    step8_clone_repositories
    step9_configure_environment
    step10_build_docker_images
    step11_initialize_databases
    step12_start_services
    step13_verify_installation
    step14_install_cli
    step15_setup_systemd
    step16_final_configuration

    # Final summary
    print_header "INSTALLATION COMPLETE!"

    echo ""
    echo -e "${GREEN}✅ E3 DevMind AI is now installed and running!${NC}"
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}NEXT STEPS:${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "1️⃣  Configure API keys:"
    echo "   sudo nano $INSTALL_DIR/e3-devmind-ai/.env"
    echo ""
    echo "2️⃣  Restart services after adding keys:"
    echo "   cd $INSTALL_DIR/e3-devmind-ai"
    echo "   docker compose restart"
    echo ""
    echo "3️⃣  Access E3 DevMind AI:"
    echo "   Web: http://$(hostname -I | awk '{print $1}'):8000"
    echo "   API: http://$(hostname -I | awk '{print $1}'):8000/api"
    echo "   Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
    echo ""
    echo "4️⃣  Use CLI:"
    echo "   devmind status"
    echo "   devmind ask \"What are the risks in our current sprint?\""
    echo ""
    echo "5️⃣  Check logs:"
    echo "   devmind-logs"
    echo "   # Or: cd $INSTALL_DIR/e3-devmind-ai && docker compose logs -f"
    echo ""
    echo "6️⃣  Useful commands:"
    echo "   devmind-start    # Start services"
    echo "   devmind-stop     # Stop services"
    echo "   devmind-status   # Check status"
    echo "   devmind-health   # Health check"
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}SYSTEM INFO:${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Installation Directory: $INSTALL_DIR"
    echo "User: $USER"
    echo "Log File: $LOG_FILE"
    echo "Docker: $(docker --version)"
    echo "Python: $(python3 --version)"
    echo ""
    echo -e "${GREEN}Installation completed at $(date)${NC}"
    echo ""
    print_warning "⚠️  IMPORTANT: Add your API keys to .env before using multimodal features!"
    echo ""
}

# Run installation
main "$@"
