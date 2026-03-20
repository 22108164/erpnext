#!/bin/bash
# NxLIMS Production Setup Script
# Initializes and configures NxLIMS for production deployment

set -e

echo "=================================================="
echo "NxLIMS Production Setup Script"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SITE_NAME=${1:-"production"}
DB_NAME=${2:-"nxlims_production"}
BENCH_DIR=${3:-"/home/nxlims/nxlims_prod"}

# Validate inputs
if [ -z "$SITE_NAME" ] || [ -z "$DB_NAME" ] || [ -z "$BENCH_DIR" ]; then
    echo -e "${RED}Usage: ./setup-production.sh SITE_NAME DB_NAME BENCH_DIR${NC}"
    exit 1
fi

# Check if bench directory exists
if [ ! -d "$BENCH_DIR" ]; then
    echo -e "${RED}Error: Bench directory not found: $BENCH_DIR${NC}"
    exit 1
fi

cd "$BENCH_DIR"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Site Name: $SITE_NAME"
echo "  Database: $DB_NAME"
echo "  Bench Directory: $BENCH_DIR"
echo ""

# Step 1: Run migration patches
echo -e "${YELLOW}[1] Running migration patches...${NC}"

# Setup LIMS roles and permissions
echo "  - Setting up LIMS roles and permissions..."
bench --site "$SITE_NAME" execute erpnext.patches.v16_0.setup_nxlims_roles

# Configure LIMS-only workspace
echo "  - Configuring LIMS-only workspace..."
bench --site "$SITE_NAME" execute erpnext.patches.v16_0.configure_lims_only_workspace

echo -e "${GREEN}✓ Migration patches completed${NC}"
echo ""

# Step 2: Configure LIMS Settings
echo -e "${YELLOW}[2] Initializing LIMS Settings...${NC}"

bench --site "$SITE_NAME" shell << 'EOF'
import frappe

settings = frappe.get_single('LIMS Settings')
settings.enable_offline_sync = 1
settings.sync_batch_limit = 200
settings.enable_sms = 1
settings.enable_whatsapp = 0
settings.save()

print("✓ LIMS Settings initialized")
EOF

echo -e "${GREEN}✓ LIMS Settings configured${NC}"
echo ""

# Step 3: Create default users
echo -e "${YELLOW}[3] Creating default LIMS users...${NC}"

bench --site "$SITE_NAME" shell << 'EOF'
import frappe
from frappe.utils import random_string

def create_user(email, first_name, last_name, role):
    if frappe.db.exists("User", email):
        print(f"  ℹ User already exists: {email}")
        return False
    
    user = frappe.get_doc({
        'doctype': 'User',
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'send_welcome_email': False,
        'roles': [{'role': role}]
    })
    user.insert(ignore_permissions=True)
    print(f"  ✓ Created user: {email} ({role})")
    return True

# Create LIMS roles
create_user('reception@nxlims.local', 'Reception', 'Desk', 'LIMS Reception')
create_user('technician@nxlims.local', 'Lab', 'Technician', 'LIMS Technician')
create_user('billing@nxlims.local', 'Billing', 'Officer', 'LIMS Billing')
create_user('manager@nxlims.local', 'Lab', 'Manager', 'LIMS Manager')

print("✓ Default users created")
EOF

echo -e "${GREEN}✓ Default users created${NC}"
echo ""

# Step 4: Create sample company if not exists
echo -e "${YELLOW}[4] Initializing default company...${NC}"

bench --site "$SITE_NAME" shell << 'EOF'
import frappe

if not frappe.db.exists("Company", "NxLIMS Lab"):
    company = frappe.get_doc({
        'doctype': 'Company',
        'company_name': 'NxLIMS Lab',
        'country': 'India',
        'domain': 'Medical',
    })
    company.insert(ignore_permissions=True)
    print("✓ Company created: NxLIMS Lab")
else:
    print("ℹ Company already exists: NxLIMS Lab")
EOF

echo -e "${GREEN}✓ Company initialized${NC}"
echo ""

# Step 5: Set up cron jobs
echo -e "${YELLOW}[5] Enabling scheduled jobs...${NC}"

bench --site "$SITE_NAME" shell << 'EOF'
import frappe

# Enable scheduler
scheduler = frappe.get_doc("Scheduled Job Type", "Scheduler Active")
scheduler.disabled = 0
scheduler.save()

print("✓ Scheduler jobs enabled")
EOF

echo -e "${GREEN}✓ Scheduled jobs enabled${NC}"
echo ""

# Step 6: Perform cleanup and optimization
echo -e "${YELLOW}[6] Performing database cleanup...${NC}"

bench --site "$SITE_NAME" execute frappe.utils.global_search.rebuild_for_doctype

echo -e "${GREEN}✓ Database optimized${NC}"
echo ""

# Step 7: Generate documentation
echo -e "${YELLOW}[7] Building documentation...${NC}"

bench build --site "$SITE_NAME" > /dev/null 2>&1

echo -e "${GREEN}✓ Documentation built${NC}"
echo ""

# Summary
echo "=================================================="
echo -e "${GREEN}✓ NxLIMS Production Setup Complete!${NC}"
echo "=================================================="
echo ""
echo "Default Users Created:"
echo "  - reception@nxlims.local (LIMS Reception)"
echo "  - technician@nxlims.local (LIMS Technician)"
echo "  - billing@nxlims.local (LIMS Billing)"
echo "  - manager@nxlims.local (LIMS Manager)"
echo ""
echo "Next steps:"
echo "  1. Change default user passwords"
echo "  2. Configure SMTP for email notifications"
echo "  3. Configure SMS provider (Twilio, etc.)"
echo "  4. Set up SSL certificates"
echo "  5. Configure firewall rules"
echo "  6. Run system backups"
echo ""
echo "Access your NxLIMS installation at:"
echo "  https://yourdomain.com/app/nxlims"
echo ""
echo "Documentation:"
echo "  - Production Readiness: $BENCH_DIR/../NXLIMS_PRODUCTION_READINESS.md"
echo "  - Deployment Guide: $BENCH_DIR/../NXLIMS_DEPLOYMENT_GUIDE.md"
echo ""
