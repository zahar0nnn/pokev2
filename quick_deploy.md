# 🚀 Quick EC2 Deployment Commands

## One-Liner Commands

### For Linux/Mac (Bash):
```bash
# Replace YOUR_EC2_IP with your actual EC2 IP address
./deploy_to_ec2.sh YOUR_EC2_IP ubuntu
```

### For Windows (PowerShell):
```powershell
# Replace YOUR_EC2_IP with your actual EC2 IP address
.\deploy_to_ec2.ps1 -EC2IP "YOUR_EC2_IP" -Username "ubuntu"
```

## Manual Commands (if scripts don't work):

### 1. Copy files to EC2:
```bash
scp database.py scraper.py app.py monitor.py start.ps1 docker-compose.yaml Dockerfile.scraper Dockerfile.webapp requirements.txt README.md ubuntu@YOUR_EC2_IP:/home/ubuntu/pokev2/
```

### 2. SSH into EC2 and setup:
```bash
ssh ubuntu@YOUR_EC2_IP
cd /home/ubuntu/pokev2
chmod +x *.py *.sh
pip3 install -r requirements.txt
docker-compose down
docker-compose build
docker-compose up -d
python3 monitor.py
```

## What the deployment does:

1. ✅ **Checks** all required files exist locally
2. ✅ **Creates** remote directory on EC2
3. ✅ **Stops** any running services
4. ✅ **Backs up** existing files
5. ✅ **Copies** all optimized files
6. ✅ **Sets** proper permissions
7. ✅ **Installs** Python dependencies
8. ✅ **Builds** Docker containers
9. ✅ **Starts** all services
10. ✅ **Runs** health check

## After deployment:

- **Web App**: http://YOUR_EC2_IP:5001
- **Monitor**: `ssh ubuntu@YOUR_EC2_IP 'cd /home/ubuntu/pokev2 && python3 monitor.py'`
- **Logs**: `ssh ubuntu@YOUR_EC2_IP 'cd /home/ubuntu/pokev2 && docker-compose logs'`

## Troubleshooting:

If deployment fails:
1. Check SSH key is properly configured
2. Ensure EC2 security group allows port 5001
3. Verify EC2 has Docker installed
4. Check EC2 has enough resources (RAM/CPU)
