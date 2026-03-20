# NxLIMS Administrator's Quick Start Guide

## Overview

NxLIMS is a comprehensive Laboratory Information Management System (LIMS) built on Frappe/ERPNext. This guide helps administrators get the system up and running in production.

---

## Quick Setup (20 minutes)

### Prerequisites Checklist

- [ ] Ubuntu 20.04/22.04 LTS server (or equivalent)
- [ ] 4GB+ RAM, 20GB+ disk space
- [ ] Root or sudo access
- [ ] Internet connectivity for initial setup
- [ ] DNS configured (yourdomain.com)
- [ ] SSL certificate ready (or use Let's Encrypt)

### Quickstart Steps

```bash
# 1. Clone and setup
git clone https://github.com/frappe/erpnext.git nxlims
cd nxlims

# 2. Run production setup
bash setup-production.sh production nxlims_production /path/to/bench

# 3. Start services
cd /path/to/bench
bench start

# 4. Access at http://localhost:8000
# Default admin: Administrator / admin_password
```

---

## Key Workflows

### Patient Registration Flow

1. **Reception Desk** logs in with LIMS Reception role
2. **Create New Patient**: NxLIMS → Patient → Create
   - Enter patient name, contact info, referred doctor
   - Save
3. **Register Test**: NxLIMS → Test Registration → Create
   - Select patient
   - Choose tests from catalog
   - Set collection date/time
   - Submit
4. Patient receives SMS/WhatsApp confirmation

### Sample Collection to Result Reporting

1. **Lab Technician** creates lab sample
   - Link to test registration
   - Record collection time/method
2. **Run Tests & enter results**
   - Create result entry
   - Enter test values
   - System auto-flags critical results
3. **Critical alerts** sent to referred doctor
   - Email + SMS + WhatsApp
4. **Patient report** generated
   - Print or email to patient

### Billing & Financial Reporting

1. **Billing Officer** reviews Lab Test Registrations
2. **View Lab Performance Dashboard**
   - Revenue by period
   - Test volume trends
   - Profitability analysis
3. **Generate reports**
   - Financial reports (7/14/30 day)
   - Test statistics
   - Expense tracking

---

## Important Admin Tasks

### 1. Change Default Passwords

```bash
bench --site production shell
```

```python
import frappe
user = frappe.get_doc('User', 'reception@nxlims.local')
user.set_password('NewSecurePassword123!')
user.save()
```

### 2. Configure Email

**Setup → Email Account**

```
SMTP Server: your-smtp-server.com
SMTP Port: 587 (TLS) or 465 (SSL)
Email: noreply@yourdomain.com
Password: [Your email password]
Use TLS: Yes
Sent mail folder: [Sent Items]
```

### 3. Configure SMS (Twilio)

**LIMS → LIMS Settings**

```
Enable SMS: ✓
SMS Provider: Twilio
Account SID: AC...
Auth Token: [Your token]
From Number: +1234567890
```

### 4. Configure WhatsApp

**LIMS → LIMS Settings**

```
Enable WhatsApp: ✓
Webhook URL: https://yourdomain.com/api/method/lims.notifications.handle_whatsapp
```

### 5. Create Lab Test Catalog

```
LIMS → Lab Test Catalog → Create
- Test Name: Hemoglobin
- Sample Type: Blood
- Normal Range: 12.0-17.5 g/dL
- Critical Low: < 7.0
- Critical High: > 20.0
- Price: 500
```

### 6. Enable Offline Sync

```bash
bench --site production console
import frappe
settings = frappe.get_single('LIMS Settings')
settings.enable_offline_sync = 1
settings.sync_batch_limit = 200
settings.save()
```

### 7. Setup Automated Backups

```bash
# Create backup script
sudo mkdir -p /opt/nxlims
sudo cat > /opt/nxlims/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/mnt/backups/nxlims"
DATE=$(date +"%Y%m%d_%H%M%S")

mkdir -p $BACKUP_DIR
cd /path/to/bench
bench backup production $BACKUP_DIR/backup_$DATE --with-files
find $BACKUP_DIR -type f -mtime +30 -delete
EOF

sudo chmod +x /opt/nxlims/backup.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/nxlims/backup.sh") | crontab -
```

---

## User Role Definitions

### LIMS Reception
- Create patient records
- Register new tests
- View test status
- Print patient reports

### LIMS Technician
- Process samples
- Enter test results
- View quality control data
- Manage reagents

### LIMS Billing
- View test registrations
- Manage expenses
- View financial reports
- Generate invoices

### LIMS Manager
- Full system access
- User management
- System configuration
- Report generation
- Audit trail access

---

## Monitoring & Alerts

### Check System Health

```bash
# CPU & Memory usage
top -b -n 1 | head -20

# Database size
mysql -u root -p -e "SELECT table_schema, ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb FROM information_schema.tables GROUP BY table_schema;"

# Redis connectivity
redis-cli ping

# Disk space
df -h
```

### Monitor Application Logs

```bash
# Real-time logs
bench --site production logs

# View error log
bench --site production console
import frappe
logs = frappe.get_all('Error Log', fields=['*'], limit=10)
for log in logs: print(f"{log.creation}: {log.title}")
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| App won't start | Check logs: `bench --site production logs` |
| Can't send email | Verify SMTP settings in Setup > Email Account |
| SMS not working | Check Twilio credentials in LIMS Settings |
| Slow performance | Check database indexes, clear Redis cache |
| Offline sync failing | Verify network, check sync events log |
| User locked out | Run: `bench --site production reset-user [email]` |

---

## Regular Maintenance

### Weekly
- [ ] Check error logs
- [ ] Verify database backups completed
- [ ] Review system resource usage

### Monthly
- [ ] Analyze lab performance dashboard
- [ ] Update SMTP/SMS credentials if needed
- [ ] Review audit trail for suspicious activity
- [ ] Test backup restoration

### Quarterly
- [ ] Security audit
- [ ] Database maintenance
- [ ] Performance optimization
- [ ] Update system packages

---

## Support & Resources

- **Documentation**: See `NXLIMS_PRODUCTION_READINESS.md`
- **Deployment Guide**: See `NXLIMS_DEPLOYMENT_GUIDE.md`
- **Bug Reports**: File issues in GitHub repository
- **Community**: Forum at https://discuss.frappe.io

---

## License

NxLIMS is built on ERPNext (GNU General Public License v3)

**Last Updated**: March 20, 2026
