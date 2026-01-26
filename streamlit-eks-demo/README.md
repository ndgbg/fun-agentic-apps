# 🚀 .NET to EKS Deployment Demo

A single-file Streamlit demo that connects to AWS EKS clusters and deploys .NET Core applications.

## 📁 Simple Project Structure

```
streamlit-eks-demo/
├── eks_demo.py              # Single consolidated demo file
├── requirements.txt         # Python dependencies
├── setup_prerequisites.sh   # Install AWS tools (kubectl, eksctl)
├── run.sh                  # Quick start script
└── README.md               # This file
```

## 🎯 What This Demo Does

This Streamlit application provides an interactive interface for deploying .NET applications to AWS EKS:

- **AWS Integration**: Uses boto3 to connect to your AWS account and interact with EKS, ECR, and EC2 services
- **Repository Analysis**: Fetches and analyzes GitHub repositories to detect .NET projects, Dockerfiles, and deployment configurations
- **Cluster Management**: Creates and configures EKS clusters using eksctl with proper VPC, subnet, and security group settings
- **Container Deployment**: Builds Docker images, pushes to ECR, and deploys to Kubernetes with proper service and ingress configurations
- **Live Monitoring**: Polls Kubernetes API to display pod status, logs, and cluster health in real-time

## 🚀 Quick Start

### 1. Setup Prerequisites (One Time)
```bash
cd streamlit-eks-demo
./setup_prerequisites.sh  # Installs kubectl, eksctl, Docker
aws configure             # Configure your AWS credentials
```

### 2. Run the Demo
```bash
./run.sh
```

### 3. Open Browser
Navigate to `http://localhost:8501`

## 📱 Demo Features (All in One File)

### 🏠 **Main Demo Page**
- AWS connection status
- GitHub repository analysis
- EKS cluster creation
- Application deployment
- Real-time monitoring

### 🔧 **MCP Configuration**
- Generate MCP server configurations
- Download ready-to-use `mcp.json` files
- One-click Kiro integration

### 📚 **Example Commands**
- Natural language EKS commands
- Copy-paste ready for Kiro
- Organized by category

### 🔍 **Live Cluster Monitor**
- Real-time pod status
- kubectl commands
- Namespace management

## 🎯 Demo Flow

This is what happens when you use the demo from start to finish:

### 1. **Connect to AWS**
The application uses your AWS credentials (from `aws configure`) to establish a session with boto3. It verifies access by calling `sts.get_caller_identity()` and displays your account ID and active region.

```
✅ AWS Connected
Account: 1234...5678
Region: us-west-2
```

### 2. **Analyze GitHub Project**
When you provide a GitHub URL, the demo:
- Fetches the repository metadata using GitHub API
- Scans for `.csproj` files to detect .NET projects
- Checks for existing `Dockerfile` and Kubernetes manifests
- Identifies the .NET version and project type (Web API, MVC, etc.)

```
GitHub URL: https://github.com/your-username/dotnet-api
✅ Repository found - .NET 8 Web API
❌ No Dockerfile found
```

### 3. **Deploy to EKS**
The deployment process executes these steps:
- **Cluster Creation**: Runs `eksctl create cluster` with managed node groups, configures VPC and subnets
- **Namespace Setup**: Creates a Kubernetes namespace to isolate your application
- **Image Build**: If no Dockerfile exists, generates one based on detected .NET version, builds and pushes to ECR
- **Deployment**: Applies Kubernetes deployment and service manifests, creates LoadBalancer for external access
- **Health Check**: Waits for pods to reach "Running" state and LoadBalancer to provision

```
🏗️ Creating EKS cluster... ✅
📦 Creating namespace... ✅
🚀 Deploying application... ✅
🌐 LoadBalancer ready... ✅

Result: http://a1b2c3-123456789.us-west-2.elb.amazonaws.com
```

## 🔧 Prerequisites

### Required Tools
- **Python 3.8+**
- **AWS CLI** (configured with credentials)
- **kubectl** (installed by setup script)
- **eksctl** (installed by setup script)
- **Docker** (for building images)

### AWS Setup
```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
# Enter: Access Key, Secret Key, Region (us-west-2), Format (json)

# Verify connection
aws sts get-caller-identity
```

## 💰 Cost Awareness

**Real AWS resources = real costs:**
- EKS Cluster: ~$0.10/hour ($72/month)
- EC2 Nodes: ~$0.04/hour per t3.medium node
- LoadBalancer: ~$0.025/hour
- **Total**: ~$5-10/day for testing

**Always clean up when done:**
```bash
eksctl delete cluster --name dotnet-demo-cluster --region us-west-2
```

## 🎓 What You'll Learn

1. **EKS Operations** - Hands-on cluster management
2. **Kubernetes Deployment** - Pod and service creation  
3. **AWS Integration** - ECR, LoadBalancers, VPC setup
4. **Natural Language Ops** - MCP server integration
5. **Live Monitoring** - Cluster health checks

## 🔗 Integration with Your Projects

### Use Your Own .NET Repository
```
GitHub URL: https://github.com/your-username/your-dotnet-project
```

The demo will:
- ✅ Analyze your repository structure
- ✅ Detect .NET framework and dependencies
- ✅ Deploy to your EKS cluster
- ✅ Provide working endpoints

### Integration with Kiro IDE
1. **Generate MCP config** in the demo
2. **Download `mcp.json`** file
3. **Place in `.kiro/settings/mcp.json`**
4. **Use natural language** commands in Kiro
5. **Deploy to clusters** created by this demo

## 🚨 Important Notes

- **This creates real AWS resources** that incur costs
- **Always clean up** clusters when done testing
- **Monitor your AWS billing** during experimentation
- **Use appropriate IAM permissions** for security

## 🎉 Success Indicators

When working correctly, you'll see:
- ✅ Cluster names in AWS Console
- ✅ Pods running in Kubernetes
- ✅ Working LoadBalancer endpoints
- ✅ Application responses
- ✅ kubectl commands that work

## 🔄 Next Steps

After running the demo:
1. **Deploy your own .NET applications**
2. **Set up CI/CD pipelines** 
3. **Configure monitoring and logging**
4. **Integrate with EKS MCP server in Kiro**
5. **Scale to production workloads**

This single-file demo bridges the gap between learning and doing - you're working with AWS infrastructure, not simulations!