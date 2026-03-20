# NxLIMS End-to-End Testing Scenarios

Complete test scenarios to validate NxLIMS functionality before production go-live.

---

## 1. Patient Registration Flow

### Test 1.1: Create Patient

**Steps:**
1. Login as LIMS Reception
2. Go to LIMS → Patient → Create
3. Fill:
   - Patient Name: "John Doe"
   - Mobile: "+91-9876543210"
   - Gender: Male
   - Referred Doctor: "Dr. Smith"
   - Doctor Contact: "doctor@clinic.com"
4. Save

**Expected Result:** ✓ Patient created with ID "LIM-PAT-2026-001"

### Test 1.2: Search Patient

**Steps:**
1. Go to LIMS → Patient list
2. Search "John Doe"
3. Verify all fields populated

**Expected Result:** ✓ Patient found and details displayed

---

## 2. Test Registration Workflow

### Test 2.1: Register Tests

**Steps:**
1. Login as LIMS Reception
2. Go to LIMS → Test Registration → Create
3. Select Patient: "John Doe"
4. Add Test Items:
   - Test Name: "Hemoglobin"
   - Collection Time: [Now]
5. Select Billing Option
6. Submit

**Expected Result:** ✓ Test registration created, status = "Registered"

### Test 2.2: Critical Value Configuration

**Steps:**
1. Go to LIMS → Lab Test Catalog
2. Edit "Hemoglobin" test
3. Set Critical Low: 7.0, Critical High: 20.0
4. Save

**Expected Result:** ✓ Critical values saved

---

## 3. Sample Management

### Test 3.1: Create Lab Sample

**Steps:**
1. Login as LIMS Technician
2. Go to LIMS → Lab Sample → Create
3. Link to Test Registration: "[Test ID]"
4. Set Collection Method: "Venipuncture"
5. Submit

**Expected Result:** ✓ Sample created and linked to test

### Test 3.2: Sample Tracking

**Steps:**
1. View Lab Sample
2. Verify:
   - Patient information populated
   - Test details visible
   - Status = "Collected"

**Expected Result:** ✓ All information correctly linked

---

## 4. Result Entry & Critical Alerts

### Test 4.1: Enter Normal Result

**Steps:**
1. Go to LIMS → Lab Result Entry → Create
2. Link to Test Registration
3. Enter Test Result: "14.5 g/dL" (normal for Hemoglobin)
4. Save and Submit

**Expected Result:** ✓ Result accepted, no alert triggered

### Test 4.2: Enter Critical Result

**Steps:**
1. Create another Test Registration
2. Enter Result Entry: "6.5 g/dL" (below critical low of 7.0)
3. Submit

**Expected Result:**
✓ System detects critical value
✓ Lab Critical Result Alert created automatically
✓ Alert status = "Pending"

### Test 4.3: Critical Alert Notification

**Steps:**
1. View Lab Critical Result Alert
2. Verify fields populated:
   - Patient name, ID
   - Test name, result value
   - Critical range
   - Doctor contact info
3. Click "Send Alert"

**Expected Result:**
✓ Alert notification sent
✓ Status changes to "Sent"
✓ Email status shows "Sent"
✓ SMS/WhatsApp status shows appropriate status

---

## 5. Data Security & Access Control

### Test 5.1: Role-Based Access

**Users to Test:**
1. **LIMS Reception** - Login to `reception@nxlims.local`
   - Can create Patient ✓
   - Can create Test Registration ✓
   - Cannot edit Expense ✗
   - Cannot view Financial Reports ✗

2. **LIMS Technician** - Login to `technician@nxlims.local`
   - Cannot create Patient ✗
   - Can create Lab Sample ✓
   - Can submit Result Entry ✓
   - Cannot view Settings ✗

3. **LIMS Billing** - Login to `billing@nxlims.local`
   - Cannot create Patient ✗
   - Cannot edit Lab Sample ✗
   - Can view Financial Reports ✓
   - Can create Expenses ✓

4. **LIMS Manager** - Login to `manager@nxlims.local`
   - Full access to all functions ✓

### Test 5.2: Audit Trail

