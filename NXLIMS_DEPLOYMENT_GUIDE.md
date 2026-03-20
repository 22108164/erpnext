# NxLIMS Deployment & Administration Guide

Production deployment checklist and procedures for NxLIMS LIMS system.

---

## 1. PRE-DEPLOYMENT REQUIREMENTS

### 1.1 Infrastructure Setup

- **Server Requirements**:
  - Ubuntu 20.04 LTS or CentOS 8+
  - Minimum 4GB RAM, 20GB disk space
  - CPU: 2+ cores
  - Network: 1Gbps connectivity

- **Database**:
  - MariaDB 10.5+ or MySQL 8.0+
  - Dedicated database user with appropriate permissions
  - Automated daily backups to separate storage

- **Redis**:
  - Redis 6.0+ for caching and job scheduling
  - Network isolation: Private subnet only

- **SSL/TLS**:
  - Valid wildcard certificate for *.yourdomain.com
  - Certificate stored in `/etc/ssl/private/` with proper permissions
  - Enable HSTS headers

### 1.2 Network & Security

```bash
# UFW firewall rules (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

### 1.3 System Users

```bash
# Create NxLIMS system user
sudo useradd -m -s /bin/bash nxlims
sudo usermod -aG docker nxlims  # If using Docker
```

---

## 2. DATABASE SETUP

### 2.1 MariaDB Installation & Configuration

```bash
sudo apt update
sudo apt install mariadb-server mariadb-client
sudo mysql_secure_installation

# Create NxLIMS database and user
sudo mysql -u root -p
```

```sql
CREATE DATABASE nxlims_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'nxlims'@'localhost' IDENTIFIED BY 'StrongPassword123!';
GRANT ALL PRIVILEGES ON nxlims_production.* TO 'nxlims'@'localhost';
FLUSH PRIVILEGES;
```

### 2.2 Database Optimization

```sql
-- Performance tuning for MariaDB
SET GLOBAL innodb_buffer_pool_size = 2G;
SET GLOBAL max_connections = 500;
SET GLOBAL query_cache_size = 256M;
SET GLOBAL query_cache_type = 1;

-- Enable binary logging for backup & replication
SET GLOBAL binlog_format = 'ROW';
```

### 2.3 Automated Backups

```bash
# Create backup script at /opt/nxlims/backup.sh
#!/bin/bash

BACKUP_DIR="/mnt/backups/nxlims"
DATE=$(date +"%Y%m%d_%H%M%S")
DB_USER="nxlims"
DB_PASS="StrongPassword123!"
DB_NAME="nxlims_production"

mkdir -p $BACKUP_DIR

# Full database backup
mysqldump -u$DB_USER -p$DB_PASS $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

# Sync to cloud storage (AWS S3 example)
aws s3 sync $BACKUP_DIR s3://nxlims-backups/production/ --region us-east-1

# Create cron job
0 2 * * * /opt/nxlims/backup.sh
```

---

## 3. ERPNext/NxLIMS INSTALLATION

### 3.1 Using Frappe Bench

```bash
# Install Frappe Bench
sudo apt install python3-pip python3-dev python3-venv git
cd /home/nxlims
git clone https://github.com/frappe/bench.git
cd bench && pip install -e .

# Create bench instance
bench init nxlims_prod --frappe-branch develop
cd nxlims_prod

# Create site
bench new-site production --db-name nxlims_production --db-root-password YourPassword

# Download NxLIMS (ERPNext with LIMS customizations)
bench get-app erpnext https://github.com/frappe/erpnext.git
bench --site production install-app erpnext

