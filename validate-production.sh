#!/bin/bash
# NxLIMS Production Validation & Testing Script
# Validates that all systems are ready for production

set -e

echo "=================================================="
echo "NxLIMS Production Validation Suite"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0

# Helper functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Validate configuration
SITE_NAME=${1:-"production"}
BENCH_DIR=${2:-"/home/nxlims/nxlims_prod"}

if [ ! -d "$BENCH_DIR" ]; then
    fail "Bench directory not found: $BENCH_DIR"
    exit 1
fi

cd "$BENCH_DIR"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Site: $SITE_NAME"
echo "  Bench: $BENCH_DIR"
echo ""

# ============================================
# SYSTEM CHECKS
# ============================================
echo -e "${YELLOW}System Checks:${NC}"

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    if [[ "$PYTHON_VERSION" > "3.8" ]]; then
        pass "Python 3.8+ installed ($PYTHON_VERSION)"
    else
        warn "Python version is $PYTHON_VERSION, 3.8+ recommended"
    fi
else
    fail "Python 3 not found"
fi

# Check Node.js
if command -v node &> /dev/null; then
    pass "Node.js installed ($(node --version))"
else
    warn "Node.js not found (required for desktop app)"
fi

# Check MySQL/MariaDB connection
if command -v mysql &> /dev/null; then
    if mysql -u root -e "SELECT 1" > /dev/null 2>&1; then
        pass "MySQL/MariaDB connection OK"
    else
        warn "MySQL accessible but check credentials"
    fi
else
    fail "MySQL/MariaDB not found"
fi

# Check Redis
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        pass "Redis is running"
    else
        warn "Redis not running"
    fi
else
    warn "Redis not found"
fi

echo ""

# ============================================
# DATABASE CHECKS
# ============================================
echo -e "${YELLOW}Database Checks:${NC}"

bench --site "$SITE_NAME" shell << 'PYEOF'
import frappe

# Check database connection
try:
    result = frappe.db.sql("SELECT 1")
    print("✓ Database connection OK")
except Exception as e:
    print(f"✗ Database connection failed: {e}")
    exit(1)

# Check LIMS doctypes exist
lims_doctypes = [
    "LIMS Patient",
    "Lab Test Registration",
    "Lab Sample",
    "Lab Result Entry",
    "Lab Quality Control",
    "Lab Reagent",
    "Lab Expense",
    "LIMS Sync Event",
    "LIMS Settings",
    "Lab Test Catalog",
    "Lab Critical Result Alert"
]

missing_doctypes = []
for doctype in lims_doctypes:
    if not frappe.db.exists("DocType", doctype):
        missing_doctypes.append(doctype)
    else:
        print(f"✓ DocType exists: {doctype}")

if missing_doctypes:
    print(f"✗ Missing DocTypes: {', '.join(missing_doctypes)}")

# Check LIMS roles exist
lims_roles = ["LIMS Manager", "LIMS Reception", "LIMS Technician", "LIMS Billing"]
for role in lims_roles:
    if frappe.db.exists("Role", role):
        print(f"✓ Role exists: {role}")
    else:
        print(f"✗ Role missing: {role}")

# Verify offshore sync is enabled
try:
    settings = frappe.get_single("LIMS Settings")
    if settings.enable_offline_sync:
        print("✓ Offline sync enabled")
    else:
        print("⚠ Offline sync is disabled")
except Exception as e:
    print(f"⚠ Could not verify offline sync: {e}")

print("Database checks complete")
PYEOF

echo ""

# ============================================
# API CHECKS
# ============================================
echo -e "${YELLOW}API & Endpoint Checks:${NC}"

bench --site "$SITE_NAME" shell << 'PYEOF'
import frappe
from erpnext.lims.sync import ALLOWED_SYNC_DOCTYPES

# Check sync API is available
try:
    from erpnext.lims.sync import push_sync_events, pull_sync_changes
    print("✓ Sync APIs available (push_sync_events, pull_sync_changes)")
except ImportError:
    print("✗ Sync APIs not found")

# Check notification module
try:
    from erpnext.lims.notifications import send_whatsapp_via_webhook, send_sms_via_provider
    print("✓ Notification module loaded")
except ImportError:
    print("⚠ Some notification methods not available")

# Check critical alert system
try:
    from erpnext.lims.doctype.lab_critical_result_alert.lab_critical_result_alert import check_and_create_critical_alerts_for_result
    print("✓ Critical result alert system available")
