# NxLIMS Production-Ready LIMS System

**NxLIMS** is a comprehensive, production-ready Laboratory Information Management System (LIMS) built on the Frappe/ERPNext framework, meeting all requirements for modern clinical laboratory operations.

## ✨ Key Features

### Core LIMS Operations
- ✅ **Patient & Test Registration** - Complete patient intake and test ordering
- ✅ **Sample Management** - Specimen tracking and collection workflows
- ✅ **Result Entry** - Comprehensive result recording and validation
- ✅ **Quality Control** - QC data management and compliance
- ✅ **Critical Result Alerts** - Automatic notifications to referred doctors via Email/SMS/WhatsApp

### Data Management & Security
- ✅ **Secure Patient Data** - Field-level encryption, audit trails
- ✅ **Role-Based Access Control** - 4 predefined roles (Manager, Reception, Technician, Billing)
- ✅ **Complete Audit Trail** - All actions logged via LIMS Sync Event tracking
- ✅ **Offline Synchronization** - Full offline operation with automatic data sync on reconnect

### Reporting & Analytics
- ✅ **Lab Performance Dashboard** - Real-time KPIs and metrics
- ✅ **Test Statistics Reports** - Volume, turnaround time, quality metrics
- ✅ **Financial Reports** - Revenue, expense tracking, profit analysis
- ✅ **Flexible Time Windows** - 7-day, fortnightly, monthly profit sheets

### Operational Features
- ✅ **Inventory & Reagent Management** - Chemical/reagent tracking
- ✅ **Email/SMS/WhatsApp Integration** - Multi-channel notifications
- ✅ **Doctor Alerts** - Automatic critical result notifications
- ✅ **Windows Desktop App** - Offline-capable (Electron-based)
- ✅ **Financial Analytics** - Multi-level expense tracking and profit evaluation

---

## 📦 What's Included

```
erpnext/
├── lims/                          # LIMS module
│   ├── doctype/                   # Complete doctype definitions
│   │   ├── lims_patient/          # Patient master data
│   │   ├── lab_test_registration/ # Test registration workflow
│   │   ├── lab_sample/            # Sample management
│   │   ├── lab_result_entry/      # Results & critical alerts
│   │   ├── lab_quality_control/   # QC management
│   │   ├── lab_reagent/           # Inventory management
│   │   ├── lab_expense/           # Expense tracking
│   │   ├── lab_critical_result_alert/ # [NEW] Doctor notifications
│   │   ├── lims_settings/         # Configuration & integrations
│   │   └── lims_sync_event/       # Audit trail & offline sync
│   ├── report/                    # Analytics & reporting
│   │   ├── lims_financial_and_profitability/
│   │   └── lims_test_statistics/
│   ├── sync.py                    # Offline sync API
│   └── notifications.py           # Email/SMS/WhatsApp integration
│
├── patches/v16_0/                 # Migration patches
│   ├── setup_nxlims_roles.py      # LIMS role & permission setup
│   └── configure_lims_only_workspace.py # LIMS-only UI
│
└── hooks.py                       # App configuration & branding

desktop/nxlims-desktop/           # Electron desktop app
├── main.js                        # [ENHANCED] App launcher with IPC
├── package.json                   # [ENHANCED] Build configuration
├── preload.js                     # Secure context bridge
├── offline.html                   # Offline fallback UI
└── assets/                        # Branding assets
```

---

## 🚀 Quick Start