# Install NxLIMS specific apps if published separately
# bench get-app nxlims https://github.com/your-repo/nxlims.git
# bench --site production install-app nxlims
```

### 3.2 Production Configuration

```bash
# Edit production site config
vim sites/production/site_config.json
```

```json
{
 "db_name": "nxlims_production",
 "db_password": "StrongPassword123!",
 "developer_mode": false,
 "disable_documentation": true,
 "encryption_key": "GenerateWithFrappe",
 "ssl_certificate": "/etc/ssl/certs/yourdomain.crt",
 "ssl_certificate_key": "/etc/ssl/private/yourdomain.key",
 "backend_protocol": "http",
 "session_cookie_secure": true,
 "session_cookie_samesite": "Lax",
 "use_redis_cache": true,
 "redis_cache_db": 0
}
```

### 3.3 Initialize LIMS Module

```bash
bench --site production execute erpnext.patches.v16_0.setup_nxlims_roles
bench --site production execute erpnext.patches.v16_0.configure_lims_only_workspace
```

---

## 4. COMMUNICATION SETUP

### 4.1 SMTP Configuration

```bash
# In NxLIMS: Setup > Email Account
# - SMTP Server: mail.yourdomain.com
# - SMTP Port: 587 (TLS) or 465 (SSL)
# - Email Account: noreply@yourdomain.com
# - Password: EmailPassword123!
# - Use TLS: Yes
```

### 4.2 SMS Provider Setup (Twilio)

```bash
# In NxLIMS: Setup > SMS Settings
# 1. Sign up at https://www.twilio.com
# 2. Get Account SID and Auth Token
# 3. Get a phone number (e.g., +1-555-NXLIMS)

# In LIMS Settings:
# - Enable SMS: ☑
# - SMS Provider: Twilio
# - Account SID: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# - Auth Token: auth_token_here
# - From Number: +15551234567
# - Save
```

### 4.3 WhatsApp Integration (Optional)

```bash
# Setup WhatsApp Business API webhook:
# 1. Register with Meta/WhatsApp Business
# 2. Configure webhook URL: https://yourdomain.com/api/v1/whatsapp
# 3. Get webhook token

# In LIMS Settings:
# - Enable WhatsApp: ☑
# - Webhook URL: https://yourdomain.com/api/v1/whatsapp
# - Save
```

---

## 5. USER ROLES & PERMISSIONS

### 5.1 Create Standard Users

```bash
bench --site production shell

# In Frappe console
import frappe

# Reception user
u = frappe.get_doc({
    'doctype': 'User',
    'email': 'reception@nxlims.local',
    'first_name': 'Reception',
    'last_name': 'Desk',
    'user_type': 'Website User',
    'roles': [{'role': 'LIMS Reception'}]
})
u.insert()

# Lab Technician user
u = frappe.get_doc({
    'doctype': 'User',
    'email': 'technician@nxlims.local',
    'first_name': 'Lab',
    'last_name': 'Technician',
    'user_type': 'Website User',
    'roles': [{'role': 'LIMS Technician'}]
})
u.insert()

# Billing user
u = frappe.get_doc({
    'doctype': 'User',
    'email': 'billing@nxlims.local',
    'first_name': 'Billing',
    'last_name': 'Officer',
    'user_type': 'Website User',
    'roles': [{'role': 'LIMS Billing'}]
})
u.insert()

# Lab Manager user
u = frappe.get_doc({
    'doctype': 'User',
    'email': 'manager@nxlims.local',
    'first_name': 'Lab',
    'last_name': 'Manager',
    'user_type': 'Website User',
    'roles': [{'role': 'LIMS Manager'}]
})
u.insert()
```

### 5.2 Role Permissions Matrix

| Feature | Reception | Technician | Billing | Manager |
|---------|-----------|-----------|---------|---------|
| Patient Registration | Create, Read | Read | - | Read, Write |
| Test Catalog | Read | Read | Read | Read, Write |
| Test Registration | Create, Read, Submit | Read | - | Read, Write, Submit |
| Sample Management | - | Create, Read, Submit | - | Read, Write, Submit |
| Result Entry | - | Create, Read, Submit | - | Read, Write, Submit |
| QC Management | - | Create, Read, Submit | - | Read, Write, Submit |
| Billing/Expense | - | - | Read, Write, Submit | Read, Write, Submit |
| Reports & Analytics | - | Read | Read | Read, Write |
| System Settings | - | - | - | Read, Write |

---

## 6. PERFORMANCE TUNING

### 6.1 Gunicorn Workers

```bash
# Edit /etc/supervisor/conf.d/nxlims.conf
```

```ini
[program:nxlims-bench-worker]
directory=/home/nxlims/nxlims_prod
command=bench worker-b production
autostart=true
autorestart=true
numprocs=4
stdout_logfile=/var/log/nxlims-worker.log

[program:nxlims-bench-web]
directory=/home/nxlims/nxlims_prod
command=bench serve production --port 8000
autostart=true
autorestart=true
stdout_logfile=/var/log/nxlims-web.log
```

### 6.2 Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/nxlims.conf

upstream nxlims_backend {
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    client_max_body_size 50M;

    location / {
        proxy_pass http://nxlims_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120;
    }

    # Static files caching
    location /files/ {
        proxy_pass http://nxlims_backend;
        expires 30d;
    }
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 6.3 Redis Configuration

```bash
# /etc/redis/redis.conf