except Exception as e:
    print(f"✗ Critical alert system error: {e}")

# List allowed sync doctypes
print(f"✓ Allowed sync doctypes ({len(ALLOWED_SYNC_DOCTYPES)}):")
for doctype in ALLOWED_SYNC_DOCTYPES:
    print(f"  - {doctype}")

print("API checks complete")
PYEOF

echo ""

# ============================================
# CONFIGURATION CHECKS
# ============================================
echo -e "${YELLOW}Configuration Checks:${NC}"

bench --site "$SITE_NAME" shell << 'PYEOF'
import frappe

settings = frappe.get_single("LIMS Settings")

print("LIMS Settings:")
print(f"  Enable SMS: {'✓' if settings.enable_sms else '✗'}")
print(f"  SMS Provider: {settings.sms_provider or 'Not configured'}")
print(f"  Enable WhatsApp: {'✓' if settings.enable_whatsapp else '✗'}")
print(f"  Enable Offline Sync: {'✓' if settings.enable_offline_sync else '✗'}")
print(f"  Sync Batch Limit: {settings.sync_batch_limit}")

# Check email setup
email_account = frappe.db.sql("""
    SELECT name, email_id, smtp_server FROM `tabEmail Account` 
    WHERE enabled = 1 LIMIT 1
""", as_dict=True)

if email_account:
    print(f"\nEmail Configuration:")
    print(f"  Account: {email_account[0]['email_id']}")
    print(f"  Server: {email_account[0]['smtp_server']}")
    print(f"  Status: ✓ Configured")
else:
    print(f"\n⚠ Email Configuration: Not configured")

print("\nConfiguration checks complete")
PYEOF

echo ""

# ============================================
# SECURITY CHECKS
# ============================================
echo -e "${YELLOW}Security Checks:${NC}"

bench --site "$SITE_NAME" shell << 'PYEOF'
import frappe
import json

print("Security Audit:")

# Check if SSL is enabled
site_config = frappe.get_site_config()
if site_config.get("ssl_certificate"):
    print("  ✓ SSL certificate configured")
else:
    print("  ⚠ SSL not configured (development mode)")

# Check session security
if site_config.get("session_cookie_secure"):
    print("  ✓ Secure session cookies enabled")
else:
    print("  ⚠ Secure session cookies not enabled")

# Check if developer mode is disabled
if site_config.get("developer_mode"):
    print("  ⚠ Developer mode is ENABLED (should be disabled in production)")
else:
    print("  ✓ Developer mode is disabled")

# Check encryption key
if site_config.get("encryption_key"):
    print("  ✓ Encryption key configured")
else:
    print("  ✗ Encryption key NOT configured")

# Check active users
admin_users = frappe.db.sql(
    "SELECT COUNT(*) as count FROM `tabUser` WHERE user_type='System User' AND enabled=1",
    as_dict=True
)
print(f"  Active users: {admin_users[0]['count']}")

print("\nSecurity checks complete")
PYEOF

echo ""

# ============================================
# DATA SAMPLE CHECKS
# ============================================
echo -e "${YELLOW}Data Sample Checks:${NC}"

bench --site "$SITE_NAME" shell << 'PYEOF'
import frappe

print("Sample Data Verification:")

# Check if we have sample data or need to create it
patient_count = frappe.db.count("LIMS Patient")
test_reg_count = frappe.db.count("Lab Test Registration")
test_cat_count = frappe.db.count("Lab Test Catalog")

print(f"  LIMS Patients: {patient_count}")
print(f"  Test Registrations: {test_reg_count}")
print(f"  Test Catalog: {test_cat_count}")

if test_cat_count == 0:
    print("\n⚠ No test catalog items - need to create sample tests")
else:
    print("\n✓ Sample data exists")

print("\nData checks complete")
PYEOF

echo ""

# ============================================
# SUMMARY
# ============================================
echo "=================================================="
echo "Validation Summary"
echo "=================================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}⚠ VALIDATION FAILED - Fix errors before production deployment${NC}"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}✓ VALIDATION PASSED (with warnings) - Review warnings before deployment${NC}"
else
    echo -e "${GREEN}✓ VALIDATION PASSED - System ready for production${NC}"
fi

echo ""
echo "Next steps:"
echo "  1. Review any warnings above"
echo "  2. Run configure-production.sh to finalize setup"
echo "  3. Test user login flows"
echo "  4. Enable backups"
echo "  5. Set up monitoring"
echo ""
