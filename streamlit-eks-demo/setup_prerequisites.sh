#!/bin/bash

echo "🔧 Setting up prerequisites for EKS deployment demo"
echo "=================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to configure AWS credentials interactively
configure_aws() {
    echo ""
    echo "🔐 AWS Credentials Configuration"
    echo "================================"
    echo ""
    echo "You need AWS credentials to use this demo. Here's how to get them:"
    echo ""
    echo "1. Go to AWS Console: https://console.aws.amazon.com/"
    echo "2. Navigate to IAM → Users"
    echo "3. Create a new user (if you don't have one)"
    echo "4. Attach 'AdministratorAccess' policy"
    echo "5. Create access keys in Security credentials tab"
    echo ""
    
    read -p "Do you have AWS Access Key ID and Secret Access Key? (y/n): " has_keys
    
    if [[ $has_keys =~ ^[Yy]$ ]]; then
        echo ""
        echo "Great! Let's configure AWS CLI..."
        echo ""
        
        # Prompt for AWS credentials
        read -p "Enter your AWS Access Key ID: " access_key
        read -s -p "Enter your AWS Secret Access Key: " secret_key
        echo ""
        read -p "Enter your default region (e.g., us-west-2): " region
        region=${region:-us-west-2}  # Default to us-west-2 if empty
        
        # Configure AWS CLI
        aws configure set aws_access_key_id "$access_key"
        aws configure set aws_secret_access_key "$secret_key"
        aws configure set default.region "$region"
        aws configure set default.output "json"
        
        echo ""
        echo "🔍 Testing AWS connection..."
        
        if aws sts get-caller-identity >/dev/null 2>&1; then
            echo "✅ AWS credentials configured successfully!"
            account_id=$(aws sts get-caller-identity --query 'Account' --output text)
            user_arn=$(aws sts get-caller-identity --query 'Arn' --output text)
            echo "   Account ID: $account_id"
            echo "   User: $user_arn"
            echo "   Region: $region"
        else
            echo "❌ AWS credential test failed. Please check your keys and try again."
            echo "   You can run 'aws configure' manually later."
        fi
    else
        echo ""
        echo "📋 To get AWS credentials:"
        echo "1. Sign up at https://aws.amazon.com (if you don't have an account)"
        echo "2. Go to IAM → Users → Create user"
        echo "3. Attach AdministratorAccess policy"
        echo "4. Create access keys"
        echo "5. Run this setup script again"
        echo ""
        echo "⚠️  You can continue setup, but AWS features won't work without credentials."
        read -p "Continue setup without AWS configuration? (y/n): " continue_setup
        
        if [[ ! $continue_setup =~ ^[Yy]$ ]]; then
            echo "Setup cancelled. Please get AWS credentials and run again."
            exit 1
        fi
    fi
}

# Check Python
if command_exists python3; then
    echo "✅ Python 3 is installed"
    python3 --version
else
    echo "❌ Python 3 is required but not installed"
    echo "Please install Python 3 first"
    exit 1
fi

# Check AWS CLI
if command_exists aws; then
    echo "✅ AWS CLI is installed"
    aws --version
    
    # Check AWS credentials
    if aws sts get-caller-identity >/dev/null 2>&1; then
        echo "✅ AWS credentials are already configured"
        account_id=$(aws sts get-caller-identity --query 'Account' --output text)
        region=$(aws configure get region)
        echo "   Account ID: $account_id"
        echo "   Region: $region"
        
        read -p "Do you want to reconfigure AWS credentials? (y/n): " reconfigure
        if [[ $reconfigure =~ ^[Yy]$ ]]; then
            configure_aws
        fi
    else
        echo "⚠️  AWS credentials not configured"
        configure_aws
    fi
else
    echo "⚠️  AWS CLI not found - installing..."
    pip3 install awscli
    
    if command_exists aws; then
        echo "✅ AWS CLI installed successfully"
        configure_aws
    else
        echo "❌ Failed to install AWS CLI"
        exit 1
    fi
fi

# Check kubectl
if command_exists kubectl; then
    echo "✅ kubectl is installed"
    kubectl version --client --short 2>/dev/null || kubectl version --client
else
    echo "⚠️  kubectl not found - installing..."
    
    # Install kubectl based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install kubectl
        else
            echo "Please install kubectl manually: https://kubernetes.io/docs/tasks/tools/install-kubectl-macos/"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        chmod +x kubectl
        sudo mv kubectl /usr/local/bin/
    else
        echo "Please install kubectl manually: https://kubernetes.io/docs/tasks/tools/"
    fi
