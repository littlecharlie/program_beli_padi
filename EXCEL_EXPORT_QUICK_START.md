# Excel Export - Quick Start Guide

## Installation

### 1. Install Required Library

```bash
# If using virtual environment (recommended)
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install openpyxl
pip install openpyxl==3.1.2

# Or install all updated dependencies
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python -c "import openpyxl; print(f'openpyxl {openpyxl.__version__} installed successfully')"
```

Expected output:
```
openpyxl 3.1.2 installed successfully
```

## Quick Test

### Run Test Suite

```bash
python test_excel_export.py
```

This will:
- Export sample reports to `~/Documents/test_exports/`
- Test all four export types
- Display results

## User Guide

### Using Excel Export in the Application

1. **Open Reports Screen**
   - Launch the application
   - Navigate to "Reports" section

2. **Generate a Report**
   - Select report type:
     - Purchase Bills
     - Delivery Invoices
     - Farmer Summary
     - Mill Summary
   - Set date range (From/To dates)
   - Optional: Select filter (specific farmer/mill or "All")
   - Click **"Generate Report"** button

3. **Export to Excel**
   - Click **"Export to Excel"** button (green button)
   - Choose save location (default: Documents folder)
   - Modify filename if desired
   - Click **"Save"**
   - Wait for success message
   - Click **"Yes"** to open file immediately, or **"No"** to continue

### Export Features

**All Reports Include:**
- Professional blue headers with white text
- Auto-sized columns
- Proper formatting:
  - Currency: RM 1,234.56
  - Numbers: 1,234.56
  - Dates: DD/MM/YYYY HH:MM
- Summary totals at bottom
- Title section with date range
- Generation timestamp

## Report Types Details

### 1. Purchase Bills Report

**Contains:** All purchase transactions within date range

**Columns:**
- Bill Number, Date, Farmer Name, Farmer IC
- Truck Number, Weights (Gross, Discount, Net)
- Pricing, Payment, Subsidy
- Status, Created By

**Use Cases:**
- Monthly purchase summaries
- Audit trails
- Financial reporting
- Farmer payment verification

### 2. Delivery Invoices Report

**Contains:** All delivery invoices within date range

**Columns:**
- Invoice Number, Date, Rice Mill, Mill Code
- Truck Number, Bills Count, Total Weight
- Created By

**Use Cases:**
- Mill delivery summaries
- Logistics tracking
- Invoice verification
- Weight reconciliation

### 3. Farmer Summary Report

**Contains:** Aggregated statistics per farmer

**Columns:**
- Farmer IC, Name, Phone, Address
- Bills Count, Total Weight
- Total Payment, Average Weight per Bill

**Use Cases:**
- Farmer performance reports
- Payment summaries
- Top farmer analysis
- Annual statements

### 4. Mill Summary Report

**Contains:** Aggregated statistics per rice mill

**Columns:**
- Mill Code, Name, Location, Contact
- Invoices Count, Total Weight
- Average Weight per Invoice

**Use Cases:**
- Mill delivery summaries
- Distribution analysis
- Capacity planning
- Business intelligence

## Tips and Best Practices

### 1. File Naming

Use descriptive filenames:
```
✓ Good: purchase_bills_january_2025.xlsx
✓ Good: farmer_summary_Q1_2025.xlsx
✗ Avoid: export.xlsx
✗ Avoid: report1.xlsx
```

### 2. Date Ranges

For best results:
- Use specific date ranges (not too broad)
- Monthly exports recommended
- Quarterly for summaries
- Annual for year-end reports

### 3. Filters

**Use Filters When:**
- Generating reports for specific farmers
- Analyzing specific mills
- Creating targeted statements
- Troubleshooting specific issues

**Use "All" When:**
- Creating comprehensive reports
- Monthly/quarterly summaries
- Financial consolidation
- Management reports

### 4. Opening Files

**Excel Files Work With:**
- Microsoft Excel 2010 and later
- LibreOffice Calc
- Google Sheets (upload .xlsx file)
- WPS Office
- Numbers (macOS)

## Keyboard Shortcuts

