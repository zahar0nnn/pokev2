# 🚀 AWS EC2 Quick Start Guide

## ⚡ **Quick Deployment (5 minutes)**

### **Step 1: Launch EC2 Instance**
1. Go to AWS EC2 Console
2. Launch Instance → Ubuntu Server 22.04 LTS
3. Instance Type: `t3.small` (or `t2.micro` for free tier)
4. Security Group: Allow SSH (22), HTTP (80), MySQL (3306)
5. Launch with your key pair

### **Step 2: Connect and Deploy**
```bash
# Connect to your instance
ssh -i "your-key.pem" ubuntu@your-ec2-ip

# Download and run deployment script
wget https://raw.githubusercontent.com/yourusername/pokev2/main/deploy-aws.sh
chmod +x deploy-aws.sh
./deploy-aws.sh
```

### **Step 3: Access Your App**
- **Web App**: `http://your-ec2-ip`
- **Database**: `your-ec2-ip:3306`

## 🔧 **Manual Deployment**

### **1. Upload Project Files**
```bash
# On your local machine
scp -i "your-key.pem" -r ./pokev2/* ubuntu@your-ec2-ip:/opt/phygitals/
```

### **2. Configure Environment**
```bash
# On EC2 instance
cd /opt/phygitals
cp env.example .env
nano .env  # Update passwords
```

### **3. Start Services**
```bash
docker-compose -f docker-compose.prod.yaml up -d
```

## 📊 **Monitoring Commands**

```bash
# Check service status
docker-compose -f docker-compose.prod.yaml ps

# View logs
docker-compose -f docker-compose.prod.yaml logs -f

# System monitoring
./monitor.sh

# Run scraper manually
./run_scraper.sh
```

## 🔒 **Security Checklist**

- ✅ Security Group configured (SSH, HTTP, MySQL)
- ✅ Strong passwords in `.env` file
- ✅ UFW firewall enabled
- ✅ Non-root Docker users
- ✅ Log rotation configured
- ✅ Automated backups set up

## 💰 **Cost Optimization**

- **Free Tier**: Use `t2.micro` for testing
- **Production**: Use `t3.small` or larger
- **Storage**: Use EBS gp3 for better price/performance
- **Monitoring**: Set up CloudWatch billing alerts

## 🆘 **Troubleshooting**

### **Web App Not Loading**
```bash
# Check if containers are running
docker ps

# Check webapp logs
docker logs phygitals-webapp

# Test local connection
curl http://localhost:5001/debug
```

### **Database Issues**
```bash
# Check database logs
docker logs phygitals-mysql

# Connect to database
docker exec -it phygitals-mysql mysql -u root -p
```

### **Scraper Issues**
```bash
# Run scraper manually
docker-compose -f docker-compose.prod.yaml run --rm scraper python scraper.py

# Check scraper logs
docker logs phygitals-scraper
```

## 📈 **Scaling Options**

### **Vertical Scaling**
- Upgrade instance type (t3.small → t3.medium)
- Increase EBS volume size

### **Horizontal Scaling**
- Use Application Load Balancer
- Set up Auto Scaling Groups
- Migrate to RDS for database

## 🔄 **Updates and Maintenance**

### **Update Application**
```bash
git pull
docker-compose -f docker-compose.prod.yaml build
docker-compose -f docker-compose.prod.yaml up -d
```

### **Backup Data**
```bash
./backup.sh
ls -la backups/
```

### **Restart Services**
```bash
docker-compose -f docker-compose.prod.yaml restart
```

## 📞 **Support**

- **Logs**: `docker-compose logs -f`
- **Status**: `docker-compose ps`
- **Resources**: `htop`
- **Network**: `curl -I http://localhost:5001`

---

**🎉 Your Phygitals scraper is now running on AWS EC2!**