fi

# Check eksctl
if command_exists eksctl; then
    echo "✅ eksctl is installed"
    eksctl version
else
    echo "⚠️  eksctl not found - installing..."
    
    # Install eksctl based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew tap weaveworks/tap
            brew install weaveworks/tap/eksctl
        else
            curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
            sudo mv /tmp/eksctl /usr/local/bin
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
        sudo mv /tmp/eksctl /usr/local/bin
    else
        echo "Please install eksctl manually: https://eksctl.io/introduction/#installation"
    fi
fi

# Check Docker
if command_exists docker; then
    echo "✅ Docker is installed"
    docker --version
    
    # Check if Docker daemon is running
    if docker info >/dev/null 2>&1; then
        echo "✅ Docker daemon is running"
    else
        echo "⚠️  Docker daemon is not running"
        echo "Please start Docker Desktop or Docker service"
    fi
else
    echo "⚠️  Docker not found"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

echo ""
echo "🎉 Setup complete! You can now run the demo:"
echo "   streamlit run app.py"
echo ""
echo "📋 Prerequisites checklist:"
echo "   ✅ Python 3"
echo "   ✅ AWS CLI"
echo "   ✅ kubectl"
echo "   ✅ eksctl"
echo "   ✅ Docker"
echo "   ✅ Python dependencies"
echo ""
echo "🔐 Make sure your AWS credentials are configured:"
echo "   aws configure"
echo ""
echo "🚀 Ready to deploy to real EKS clusters!"

# Check kubectl
if command_exists kubectl; then
    echo "✅ kubectl is installed"
    kubectl version --client --short 2>/dev/null || kubectl version --client
else
    echo "⚠️  kubectl not found - installing..."
    
    # Install kubectl based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install kubectl
        else
            echo "Installing kubectl manually..."
            curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
            chmod +x kubectl
            sudo mv kubectl /usr/local/bin/
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        chmod +x kubectl
        sudo mv kubectl /usr/local/bin/
    else
        echo "Please install kubectl manually: https://kubernetes.io/docs/tasks/tools/"
    fi
    
    # Verify installation
    if command_exists kubectl; then
        echo "✅ kubectl installed successfully"
    else
        echo "⚠️  kubectl installation may have failed"
    fi
fi

# Check eksctl
if command_exists eksctl; then
    echo "✅ eksctl is installed"
    eksctl version
else
    echo "⚠️  eksctl not found - installing..."
    
    # Install eksctl based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew tap weaveworks/tap
            brew install weaveworks/tap/eksctl
        else
            curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
            sudo mv /tmp/eksctl /usr/local/bin
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
        sudo mv /tmp/eksctl /usr/local/bin
    else
        echo "Please install eksctl manually: https://eksctl.io/introduction/#installation"
    fi
    
    # Verify installation
    if command_exists eksctl; then
        echo "✅ eksctl installed successfully"
    else
        echo "⚠️  eksctl installation may have failed"
    fi
fi

# Check Docker
if command_exists docker; then
    echo "✅ Docker is installed"
    docker --version
    
    # Check if Docker daemon is running
    if docker info >/dev/null 2>&1; then
        echo "✅ Docker daemon is running"
    else
        echo "⚠️  Docker daemon is not running"
        echo "Please start Docker Desktop or Docker service"
    fi
else
    echo "⚠️  Docker not found"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    echo "Docker is needed for building container images"
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

echo ""
echo "🎉 Setup complete! Summary:"
echo "=========================="
echo "   ✅ Python 3"
echo "   ✅ AWS CLI"
if aws sts get-caller-identity >/dev/null 2>&1; then
    echo "   ✅ AWS Credentials (configured)"
else
    echo "   ⚠️  AWS Credentials (not configured)"
fi
if command_exists kubectl; then
    echo "   ✅ kubectl"
else
    echo "   ⚠️  kubectl (not installed)"
fi
if command_exists eksctl; then
    echo "   ✅ eksctl"
else
    echo "   ⚠️  eksctl (not installed)"
fi
if command_exists docker; then
    echo "   ✅ Docker"
else
    echo "   ⚠️  Docker (not installed)"
fi
echo "   ✅ Python dependencies"
echo ""
echo "🚀 Ready to run the demo:"
echo "   ./run.sh"
echo ""
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "⚠️  Note: AWS credentials are not configured."
    echo "   The demo will show instructions to configure them."
    echo "   You can also run 'aws configure' manually."
fi
echo ""
echo "🌐 The demo will open at: http://localhost:8501"