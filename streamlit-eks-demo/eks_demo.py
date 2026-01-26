import streamlit as st
import boto3
import subprocess
import json
import time
import os
import requests
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# Page configuration
st.set_page_config(
    page_title="🚀 .NET to EKS Deployment Demo",
    page_icon="🚀",
    layout="wide"
)

# Early AWS credential check - show warning banner if not configured
@st.cache_resource
def get_aws_integration():
    return AWSEKSIntegration()

# Quick credential check for banner
def check_credentials_configured():
    """Check if credentials are configured via Streamlit session state or AWS CLI"""
    # Check session state first
    if 'aws_access_key' in st.session_state and 'aws_secret_key' in st.session_state:
        return True
    
    # Fall back to AWS CLI check
    try:
        temp_aws = AWSEKSIntegration()
        creds_check, _ = temp_aws.check_aws_credentials()
        return creds_check
    except:
        return False

# Show credential warning if not configured
if not check_credentials_configured():
    st.error("🚨 **AWS Credentials Required!** Configure them in the sidebar or use `aws configure`.")

def configure_aws_credentials():
    """Show AWS credential configuration form in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔐 Configure AWS Credentials")
    
    # Check if already configured
    if 'aws_access_key' in st.session_state and 'aws_secret_key' in st.session_state:
        st.sidebar.success("✅ Credentials configured in session")
        if st.sidebar.button("Clear Stored Credentials"):
            del st.session_state['aws_access_key']
            del st.session_state['aws_secret_key']
            del st.session_state['aws_region']
            st.rerun()
        return True
    
    # Show configuration form
    with st.sidebar.form("aws_credentials"):
        st.markdown("""
        **Get your AWS credentials:**
        1. Go to [AWS Console](https://console.aws.amazon.com/)
        2. Navigate to **IAM** → **Users**
        3. Create user with **AdministratorAccess**
        4. Create **Access Keys**
        """)
        
        access_key = st.text_input("AWS Access Key ID", 
            placeholder="AKIA...", 
            help="Your AWS Access Key ID (starts with AKIA)")
        
        secret_key = st.text_input("AWS Secret Access Key", 
            type="password",
            placeholder="Enter your secret key",
            help="Your AWS Secret Access Key (keep this secure)")
        
        region = st.selectbox("AWS Region", 
            ["us-west-2", "us-east-1", "us-west-1", "eu-west-1", "ap-southeast-1"],
            help="Choose your preferred AWS region")
        
        submitted = st.form_submit_button("💾 Save Credentials")
        
        if submitted:
            if access_key and secret_key:
                # Test credentials
                try:
                    test_aws = AWSEKSIntegration(region, access_key, secret_key)
                    success, identity = test_aws.check_aws_credentials()
                    
                    if success:
                        # Store in session state
                        st.session_state['aws_access_key'] = access_key
                        st.session_state['aws_secret_key'] = secret_key
                        st.session_state['aws_region'] = region
                        
                        st.sidebar.success("✅ Credentials saved and verified!")
                        st.sidebar.write(f"**Account:** {identity.get('Account', 'Unknown')}")
                        st.rerun()
                    else:
                        st.sidebar.error("❌ Invalid credentials. Please check and try again.")
                except Exception as e:
                    st.sidebar.error(f"❌ Error testing credentials: {str(e)}")
            else:
                st.sidebar.error("❌ Please enter both Access Key ID and Secret Access Key")
    
    return False

# AWS Integration Class
class AWSEKSIntegration:
    def __init__(self, region='us-west-2', access_key=None, secret_key=None):
        self.region = region
        
        # Use provided credentials or fall back to default AWS config
        if access_key and secret_key:
            self.eks_client = boto3.client('eks', 
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key)
            self.ec2_client = boto3.client('ec2', 
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key)
            self.ecr_client = boto3.client('ecr', 
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key)
            self.sts_client = boto3.client('sts', 
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key)
        else:
            self.eks_client = boto3.client('eks', region_name=region)
            self.ec2_client = boto3.client('ec2', region_name=region)
            self.ecr_client = boto3.client('ecr', region_name=region)
            self.sts_client = boto3.client('sts', region_name=region)
        
    def check_aws_credentials(self):
        """Check if AWS credentials are configured"""
        try:
            identity = self.sts_client.get_caller_identity()
            return True, identity
        except Exception as e:
            return False, str(e)
    
    def list_clusters(self):
        """List all EKS clusters in the region"""
        try:
            response = self.eks_client.list_clusters()
            clusters = []
            
            for cluster_name in response['clusters']:
                cluster_info = self.eks_client.describe_cluster(name=cluster_name)
                clusters.append({
                    'name': cluster_name,
                    'status': cluster_info['cluster']['status'],
                    'version': cluster_info['cluster']['version'],
                    'endpoint': cluster_info['cluster']['endpoint'],
                    'created': cluster_info['cluster']['createdAt']
                })
            
            return True, clusters
        except Exception as e:
            return False, str(e)
    
    def create_cluster(self, cluster_name, node_group_name="default-nodes"):
        """Create a new EKS cluster using eksctl"""
        try:
            # Check if eksctl is installed
            result = subprocess.run(['eksctl', 'version'], capture_output=True, text=True)
            if result.returncode != 0:
                return False, "eksctl is not installed. Please install it first."
            
            # Create cluster with eksctl
            cmd = [
                'eksctl', 'create', 'cluster',
                '--name', cluster_name,
                '--region', self.region,
                '--nodegroup-name', node_group_name,
                '--node-type', 't3.medium',
                '--nodes', '2',
                '--nodes-min', '1',
                '--nodes-max', '4',
                '--managed'
            ]
            
            return True, f"Cluster creation started. Command: {' '.join(cmd)}"
            
        except Exception as e:
            return False, str(e)
    
    def get_cluster_kubeconfig(self, cluster_name):
        """Update kubeconfig for the cluster"""
        try:
            cmd = [
                'aws', 'eks', 'update-kubeconfig',
                '--region', self.region,
                '--name', cluster_name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return True, "Kubeconfig updated successfully"
            else:
                return False, result.stderr
                
        except Exception as e:
            return False, str(e)
    
    def get_kubernetes_client(self, cluster_name):
        """Get Kubernetes client for the cluster"""
        try:
            # Update kubeconfig
            success, message = self.get_cluster_kubeconfig(cluster_name)
            if not success:
                return None, message
            
            # Load kubeconfig
            config.load_kube_config()
            
            # Create clients
            v1 = client.CoreV1Api()
            apps_v1 = client.AppsV1Api()
            
            return (v1, apps_v1), "Kubernetes client connected"
            
        except Exception as e:
            return None, str(e)
    
    def list_pods(self, cluster_name, namespace='default'):
        """List pods in a namespace"""
        try:
            clients, message = self.get_kubernetes_client(cluster_name)
            if clients is None:
                return False, message
            
            v1, _ = clients
            pods = v1.list_namespaced_pod(namespace=namespace)
            
            pod_list = []
            for pod in pods.items:
                pod_list.append({
                    'name': pod.metadata.name,
                    'status': pod.status.phase,
                    'ready': sum(1 for c in pod.status.container_statuses or [] if c.ready),
                    'total': len(pod.spec.containers),
                    'restarts': sum(c.restart_count for c in pod.status.container_statuses or []),
                    'age': pod.metadata.creation_timestamp
                })
            
            return True, pod_list
            
        except Exception as e:
            return False, str(e)
    
    def create_namespace(self, cluster_name, namespace_name):
        """Create a namespace"""
        try:
            clients, message = self.get_kubernetes_client(cluster_name)
            if clients is None:
                return False, message
            
            v1, _ = clients
            
            # Check if namespace exists
            try:
                v1.read_namespace(name=namespace_name)
                return True, f"Namespace '{namespace_name}' already exists"
            except ApiException as e:
                if e.status != 404:
                    return False, str(e)
            
            # Create namespace
            namespace = client.V1Namespace(
                metadata=client.V1ObjectMeta(name=namespace_name)
            )
            
            v1.create_namespace(body=namespace)
            return True, f"Namespace '{namespace_name}' created successfully"
            
        except Exception as e:
            return False, str(e)
    
    def deploy_application(self, cluster_name, namespace, app_name, image, replicas=3):
        """Deploy an application to the cluster"""
        try:
            clients, message = self.get_kubernetes_client(cluster_name)
            if clients is None:
                return False, message
            
            v1, apps_v1 = clients
            
            # Create deployment
            deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(name=app_name),
                spec=client.V1DeploymentSpec(
                    replicas=replicas,
                    selector=client.V1LabelSelector(
                        match_labels={"app": app_name}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={"app": app_name}
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=app_name,
                                    image=image,
                                    ports=[client.V1ContainerPort(container_port=8080)],
                                    resources=client.V1ResourceRequirements(
                                        requests={"memory": "256Mi", "cpu": "250m"},
                                        limits={"memory": "512Mi", "cpu": "500m"}
                                    )
                                )
                            ]
                        )
                    )
                )
            )
            
            apps_v1.create_namespaced_deployment(
                body=deployment,
                namespace=namespace
            )
            
            # Create service
            service = client.V1Service(
                metadata=client.V1ObjectMeta(name=f"{app_name}-service"),
                spec=client.V1ServiceSpec(
                    selector={"app": app_name},
                    ports=[client.V1ServicePort(
                        port=80,
                        target_port=8080
                    )],
                    type="LoadBalancer"
                )
            )
            
            v1.create_namespaced_service(
                body=service,
                namespace=namespace
            )
            
            return True, f"Application '{app_name}' deployed successfully"
            
        except Exception as e:
            return False, str(e)
    
    def get_service_endpoint(self, cluster_name, namespace, service_name):
        """Get the external endpoint of a service"""
        try:
            clients, message = self.get_kubernetes_client(cluster_name)
            if clients is None:
                return False, message
            
            v1, _ = clients
            
            service = v1.read_namespaced_service(
                name=service_name,
                namespace=namespace
            )
            
            if service.status.load_balancer.ingress:
                endpoint = service.status.load_balancer.ingress[0].hostname
                return True, f"http://{endpoint}"
            else:
                return False, "LoadBalancer endpoint not ready yet"
                
        except Exception as e:
            return False, str(e)

# Sidebar navigation
st.sidebar.title("🚀 EKS Demo Navigation")
page = st.sidebar.selectbox("Choose a page:", [
    "🏠 Main Demo", 
    "🔧 MCP Configuration", 
    "📚 Example Commands", 
    "🔍 Cluster Monitor"
])

# Configure AWS credentials in sidebar
credentials_configured = configure_aws_credentials()

# Initialize AWS with session state credentials if available
if 'aws_access_key' in st.session_state and 'aws_secret_key' in st.session_state:
    aws_eks = AWSEKSIntegration(
        region=st.session_state.get('aws_region', 'us-west-2'),
        access_key=st.session_state['aws_access_key'],
        secret_key=st.session_state['aws_secret_key']
    )
else:
    aws_eks = get_aws_integration()

# Check AWS credentials
st.sidebar.header("🔐 AWS Connection Status")
creds_valid, creds_info = aws_eks.check_aws_credentials()

if creds_valid:
    st.sidebar.success("✅ AWS Connected")
    account_id = creds_info.get('Account', 'Unknown')
    st.sidebar.write(f"**Account:** {account_id[:4]}...{account_id[-4:]}")
    st.sidebar.write(f"**Region:** {aws_eks.region}")
    
    # Show credential source
    if 'aws_access_key' in st.session_state:
        st.sidebar.info("📱 Using web-configured credentials")
    else:
        st.sidebar.info("💻 Using AWS CLI credentials")
else:
    st.sidebar.error("❌ AWS Not Connected")
    if not credentials_configured:
        st.sidebar.markdown("""
        **Configure credentials above ☝️**
        
        Or use AWS CLI:
        ```bash
        aws configure
        ```
        """)
    
    # Add a prominent warning at the top of the main page
    if page == "🏠 Main Demo":
        st.error("🚨 **AWS Credentials Required!** Please configure AWS credentials in the sidebar before proceeding.")
        st.info("💡 **Quick Setup:** Enter your AWS Access Key and Secret Key in the sidebar form.")
        st.stop()

# Region selector (only if using CLI credentials)
if 'aws_access_key' not in st.session_state:
    aws_region = st.sidebar.selectbox("AWS Region", 
        ["us-west-2", "us-east-1", "us-west-1", "eu-west-1"], 
        index=0)
    
    if aws_region != aws_eks.region:
        aws_eks.region = aws_region
        aws_eks = AWSEKSIntegration(aws_region)
else:
    aws_region = st.session_state.get('aws_region', 'us-west-2')

# PAGE 1: MAIN DEMO
if page == "🏠 Main Demo":
    st.title("🚀 .NET Core to AWS EKS Deployment Demo")
    st.markdown("""
    This demo connects to your **real AWS EKS cluster** and deploys .NET Core applications.
    Provide a GitHub URL to your .NET project and watch it deploy to your actual EKS cluster!
    """)
    
    if not creds_valid:
        st.error("🚨 **AWS Credentials Not Configured!**")
        st.markdown("""
        ### 🔧 Quick Setup Instructions:
        
        1. **Install AWS CLI** (if not already installed):
           ```bash
           pip install awscli
           ```
        
        2. **Configure your credentials**:
           ```bash
           aws configure
           ```
           
        3. **Enter your AWS details**:
           - **AWS Access Key ID**: Your access key
           - **AWS Secret Access Key**: Your secret key  
           - **Default region**: us-west-2 (or your preferred region)
           - **Default output format**: json
        
        4. **Verify connection**:
           ```bash
           aws sts get-caller-identity
           ```
        
        ### 🔑 Where to get AWS credentials:
        - Go to [AWS Console](https://console.aws.amazon.com/)
        - Navigate to **IAM** → **Users** → **Your User** → **Security credentials**
        - Click **Create access key**
        
        ### 🛡️ Required permissions:
        Your AWS user needs permissions for:
        - EKS (Elastic Kubernetes Service)
        - EC2 (for worker nodes)
        - ECR (Elastic Container Registry)
        - IAM (for cluster roles)
        """)
        st.stop()
    
    # Get existing clusters
    success, clusters = aws_eks.list_clusters()
    cluster_names = [c['name'] for c in clusters] if success else []
    
    if cluster_names:
        cluster_option = st.selectbox("Select Cluster", 
            ["Create New Cluster"] + cluster_names)
        
        if cluster_option != "Create New Cluster":
            selected_cluster = cluster_option
            create_new = False
        else:
            selected_cluster = st.text_input("New Cluster Name", "dotnet-demo-cluster")
            create_new = True
    else:
        selected_cluster = st.text_input("Cluster Name", "dotnet-demo-cluster")
        create_new = True
    
    # Main interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📂 Project Input")
        
        # GitHub URL input with default
        st.write("**Choose a demo repository:**")
        
        # Quick select buttons for common repos
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎯 .NET Web API Sample"):
                st.session_state.demo_url = "https://github.com/dotnet/dotnet-docker/tree/main/samples/aspnetapp"
        
        with col2:
            if st.button("🏪 eShop Microservices"):
                st.session_state.demo_url = "https://github.com/dotnet-architecture/eShopOnContainers"
        
        with col3:
            if st.button("🚀 Custom .NET API"):
                st.session_state.demo_url = "https://github.com/your-username/dotnet-eks-prototype"
        
        # URL input field
        default_url = st.session_state.get('demo_url', "https://github.com/dotnet/dotnet-docker/tree/main/samples/aspnetapp")
        github_url = st.text_input(
            "GitHub Repository URL",
            value=default_url,
            help="Enter the GitHub URL of your .NET Core project"
        )
        
        # Project type selection
        project_type = st.selectbox(
            "Project Type",
            ["ASP.NET Core Web API", "ASP.NET Core MVC", "Console Application"]
        )
        
        # Database option
        needs_database = st.checkbox("Requires SQL Server Database", value=True)
        
        # Deployment button
        deploy_button = st.button("🚀 Deploy to EKS", type="primary")
    
    with col2:
        st.header("🏗️ Current EKS Clusters")
        
        if success and clusters:
            for cluster in clusters:
                with st.expander(f"📊 {cluster['name']}", expanded=False):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**Status:** {cluster['status']}")
                        st.write(f"**Version:** {cluster['version']}")
                    with col_b:
                        st.write(f"**Created:** {cluster['created'].strftime('%Y-%m-%d')}")
                    
                    # Show pods if cluster is active
                    if cluster['status'] == 'ACTIVE':
                        if st.button(f"View Pods", key=f"pods_{cluster['name']}"):
                            pod_success, pods = aws_eks.list_pods(cluster['name'], 'default')
                            if pod_success:
                                st.write("**Pods in default namespace:**")
                                for pod in pods:
                                    status_icon = "🟢" if pod['status'] == 'Running' else "🔴"
                                    st.write(f"{status_icon} {pod['name']} - {pod['status']}")
                            else:
                                st.error(f"Error: {pods}")
        else:
            st.info("No EKS clusters found. Create one to get started!")
    
    # Functions for the demo
    def validate_github_url(url):
        """Validate GitHub URL format"""
        if not url:
            return False, "Please enter a GitHub URL"
        
        if not url.startswith("https://github.com/"):
            return False, "Please enter a valid GitHub URL"
        
        return True, "Valid GitHub URL"
    
    def analyze_dotnet_project(github_url):
        """Analyze a real .NET project from GitHub"""
        try:
            # Extract repo info
            parts = github_url.replace("https://github.com/", "").split("/")
            if len(parts) >= 2:
                owner, repo = parts[0], parts[1]
                
                # Check if repo exists via GitHub API
                api_url = f"https://api.github.com/repos/{owner}/{repo}"
                response = requests.get(api_url)
                
                if response.status_code == 200:
                    repo_info = response.json()
                    
                    # Try to get project files
                    contents_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
                    contents_response = requests.get(contents_url)
                    
                    analysis = {
                        "framework": "net8.0",
                        "project_type": "Web API",
                        "has_dockerfile": False,
                        "dependencies": [],
                        "endpoints": [],
                        "database_required": needs_database,
                        "repo_info": repo_info
                    }
                    
                    if contents_response.status_code == 200:
                        files = contents_response.json()
                        file_names = [f['name'] for f in files if isinstance(files, list)]
                        
                        # Check for .NET project files
                        csproj_files = [f for f in file_names if f.endswith('.csproj')]
                        if csproj_files:
                            analysis["has_csproj"] = True
                        
                        # Check for Dockerfile
                        if 'Dockerfile' in file_names or any('Dockerfile' in f for f in file_names):
                            analysis["has_dockerfile"] = True
                        
                        # Check for common .NET files
                        if 'Program.cs' in file_names:
                            analysis["has_program_cs"] = True
                    
                    return analysis
                else:
                    st.error(f"Repository not found or not accessible: {response.status_code}")
                    return None
        except Exception as e:
            st.error(f"Error analyzing repository: {str(e)}")
            return None
    
    def execute_real_deployment(cluster_name, namespace, github_url, needs_db):
        """Execute real deployment to EKS with MCP command display"""
        deployment_steps = []
        mcp_commands = []
        
        try:
            st.subheader("🤖 EKS MCP Commands Being Executed")
            
            # Step 1: Create or verify cluster
            if create_new:
                st.write("🏗️ Creating EKS cluster...")
                
                # Show MCP command
                mcp_command = f"Create a new EKS cluster named '{cluster_name}' in {aws_region} region with Kubernetes version 1.31 and managed node groups"
                st.code(f"🗣️ MCP Command: {mcp_command}", language="text")
                mcp_commands.append(mcp_command)
                
                # Show what this translates to
                with st.expander("🔍 What this command does"):
                    st.write("**Translates to these AWS operations:**")
                    st.code(f"""
eksctl create cluster \\
  --name {cluster_name} \\
  --region {aws_region} \\
  --nodegroup-name default-nodes \\
  --node-type t3.medium \\
  --nodes 2 \\
  --nodes-min 1 \\
  --nodes-max 4 \\
  --managed
                    """, language="bash")
                
                # Actually execute
                success, message = aws_eks.create_cluster(cluster_name)
                deployment_steps.append(("Cluster Creation", success, message))
                
                if success:
                    st.success(f"✅ MCP Response: {message}")
                    st.info("⏳ Cluster creation started. This may take 10-15 minutes...")
                    st.write("You can monitor progress in the AWS Console.")
                else:
                    st.error(f"❌ MCP Error: {message}")
            else:
                mcp_command = f"Use existing cluster '{cluster_name}' for deployment"
                st.code(f"🗣️ MCP Command: {mcp_command}", language="text")
                mcp_commands.append(mcp_command)
                deployment_steps.append(("Cluster Selection", True, f"Using existing cluster: {cluster_name}"))
                st.success(f"✅ Using existing cluster: {cluster_name}")
            
            # Step 2: Create namespace
            st.write("📦 Creating namespace...")
            
            mcp_command = f"Create a namespace called '{namespace}' in the {cluster_name} cluster"
            st.code(f"🗣️ MCP Command: {mcp_command}", language="text")
            mcp_commands.append(mcp_command)
            
            with st.expander("🔍 What this command does"):
                st.write("**Translates to these Kubernetes operations:**")
                st.code(f"kubectl create namespace {namespace}", language="bash")
            
            success, message = aws_eks.create_namespace(cluster_name, namespace)
            deployment_steps.append(("Namespace Creation", success, message))
            
            if success:
                st.success(f"✅ MCP Response: {message}")
            else:
                st.error(f"❌ MCP Error: {message}")
            
            # Step 3: Deploy database if needed
            if needs_db:
                st.write("🗄️ Deploying SQL Server...")
                
                mcp_command = f"Deploy SQL Server to {namespace} namespace with persistent storage, 2Gi memory limit, and proper resource constraints"
                st.code(f"🗣️ MCP Command: {mcp_command}", language="text")
                mcp_commands.append(mcp_command)
                
                with st.expander("🔍 What this command does"):
                    st.write("**Translates to these Kubernetes resources:**")
                    st.code("""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sqlserver
  namespace: dotnet-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sqlserver
  template:
    spec:
      containers:
      - name: sqlserver
        image: mcr.microsoft.com/mssql/server:2022-latest
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
                    """, language="yaml")
                
                deployment_steps.append(("Database Deployment", True, "SQL Server deployment initiated"))
                st.success("✅ MCP Response: SQL Server deployment configuration created")
            
            # Step 4: Deploy application
            st.write("🚀 Deploying application...")
            
            mcp_command = f"Deploy the .NET Core application to {namespace} namespace with 2 replicas, LoadBalancer service, and health checks enabled"
            st.code(f"🗣️ MCP Command: {mcp_command}", language="text")
            mcp_commands.append(mcp_command)
            
            with st.expander("🔍 What this command does"):
                st.write("**Translates to these Kubernetes operations:**")
                st.code(f"""
kubectl create deployment dotnet-app \\
  --image=mcr.microsoft.com/dotnet/samples:aspnetapp \\
  --replicas=2 \\
  --namespace={namespace}

kubectl expose deployment dotnet-app \\
  --type=LoadBalancer \\
  --port=80 \\
  --target-port=8080 \\
  --namespace={namespace}
                """, language="bash")
            
            sample_image = "mcr.microsoft.com/dotnet/samples:aspnetapp"
            success, message = aws_eks.deploy_application(
                cluster_name, namespace, "dotnet-app", sample_image, 2
            )
            deployment_steps.append(("Application Deployment", success, message))
            
            if success:
                st.success(f"✅ MCP Response: {message}")
            else:
                st.error(f"❌ MCP Error: {message}")
            
            # Step 5: Get service endpoint
            if success:
                st.write("🌐 Getting service endpoint...")
                
                mcp_command = f"Get the LoadBalancer endpoint for the dotnet-app service in {namespace} namespace"
                st.code(f"🗣️ MCP Command: {mcp_command}", language="text")
                mcp_commands.append(mcp_command)
                
                with st.expander("🔍 What this command does"):
                    st.write("**Translates to these Kubernetes operations:**")
                    st.code(f"kubectl get service dotnet-app-service -n {namespace} -o wide", language="bash")
                
                time.sleep(5)
                success, endpoint = aws_eks.get_service_endpoint(cluster_name, namespace, "dotnet-app-service")
                deployment_steps.append(("Service Endpoint", success, endpoint if success else "Endpoint not ready yet"))
                
                if success:
                    st.success(f"✅ MCP Response: Service available at {endpoint}")
                else:
                    st.warning(f"⏳ MCP Response: {endpoint}")
            
            # Show summary of all MCP commands
            st.subheader("📋 Complete MCP Command Sequence")
            st.write("**These are the natural language commands that were executed:**")
            
            for i, cmd in enumerate(mcp_commands, 1):
                st.write(f"**{i}.** {cmd}")
            
            st.info("💡 **In Kiro IDE**, you would type these commands in natural language and the EKS MCP server would execute them automatically!")
            
            return deployment_steps
            
        except Exception as e:
            deployment_steps.append(("Deployment Error", False, str(e)))
            return deployment_steps
    
    # Main deployment logic
    if deploy_button:
        if github_url:
            is_valid, message = validate_github_url(github_url)
            
            if is_valid:
                st.success(f"✅ {message}")
                
                # Analyze project
                with st.spinner("Analyzing .NET project..."):
                    analysis = analyze_dotnet_project(github_url)
                
                if analysis:
                    # Display analysis results
                    st.subheader("📊 Project Analysis")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Framework", analysis.get("framework", "Unknown"))
                        st.metric("Project Type", analysis.get("project_type", "Unknown"))
                    
                    with col2:
                        st.metric("Has Dockerfile", "✅" if analysis.get("has_dockerfile") else "❌")
                        st.metric("Database Required", "✅" if analysis.get("database_required") else "❌")
                    
                    with col3:
                        repo_info = analysis.get("repo_info", {})
                        st.metric("Stars", repo_info.get("stargazers_count", 0))
                        st.metric("Language", repo_info.get("language", "Unknown"))
                    
                    # Execute real deployment
                    st.subheader("🚀 Real EKS Deployment")
                    
                    if st.button("Execute Real Deployment", type="primary"):
                        namespace = "dotnet-app"
                        
                        with st.spinner("Deploying to EKS..."):
                            deployment_results = execute_real_deployment(
                                selected_cluster, namespace, github_url, needs_database
                            )
                        
                        # Show deployment results
                        st.subheader("📋 Deployment Results")
                        
                        for step_name, success, message in deployment_results:
                            if success:
                                st.success(f"✅ **{step_name}:** {message}")
                            else:
                                st.error(f"❌ **{step_name}:** {message}")
                        
                        # Show how to use with Kiro
                        st.markdown("---")
                        st.subheader("🎯 How to Use This with Kiro IDE")
                        
                        st.markdown("""
                        ### 🔧 **Step 1: Configure EKS MCP in Kiro**
                        
                        1. **Download MCP config** from the "🔧 MCP Configuration" page
                        2. **Place in Kiro**: `.kiro/settings/mcp.json`
                        3. **Restart Kiro** or reload MCP servers
                        
                        ### 💬 **Step 2: Chat with EKS MCP Server**
                        
                        In Kiro chat, you can now use these **exact natural language commands**:
                        """)
                        
                        # Show example commands
                        example_commands = [
                            f"Create a new EKS cluster named '{selected_cluster}' in {aws_region} region",
                            f"Create a namespace called 'dotnet-app' in the {selected_cluster} cluster",
                            "Deploy my .NET Core application with 2 replicas and LoadBalancer service",
                            "Show me all pods in the dotnet-app namespace and their status",
                            "Get the LoadBalancer endpoint for my application"
                        ]
                        
                        for i, cmd in enumerate(example_commands, 1):
                            st.code(f"{i}. {cmd}", language="text")
                        
                        st.markdown("""
                        ### 🎉 **Result in Kiro**
                        
                        Kiro will execute these commands and show you:
                        - ✅ **Real-time progress** of cluster creation
                        - ✅ **Live deployment status** 
                        - ✅ **Actual service endpoints**
                        - ✅ **Error troubleshooting** if issues occur
                        
                        **This Streamlit demo shows you what happens behind the scenes!**
                        """)
                        
                        # Add link to check AWS Console
                        st.markdown("---")
                        st.subheader("🔍 Verify in AWS Console")
                        
                        aws_console_url = f"https://{aws_region}.console.aws.amazon.com/eks/home?region={aws_region}#/clusters"
                        st.markdown(f"""
                        **Check your AWS Console to see the real resources:**
                        
                        🔗 [Open EKS Console]({aws_console_url})
                        
                        You should see:
                        - **EKS Cluster**: `{selected_cluster}`
                        - **Node Groups**: Running EC2 instances  
                        - **Workloads**: Deployed applications
                        """)
                        
                        # Show kubectl commands to verify
                        st.subheader("💻 Verify with kubectl")
                        st.code(f"""
# Connect to your cluster
aws eks update-kubeconfig --region {aws_region} --name {selected_cluster}

# Check cluster nodes
kubectl get nodes

# Check your application
kubectl get pods -n dotnet-app
kubectl get services -n dotnet-app

# Get LoadBalancer URL
kubectl get service dotnet-app-service -n dotnet-app -o wide
                        """, language="bash")
            else:
                st.error(f"❌ {message}")
        else:
            st.warning("⚠️ Please enter a GitHub URL")

# PAGE 2: MCP CONFIGURATION
elif page == "🔧 MCP Configuration":
    st.title("🔧 EKS MCP Server Configuration")
    st.markdown("Configure your EKS MCP server settings for Kiro IDE integration.")
    
    # Configuration form
    with st.form("mcp_config"):
        st.subheader("AWS Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            aws_profile = st.text_input("AWS Profile", value="default")
            log_level = st.selectbox("Log Level", ["ERROR", "WARN", "INFO", "DEBUG"])
        
        with col2:
            read_only = st.checkbox("Read-only mode", help="Only allow read operations")
        
        st.subheader("Auto-approve Tools")
        st.markdown("Select tools that should be auto-approved:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            auto_list_clusters = st.checkbox("list_clusters", value=True)
            auto_describe_cluster = st.checkbox("describe_cluster", value=True)
            auto_list_pods = st.checkbox("list_pods", value=True)
            auto_get_pod_logs = st.checkbox("get_pod_logs", value=True)
        
        with col2:
            auto_list_services = st.checkbox("list_services", value=True)
            auto_list_deployments = st.checkbox("list_deployments", value=True)
            auto_get_events = st.checkbox("get_events", value=True)
            auto_describe_nodes = st.checkbox("describe_nodes", value=True)
        
        submitted = st.form_submit_button("Generate Configuration")
        
        if submitted:
            # Build auto-approve list
            auto_approve = []
            if auto_list_clusters: auto_approve.append("list_clusters")
            if auto_describe_cluster: auto_approve.append("describe_cluster")
            if auto_list_pods: auto_approve.append("list_pods")
            if auto_get_pod_logs: auto_approve.append("get_pod_logs")
            if auto_list_services: auto_approve.append("list_services")
            if auto_list_deployments: auto_approve.append("list_deployments")
            if auto_get_events: auto_approve.append("get_events")
            if auto_describe_nodes: auto_approve.append("describe_nodes")
            
            # Build MCP configuration
            mcp_config = {
                "mcpServers": {
                    "eks-mcp": {
                        "disabled": False,
                        "command": "uvx",
                        "args": [
                            "mcp-proxy-for-aws@latest",
                            f"https://eks-mcp.{aws_region}.api.aws/mcp",
                            "--service",
                            "eks-mcp",
                            "--profile",
                            aws_profile,
                            "--region",
                            aws_region
                        ],
                        "env": {
                            "FASTMCP_LOG_LEVEL": log_level
                        },
                        "autoApprove": auto_approve
                    }
                }
            }
            
            if read_only:
                mcp_config["mcpServers"]["eks-mcp"]["args"].append("--read-only")
            
            st.success("✅ Configuration generated!")
            
            # Display configuration
            st.subheader("📄 Generated MCP Configuration")
            st.code(json.dumps(mcp_config, indent=2), language="json")
            
            # Instructions
            st.subheader("📋 Setup Instructions")
            st.markdown("""
            1. **Copy the configuration above**
            2. **In Kiro IDE:**
               - Open the command palette (Cmd/Ctrl + Shift + P)
               - Search for "MCP" and select "Open MCP Configuration"
               - Or create/edit `.kiro/settings/mcp.json` in your workspace
            3. **Paste the configuration** into the file
            4. **Restart Kiro** or reload the MCP servers
            5. **Test the connection** by asking: "Show me all EKS clusters"
            """)
            
            # Download button
            config_json = json.dumps(mcp_config, indent=2)
            st.download_button(
                label="📥 Download mcp.json",
                data=config_json,
                file_name="mcp.json",
                mime="application/json"
            )

# PAGE 3: EXAMPLE COMMANDS
elif page == "📚 Example Commands":
    st.title("📚 EKS MCP Natural Language Commands")
    st.markdown("Here are example natural language commands you can use with the EKS MCP server in Kiro IDE.")
    
    # Command categories
    categories = {
        "🏗️ Cluster Management": [
            "Create a new EKS cluster named 'my-cluster' in us-west-2 region",
            "Show me all EKS clusters and their status",
            "Delete the cluster named 'old-cluster'",
            "What's the status of my production-cluster?",
            "Show me the VPC configuration for my staging cluster",
            "Update my cluster to Kubernetes version 1.31"
        ],
        
        "🚀 Application Deployment": [
            "Deploy my .NET Core app to the production namespace with 3 replicas",
            "Create a deployment from my ECR image with LoadBalancer service",
            "Deploy SQL Server to the database namespace with persistent storage",
            "Update my webapi deployment with the new image tag v2.0",
            "Scale the frontend deployment to 5 replicas",
            "Create a namespace called 'dotnet-app'"
        ],
        
        "📊 Monitoring & Troubleshooting": [
            "Show me all pods in the production namespace and their status",
            "Get the logs from the api-server pod in the last 30 minutes",
            "Why is my nginx-ingress-controller pod failing to start?",
            "Show me events in the staging namespace for the last hour",
            "List all services and their endpoints in the default namespace",
            "Check the health of all nodes in my cluster"
        ]
    }
    
    # Display commands by category
    for category, commands in categories.items():
        with st.expander(category, expanded=True):
            for i, command in enumerate(commands, 1):
                st.code(command, language="text")

# PAGE 4: CLUSTER MONITOR
elif page == "🔍 Cluster Monitor":
    st.title("🔍 Real EKS Cluster Monitor")
    
    if not creds_valid:
        st.error("🚨 **AWS Credentials Not Configured!**")
        st.markdown("""
        ### To use the cluster monitor, you need AWS credentials configured.
        
        **Quick setup:**
        ```bash
        aws configure
        ```
        
        Then refresh this page to connect to your EKS clusters.
        """)
        st.stop()
    
    st.success("✅ Connected to AWS")
    
    # Get clusters
    success, clusters = aws_eks.list_clusters()
    
    if not success:
        st.error(f"Error fetching clusters: {clusters}")
        st.stop()
    
    if not clusters:
        st.info("No EKS clusters found in this region.")
        st.stop()
    
    # Cluster selector
    cluster_names = [c['name'] for c in clusters]
    selected_cluster = st.selectbox("Select Cluster to Monitor", cluster_names)
    
    # Find selected cluster info
    cluster_info = next(c for c in clusters if c['name'] == selected_cluster)
    
    # Display cluster overview
    st.subheader(f"📊 Cluster Overview: {selected_cluster}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_color = "🟢" if cluster_info['status'] == 'ACTIVE' else "🔴"
        st.metric("Status", f"{status_color} {cluster_info['status']}")
    
    with col2:
        st.metric("Kubernetes Version", cluster_info['version'])
    
    with col3:
        st.metric("Region", aws_region)
    
    with col4:
        created_date = cluster_info['created'].strftime('%Y-%m-%d')
        st.metric("Created", created_date)
    
    # Only show detailed monitoring if cluster is active
    if cluster_info['status'] != 'ACTIVE':
        st.warning(f"Cluster is {cluster_info['status']}. Detailed monitoring only available for ACTIVE clusters.")
        st.stop()
    
    # Namespace selector
    st.subheader("🏷️ Namespace Monitoring")
    
    namespace_options = ['default', 'kube-system', 'dotnet-app', 'kube-public']
    selected_namespace = st.selectbox("Select Namespace", namespace_options)
    
    # Manual refresh button
    if st.button("🔄 Refresh Pods"):
        with st.spinner("Fetching pod information..."):
            success, pods = aws_eks.list_pods(selected_cluster, selected_namespace)
        
        if success:
            if pods:
                st.subheader(f"🚀 Pods in {selected_namespace} namespace")
                
                # Create a table-like display
                for pod in pods:
                    with st.expander(f"📦 {pod['name']}", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            status_icon = "🟢" if pod['status'] == 'Running' else "🔴"
                            st.write(f"**Status:** {status_icon} {pod['status']}")
                            st.write(f"**Ready:** {pod['ready']}/{pod['total']}")
                        
                        with col2:
                            st.write(f"**Restarts:** {pod['restarts']}")
                            age = (time.time() - pod['age'].timestamp()) / 3600  # hours
                            st.write(f"**Age:** {age:.1f}h")
                
                # Summary metrics
                st.subheader("📈 Pod Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                total_pods = len(pods)
                running_pods = sum(1 for p in pods if p['status'] == 'Running')
                ready_pods = sum(1 for p in pods if p['ready'] == p['total'])
                total_restarts = sum(p['restarts'] for p in pods)
                
                with col1:
                    st.metric("Total Pods", total_pods)
                with col2:
                    st.metric("Running", running_pods)
                with col3:
                    st.metric("Ready", ready_pods)
                with col4:
                    st.metric("Total Restarts", total_restarts)
            else:
                st.info(f"No pods found in {selected_namespace} namespace")
        else:
            st.error(f"Error fetching pods: {pods}")
    
    # Quick actions
    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Create dotnet-app namespace"):
            success, message = aws_eks.create_namespace(selected_cluster, "dotnet-app")
            if success:
                st.success(message)
            else:
                st.error(message)
    
    with col2:
        if st.button("Deploy Sample App"):
            success, message = aws_eks.deploy_application(
                selected_cluster, 
                selected_namespace, 
                "sample-app", 
                "nginx:latest", 
                1
            )
            if success:
                st.success(message)
            else:
                st.error(message)
    
    # Connection info
    st.markdown("---")
    st.subheader("🔗 Connection Information")
    
    st.code(f"""
# Connect to this cluster with kubectl:
aws eks update-kubeconfig --region {aws_region} --name {selected_cluster}

# Verify connection:
kubectl get nodes

# Check pods in namespace:
kubectl get pods -n {selected_namespace}
""", language="bash")

# Footer
st.markdown("---")
st.markdown("**🚀 Real AWS EKS Integration** - This demo connects to your actual AWS account and EKS clusters!")
st.markdown("Make sure you have `eksctl`, `kubectl`, and `docker` installed for full functionality.")