**Steps:**
1. Create/Edit a Patient record
2. Go to "LIMS → LIMS Sync Event"
3. Search for event_id of operation
4. Verify:
   - Event recorded
   - Device ID tracked
   - Operation type shown
   - Timestamp accurate
   - User info logged

**Expected Result:** ✓ Complete audit trail entry created

### Test 5.3: Data Encryption

**Steps:**
1. Database shell: `mysql nxlims_production`
2. Query: `SELECT patient_identifier FROM lims_patient WHERE name='LIM-PAT-2026-001'`
3. Verify field is encrypted (not plain text)

**Expected Result:** ✓ Identifier hashed/encrypted

---

## 6. Offline Synchronization

### Test 6.1: Offline Data Creation

**Steps:**
1. Close internet connection (or simulate via Electron app setting)
2. Create new Patient record
3. Register test
4. Collect sample
5. Enter result with critical value

**Expected Result:**
✓ All operations work offline
✓ Data stored locally
✓ UI indicates offline status

### Test 6.2: Sync on Reconnect

**Steps:**
1. Restore internet connection
2. Wait for automatic sync (20s default)
3. Verify all created records appear on server:
   ```bash
   bench --site production shell
   import frappe
   count = frappe.db.count("LIMS Patient", filters={"modified": [">", "NOW()"]})
   print(f"New patients synced: {count}")
   ```

**Expected Result:** ✓ All offline data synchronized

### Test 6.3: Conflict Handling

**Steps:**
1. Create patient offline with unique ID
2. Go online and verify sync
3. Attempt creating duplicate (system should handle gracefully)

**Expected Result:** ✓ Proper conflict resolution

---

## 7. Reporting & Analytics

### Test 7.1: Lab Performance Dashboard

**Steps:**
1. Go to LIMS → Dashboard
2. Verify visible metrics:
   - Total Patients: > 0
   - Total Tests Completed: > 0
   - Pending Tests: >= 0
   - Today's Revenue: [Amount]

**Expected Result:** ✓ All metrics calculated correctly

### Test 7.2: Financial Report

**Steps:**
1. Create 5+ test registrations with amounts
2. Create 2+ lab expenses
3. Go to LIMS → Report → LIMS Financial and Profitability
4. View 7-day, 14-day, 30-day results
5. Verify columns:
   - Period
   - Revenue (sum of test amounts)
   - General Expense
   - Lab Performance Expense
   - Machinery & Tool Expense
   - Total Expense
   - Profit (Revenue - Expenses)

**Expected Result:** ✓ Report calculates correctly, profit = revenue - expenses

### Test 7.3: Test Statistics Report

**Steps:**
1. Submit multiple test registrations
2. Go to LIMS → Report → LIMS Test Statistics
3. Verify:
   - Test volume by type
   - Completion rates
   - Quality metrics

**Expected Result:** ✓ Statistics accurately reflect test data

---

## 8. Notifications (Email/SMS/WhatsApp)

### Test 8.1: Email Configuration

**Steps:**
1. Go to Setup → Email Account
2. Verify configured with:
   - SMTP Server: [configured]
   - Port: 587 (TLS)
   - Sender: noreply@yourdomain.com
3. Click "Send Test Email" ✓

**Expected Result:** ✓ Test email received successfully

### Test 8.2: SMS Configuration

**Steps:**
1. Go to LIMS → LIMS Settings
2. Set:
   - Enable SMS: ✓
   - SMS Provider: Twilio
   - Account SID: [Your Twilio SID]
   - Auth Token: [Your Twilio token]
   - From Number: [Your Twilio number]
3. Save

**Expected Result:** ✓ Configuration saved

### Test 8.3: Test Critical Alert via SMS

**Steps:**
1. Create test registration
2. Enter critical result
3. Verify Lab Critical Result Alert created
4. Click "Send Alert"
5. Referred doctor should receive SMS

**Expected Result:**
✓ SMS Received by doctor
✓ Contains patient name, test, result
✓ "CRITICAL" keyword present

### Test 8.4: WhatsApp Integration

**Steps:**
1. Go to LIMS → LIMS Settings
2. Set:
   - Enable WhatsApp: ✓
   - Webhook URL: [Your webhook]