While in Reports Screen:
- **Tab**: Navigate between fields
- **Enter**: Activate selected button
- **Alt+G**: Generate Report (if shortcut enabled)
- **Alt+E**: Export to Excel (if shortcut enabled)

## Troubleshooting

### "Please generate a report first"
**Solution:** Click "Generate Report" before clicking "Export to Excel"

### "Permission denied"
**Solution:**
- Close the file if it's already open in Excel
- Choose a different save location
- Check folder write permissions

### "Export Failed"
**Solution:**
- Verify database connection
- Check date range is valid
- Ensure sufficient disk space
- Review error message for details

### File Won't Open in Excel
**Solution:**
- Ensure .xlsx extension
- Try opening with another program
- Re-export the file
- Check file isn't corrupted (size > 0 bytes)

## Common Workflows

### Monthly Financial Report

```
1. Set date range: 1st to last day of month
2. Select "Purchase Bills"
3. Filter: "All"
4. Generate Report
5. Export to Excel
6. Save as: purchase_bills_<month>_<year>.xlsx
7. Repeat for "Farmer Summary"
8. Combine in financial package
```

### Individual Farmer Statement

```
1. Set date range: Relevant period
2. Select "Farmer Summary"
3. Filter: Select specific farmer
4. Generate Report
5. Export to Excel
6. Save as: farmer_<name>_statement_<period>.xlsx
7. Print or email to farmer
```

### Mill Delivery Analysis

```
1. Set date range: Quarter or month
2. Select "Mill Summary"
3. Filter: "All" (or specific mill)
4. Generate Report
5. Export to Excel
6. Save as: mill_deliveries_<period>.xlsx
7. Share with mill management
```

## Advanced Usage

### Programmatic Export

For automation or batch processing:

```python
from datetime import datetime
from config.database import get_db
from services.excel_export_service import ExcelExportService

db = get_db()

# Export last month's purchase bills
ExcelExportService.export_purchase_bills(
    db=db,
    file_path="/path/to/monthly_report.xlsx",
    from_date=datetime(2025, 11, 1),
    to_date=datetime(2025, 11, 30),
    filter_id=None
)
```

### Batch Export Script

Create a script to export all reports:

```python
# batch_export.py
from datetime import datetime
from config.database import get_db
from services.excel_export_service import ExcelExportService

db = get_db()
period = "202511"  # November 2025
from_date = datetime(2025, 11, 1)
to_date = datetime(2025, 11, 30)

# Export all report types
exports = [
    ("purchase", ExcelExportService.export_purchase_bills),
    ("delivery", ExcelExportService.export_delivery_invoices),
    ("farmer", ExcelExportService.export_farmer_summary),
    ("mill", ExcelExportService.export_mill_summary)
]

for name, func in exports:
    file_path = f"exports/{name}_report_{period}.xlsx"
    func(db, file_path, from_date, to_date)
    print(f"Exported: {file_path}")
```

## Support Resources

- **Full Documentation**: See `EXCEL_EXPORT_IMPLEMENTATION.md`
- **Test Suite**: Run `python test_excel_export.py`
- **Service Code**: `services/excel_export_service.py`
- **UI Code**: `ui/screens/reports.py`

## FAQ

**Q: Can I export to CSV instead?**
A: Currently only Excel (.xlsx) format is supported. CSV export could be added in future versions.

**Q: Can I customize the colors and formatting?**
A: Yes, modify the style constants in `ExcelExportService` class.

**Q: Is there a row limit?**
A: Excel 2010+ supports 1,048,576 rows. The system can handle this, but very large exports will be slower.

**Q: Can I schedule automatic exports?**
A: Not built-in currently. Use the programmatic approach with system scheduler (cron/Task Scheduler).

**Q: Can I export to cloud storage?**
A: Not directly. Export locally first, then upload to cloud storage manually or via script.

**Q: Does this work offline?**
A: Yes, as long as the database is accessible. No internet connection required.

## Updates and Changes

Check the changelog in `EXCEL_EXPORT_IMPLEMENTATION.md` for version history and updates.

---

**Version:** 1.0.0
**Last Updated:** 2025-12-04
**Author:** Claude Code
**Status:** Production Ready
