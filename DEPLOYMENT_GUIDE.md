# 🚀 EC2 Deployment Guide

## ✅ **Fixed PowerShell Scripts**

The PowerShell syntax errors have been fixed! You now have working deployment scripts:

### **Option 1: Simple PowerShell Script (Recommended)**
```powershell
.\deploy_simple.ps1 -EC2IP "51.20.73.162" -Username "ubuntu"
```

### **Option 2: Windows Batch File**
```cmd
deploy_simple.bat 51.20.73.162 ubuntu
```

### **Option 3: Linux/Mac Bash Script**
```bash
./deploy_to_ec2.sh 51.20.73.162 ubuntu
```

## 🔑 **SSH Key Setup (Required First)**

Before running any deployment script, you need to set up SSH access to your EC2:

### **1. Generate SSH Key (if you don't have one):**
```bash
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
```

### **2. Copy Public Key to EC2:**
```bash
ssh-copy-id ubuntu@51.20.73.162
```

### **3. Test SSH Connection:**
```bash
ssh ubuntu@51.20.73.162
```

## 🚀 **Deployment Steps**

### **Step 1: Setup SSH (One-time)**
```bash
# Generate key if needed
ssh-keygen -t rsa -b 4096

# Copy to EC2
ssh-copy-id ubuntu@51.20.73.162

# Test connection
ssh ubuntu@51.20.73.162 "echo 'SSH working!'"
```

### **Step 2: Deploy Code**
```powershell
# Windows PowerShell
.\deploy_simple.ps1 -EC2IP "51.20.73.162" -Username "ubuntu"
```

### **Step 3: Verify Deployment**
```bash
# Check web app
curl http://51.20.73.162:5001/debug

# Check scraper status
ssh ubuntu@51.20.73.162 "cd /home/ubuntu/pokev2 && python3 monitor.py"
```

## 🔧 **Manual Deployment (If Scripts Fail)**

### **1. Copy Files:**
```bash
scp database.py scraper.py app.py monitor.py start.ps1 docker-compose.yaml Dockerfile.scraper Dockerfile.webapp requirements.txt README.md ubuntu@51.20.73.162:/home/ubuntu/pokev2/
```

### **2. SSH and Setup:**
```bash
ssh ubuntu@51.20.73.162
cd /home/ubuntu/pokev2
chmod +x *.py *.sh
pip3 install -r requirements.txt
docker-compose down
docker-compose build
docker-compose up -d
python3 monitor.py
```

## 🌐 **After Deployment**

- **Web App**: http://51.20.73.162:5001
- **Monitor**: `ssh ubuntu@51.20.73.162 'cd /home/ubuntu/pokev2 && python3 monitor.py'`
- **Logs**: `ssh ubuntu@51.20.73.162 'cd /home/ubuntu/pokev2 && docker-compose logs'`

## 🛠️ **Troubleshooting**

### **SSH Permission Denied:**
1. Check if your SSH key is in `~/.ssh/authorized_keys` on EC2
2. Verify EC2 security group allows SSH (port 22)
3. Make sure you're using the correct username (usually `ubuntu`)

### **Docker Issues:**
1. Ensure Docker is installed on EC2: `sudo apt update && sudo apt install docker.io docker-compose`
2. Add user to docker group: `sudo usermod -aG docker ubuntu`
3. Restart session: `exit` and `ssh` back in

### **Port Issues:**
1. Check EC2 security group allows port 5001
2. Verify no firewall blocking the port

## 📋 **What the Scripts Do**

1. ✅ **Validate** all required files exist
2. ✅ **Create** remote directory on EC2
3. ✅ **Stop** any running services
4. ✅ **Backup** existing files
5. ✅ **Copy** all optimized files
6. ✅ **Set** proper permissions
7. ✅ **Install** Python dependencies
8. ✅ **Build** Docker containers
9. ✅ **Start** all services
10. ✅ **Run** health check

Your deployment scripts are now working correctly! 🎉