### Prerequisites
- Ubuntu 20.04+ LTS server (4GB RAM, 20GB disk)
- MariaDB 10.5+, Redis 6.0+, Python 3.8+
- Valid SSL certificate (or use Let's Encrypt)

### Installation (5 steps)

```bash
# 1. Clone repository
git clone https://github.com/frappe/erpnext.git nxlims
cd nxlims

# 2. Install Frappe Bench
pip3 install frappe-bench

# 3. Setup production instance
bench init nxlims_prod --frappe-branch develop
cd nxlims_prod
bench new-site production
bench get-app erpnext https://github.com/frappe/erpnext.git
bench --site production install-app erpnext

# 4. Initialize LIMS
bash ../setup-production.sh production nxlims_production $(pwd)

# 5. Validate setup
bash ../validate-production.sh production $(pwd)
```

### Configure & Deploy

```bash
# Configure SMTP, SMS, WhatsApp in LIMS Settings
# Setup users and test catalog
# Enable backups and monitoring
# Access at: https://yourdomain.com/app/nxlims
```

---

## 📋 Production Requirements Met

| Requirement | Implementation |
|-------------|-----------------|
| Patient & Test Registration | LIMS Patient, Lab Test Registration doctypes |
| Sample Management | Lab Sample doctype with tracking |
| Result Entry & Reporting | Lab Result Entry with PDF generation |
| Quality Control | Lab Quality Control doctype |
| Data Security | Encryption, audit trails, RBAC |
| User Roles & Access | 4 predefined roles with permissions matrix |
| Audit Trail | LIMS Sync Event logging all operations |
| Lab Dashboard | Real-time performance metrics |
| Test Statistics | Detailed test volume and outcome reports |
| Financial Analytics | Revenue, expense, profit analysis |
| 7/14/30 Day Reports | Profit sheets with time windowing |
| Inventory Management | Lab Reagent tracking system |
| Email Notifications | SMTP integration via Frappe |
| SMS Alerts | Twilio/SMS provider integration |
| WhatsApp Integration | Webhook-based WhatsApp Business API |
| Doctor Alerts | Lab Critical Result Alert system [NEW] |
| Offline Operation | Full offline sync API with device sync |
| Windows Installer | Electron-based .exe installer |
| Production Deployment | Comprehensive deployment guide |

---

## 🔧 Key Files & Documentation

### Setup & Deployment
- **NXLIMS_ADMIN_GUIDE.md** - Administrator's quick start
- **NXLIMS_DEPLOYMENT_GUIDE.md** - Complete deployment procedures
- **NXLIMS_PRODUCTION_READINESS.md** - Production baseline checklist
- **setup-production.sh** - Automated setup script
- **validate-production.sh** - Validation & testing suite

### Application Scripts
- **build-windows-installer.sh** - Build Windows .exe installer
- **erpnext/lims/sync.py** - Offline sync endpoints
- **erpnext/lims/notifications.py** - Email/SMS/WhatsApp integration
- **erpnext/patches/v16_0/*.py** - Migration & configuration patches

---

## 🔐 Security Features

- **Encryption**: Field-level encryption for sensitive data
- **Audit Trail**: Complete action logging via LIMS Sync Event
- **RBAC**: Role-based access control with granular permissions
- **SSL/TLS**: HTTPS enforced in production
- **Secure Cookies**: HTTP-only, secure session cookies
- **Data Protection**: GDPR-compliant retention policies
- **Backup & Recovery**: Automated daily backups with 30-day retention

---

## 📊 Reporting Capabilities

### Built-in Reports
1. **LIMS Financial and Profitability Report**
   - 7-day, 14-day, 30-day windows
   - Revenue, expenses, profit analysis
   - Machine, tool, performance expense breakdowns

2. **LIMS Test Statistics Report**
   - Test volume by type
   - Turnaround time metrics
   - Quality indicators

3. **Lab Performance Dashboard**
   - Real-time patient & test counts
   - Revenue metrics
   - Pending test tracking

---

## 🔄 Offline Synchronization

### Architecture
- **Push API**: `push_sync_events()` - Apply offline changes
- **Pull API**: `pull_sync_changes()` - Fetch latest data
- **Idempotency**: Event-based with duplicate detection
- **Device Tracking**: Per-device sync status

### Sync Doctypes
- LIMS Patient
- Lab Test Registration
- Lab Sample
- Lab Result Entry
- Lab Quality Control
- Lab Reagent
- Lab Expense

---

## 👥 User Roles

| Role | Permissions | Use Case |
|------|-----------|----------|
| **LIMS Reception** | Patient CR, Test Register, View Reports | Patient intake, scheduling |
| **LIMS Technician** | Sample Mgmt, Result Entry, QC, Reagent | Lab operations, testing |
| **LIMS Billing** | Expense Mgmt, Financial Reports | Billing, cost tracking |
| **LIMS Manager** | Full access + System Config | Administration, oversight |

---

## 📱 Desktop App (Windows)

The NxLIMS Desktop App allows offline access with automatic sync:

```bash
# Build Windows installer
cd desktop/nxlims-desktop
npm install
npm run dist:win

# Output: dist/NxLIMS-1.0.0-setup.exe
```

**Features:**
- Offline sample collection
- Automatic sync when reconnected
- Device-specific ID tracking
- Configurable server URL
- Automatic reconnection with backoff

---

## 🧪 Testing & Validation

```bash
# Complete validation suite
bash validate-production.sh production /path/to/bench

# Checks:
# - System dependencies
# - Database connectivity
# - LIMS doctypes & roles
# - API endpoints
# - Security configuration
# - Email/SMS setup
# - Data sample availability
```

---

## 📞 Support

### Documentation
- **Admin Guide** - [NXLIMS_ADMIN_GUIDE.md](NXLIMS_ADMIN_GUIDE.md)
- **Deployment** - [NXLIMS_DEPLOYMENT_GUIDE.md](NXLIMS_DEPLOYMENT_GUIDE.md)
- **Production Ready** - [NXLIMS_PRODUCTION_READINESS.md](NXLIMS_PRODUCTION_READINESS.md)

### Troubleshooting
See NXLIMS_DEPLOYMENT_GUIDE.md, Section 12: Troubleshooting

---

## 📜 License

NxLIMS is built on ERPNext/Frappe (GNU General Public License v3)

---

## 🎯 What's Next

1. **Configure SMTP** for email notifications
2. **Setup SMS provider** (Twilio recommended)
3. **Create test catalog** with critical values
4. **Initialize users** for each department
5. **Enable backups** and test restore
6. **Configure monitoring** and alerts
7. **Go-live validation** of all workflows
8. **User training** on LIMS operations

---

## 📝 Changelog

**v1.0.0** - March 20, 2026
- ✅ Complete LIMS module with all 11 requirements
- ✅ Critical Result Alert System (NEW)
- ✅ Enhanced LIMS Settings with SMS/WhatsApp config
- ✅ Electron desktop app with offline sync
- ✅ Windows .exe installer builder
- ✅ Comprehensive production deployment guide
- ✅ Admin quick start guide
- ✅ Validation & testing suite
- ✅ Production setup automation

---

**NxLIMS** - Making laboratory management simple, secured, and scalable.

*Last Updated: March 20, 2026*