3. Trigger critical alert
4. Doctor receives WhatsApp message

**Expected Result:** ✓ WhatsApp message delivered

---

## 9. Windows Desktop App

### Test 9.1: Build Installer

**Steps:**
```bash
cd desktop/nxlims-desktop
npm install
npm run dist:win
```

**Expected Result:**
✓ Build completes without errors
✓ Output file: `dist/NxLIMS-1.0.0-setup.exe`
✓ File size: ~150MB+

### Test 9.2: Install on Windows

**Steps:**
1. Run installer with Administrator privileges
2. Follow wizard
3. Accept default installation directory
4. Complete installation
5. Desktop shortcut created ✓

**Expected Result:** ✓ Application installed successfully

### Test 9.3: Launch & Configure

**Steps:**
1. Launch NxLIMS desktop app
2. Opens to offline page
3. Use menu: NxLIMS → Settings
4. Configure Base URL: `https://yourdomain.com`
5. Restart app
6. Verify connection successful

**Expected Result:** ✓ App connects to server

### Test 9.4: Offline Data Sync

**Steps:**
1. Disable network
2. Create patient, register test offline
3. Re-enable network
4. Verify sync occurs automatically
5. Check device_id is tracked

**Expected Result:** ✓ Offline data synced successfully

---

## 10. Quality Control Management

### Test 10.1: Create QC Check

**Steps:**
1. Go to LIMS → Lab Quality Control → Create
2. Set:
   - Test Name: "Hemoglobin"
   - Expected Value: "14.0"
   - Tolerance Range: ±0.5
3. Submit

**Expected Result:** ✓ QC check created

### Test 10.2: Verify QC Status

**Steps:**
1. View QC record
2. Check status field
3. Verify linked to test

**Expected Result:** ✓ QC data properly recorded

---

## 11. Inventory & Reagent Management

### Test 11.1: Add Reagent

**Steps:**
1. Go to LIMS → Lab Reagent → Create
2. Set:
   - Reagent Name: "Hemoglobin Test Reagent"
   - Quantity: 100
   - Unit: "mL"
   - Expiry Date: [Future date]
3. Save

**Expected Result:** ✓ Reagent added to inventory

### Test 11.2: Track Reagent Usage

**Steps:**
1. View reagent record
2. Verify quantity updating
3. Check expiry alert (if near date)

**Expected Result:** ✓ Inventory tracked accurately

---

## 12. Financial & Operational Analytics

### Test 12.1: Expense Tracking

**Steps:**
1. Go to LIMS → Lab Expense → Create
2. Set:
   - Expense Type: "General Expense"
   - Amount: 5000
   - Date: [Today]
3. Submit

**Expected Result:** ✓ Expense recorded

### Test 12.2: Profit Calculation

**Steps:**
1. Create multiple tests & register amounts
2. Create multiple expenses
3. Run Financial Report
4. Verify: Profit = Total Revenue - Total Expenses

**Expected Result:** ✓ Profit calculation accurate

---

## 13. Doctor Alert Workflow

### Test 13.1: Referred Doctor Alert

**Steps:**
1. Create patient with referred doctor info
2. Register test with critical range
3. Enter result exceeding critical value
4. System auto-creates alert
5. Alert automatically sends to doctor
   - Email ✓
   - SMS ✓
   - WhatsApp ✓

**Expected Result:** ✓ Doctor receives all configured notifications

---

## Performance Benchmarks

| Operation | Target | Actual |
|-----------|--------|--------|
| Patient creation | <1s | - |
| Test registration | <2s | - |
| Report generation | <5s | - |
| Offline sync (100 items) | <10s | - |
| Database query | <100ms | - |
| Page load | <2s | - |

---

## Signoff Checklist

- [ ] All 13 test scenarios passed
- [ ] No data loss in offline sync
- [ ] All notifications delivered
- [ ] User access control working
- [ ] Audit trail complete
- [ ] Reports accurate
- [ ] Desktop app functional
- [ ] Performance acceptable
- [ ] Security validated
- [ ] Backup/restore tested

**Approved for Production**: _______________  Date: _______

---

*Last Updated: March 20, 2026*