maxmemory 2GB
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
```

---

## 7. OFFLINE SYNC SETUP

### 7.1 Enable Offline Sync

```bash
bench --site production shell
import frappe

settings = frappe.get_single('LIMS Settings')
settings.enable_offline_sync = 1
settings.sync_batch_limit = 200
settings.save()
```

### 7.2 Desktop App Configuration

Edit `desktop/nxlims-desktop/main.js`:

```javascript
const store = new Store({
    defaults: {
        baseUrl: "https://yourdomain.com",  // Your production URL
        offlineMode: false,
        reloadIntervalMs: 20000
    }
});
```

---

## 8. MONITORING & LOGGING

### 8.1 Application Logs

```bash
# Tail live logs
sudo journalctl -u nxlims-web -f

# Or use Frappe admin
# Setup > Error Log
# Setup > Scheduler > Error Log
```

### 8.2 Database Monitoring

```bash
# Check database size
SELECT 
    table_schema,
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb
FROM information_schema.tables
WHERE table_schema = 'nxlims_production'
GROUP BY table_schema;

# Check slow queries
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

### 8.3 System Health Checks

```bash
#!/bin/bash
# /opt/nxlims/health_check.sh

# Check Redis
redis-cli ping

# Check database connectivity
mysqladmin -u nxlims -p -h localhost status

# Check disk space
df -h | grep -v tmpfs

# Check memory
free -h

# Check CPU load
uptime
```

---

## 9. UPDATES & MAINTENANCE

### 9.1 Application Updates

```bash
# Backup before update
bench backup production

# Update Frappe and ERPNext
cd /home/nxlims/nxlims_prod
bench update

# Restart services
bench restart

# Run migrations
bench --site production migrate
```

### 9.2 Scheduled Maintenance Window

- Schedule updates on **Sunday 02:00 AM**
- Maintenance duration: **30 minutes**
- Notify users 24 hours in advance
- Keep backups for 30 days minimum

---

## 10. DISASTER RECOVERY

### 10.1 Restore from Backup

```bash
# List available backups
aws s3 ls s3://nxlims-backups/production/

# Restore database
aws s3 cp s3://nxlims-backups/production/db_20260320_020000.sql.gz ./
gunzip db_20260320_020000.sql.gz

# Import to fresh database
mysql -u root -p nxlims_production < db_20260320_020000.sql

# Restore from Frappe backup
bench --site production restore 'backup_filename'
```

### 10.2 RTO & RPO Targets

- **RTO (Recovery Time Objective)**: < 1 hour
- **RPO (Recovery Point Objective)**: < 1 hour
- Test recovery procedures monthly

---

## 11. COMPLIANCE & AUDIT

### 11.1 Access Audit Trail

```bash
bench --site production shell
import frappe
from frappe.desk.reportview import get_report_data

# Get audit log
logs = frappe.get_all('Access Log', 
    fields=['*'],
    filters={'creation': ['>=', '2026-03-10']},
    order_by='creation desc'
)
```

### 11.2 Patient Data Encryption

- Enable field-level encryption for sensitive patient identifiers
- Use AES-256 for data at rest
- TLS 1.2+ for data in transit
- GDPR-compliant data retention policies

---

## 12. TROUBLESHOOTING

### Common Issues

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Restart web workers: `bench restart` |
| High CPU Usage | Check background jobs: `Setup > Background Jobs`, optimize queries |
| Slow Database | Run maintenance: `OPTIMIZE TABLE`, check indexes |
| Offline Sync Fails | Check sync settings, verify network connectivity |
| Email Not Sending | Verify SMTP settings under `Setup > Email Account` |

### Performance Profiling

```bash
# Enable query logging
bench --site production set-config developer_mode true
bench --site production set-config db_profiler_threshold 200
```

---

## 13. SUPPORT & ESCALATION

- **Urgent Issues**: Production@yourlims.com (24/7)
- **Non-Urgent**: Support@yourlims.com (Business hours)
- **On-Call Rotation**: Defined in incident response plan

---

**Last Updated**: March 20, 2026
**Version**: 1.0 (Production Ready)
