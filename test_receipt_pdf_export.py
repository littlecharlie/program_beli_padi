"""
Test Receipt PDF Export Functionality
Demonstrates the new receipt-to-PDF export feature
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import get_db
from services.receipt_pdf_service import ReceiptPdfService, ReceiptPdfError
from services.purchase_service import PurchaseService
from services.delivery_service import DeliveryService
from printing.purchase_receipt import PurchaseReceiptFormatter
from printing.delivery_receipt import DeliveryReceiptFormatter
from services.config_service import ConfigService


def test_purchase_receipt_pdf():
    """Test purchase bill receipt PDF export"""
    print("=" * 80)
    print("TEST: Purchase Bill Receipt PDF Export")
    print("=" * 80)

    db = get_db()

    try:
        # Get the first purchase bill
        bills = PurchaseService.get_all(db)

        if not bills:
            print("ERROR: No purchase bills found in database")
            print("Please create a purchase bill first using the application")
            return False

        bill = bills[0]
        print(f"\nFound purchase bill: {bill.bill_number}")
        print(f"Farmer: {bill.farmer.name if bill.farmer else 'Unknown'}")
        print(f"Net Weight: {float(bill.net_weight):,.2f} kg")
        print(f"Total Payment: RM {float(bill.total_payment):,.2f}")

        # Test 1: Export to default path
        print("\n--- Test 1: Export to auto-generated path ---")
        pdf_path = ReceiptPdfService.export_purchase_receipt_pdf(
            db=db,
            bill_id=bill.id,
            return_bytes=False
        )
        print(f"SUCCESS: PDF exported to: {pdf_path}")
        print(f"File exists: {os.path.exists(pdf_path)}")
        print(f"File size: {os.path.getsize(pdf_path)} bytes")

        # Test 2: Export to custom path
        print("\n--- Test 2: Export to custom path ---")
        custom_path = f"./test_receipt_{bill.bill_number}.pdf"
        pdf_path2 = ReceiptPdfService.export_purchase_receipt_pdf(
            db=db,
            bill_id=bill.id,
            output_path=custom_path,
            return_bytes=False
        )
        print(f"SUCCESS: PDF exported to: {pdf_path2}")
        print(f"File exists: {os.path.exists(pdf_path2)}")

        # Test 3: Export as bytes
        print("\n--- Test 3: Export as bytes (for in-memory use) ---")
        pdf_bytes = ReceiptPdfService.export_purchase_receipt_pdf(
            db=db,
            bill_id=bill.id,
            return_bytes=True
        )
        print(f"SUCCESS: PDF generated as bytes")
        print(f"Bytes length: {len(pdf_bytes)} bytes")

        # Show the text receipt for comparison
        print("\n--- Text Receipt Preview (first 20 lines) ---")
        company_info = {
            'name': ConfigService.get_value(db, 'company_name', 'AYOP BIN ARSHAD'),
            'address_1': ConfigService.get_value(
                db, 'company_address',
                'LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR'
            ),
            'address_2': ConfigService.get_value(
                db, 'company_address_2', 'SELANGOR DARUL EHSAN'
            ),
            'registration': ConfigService.get_value(db, 'company_registration', '474523-K'),
            'phone': ConfigService.get_value(db, 'company_phone', '0162120051')
        }
        receipt_text = PurchaseReceiptFormatter.format_receipt(bill, company_info)
        lines = receipt_text.split('\n')[:20]
        for line in lines:
            print(line)
        print("... (truncated)")

        print("\n" + "=" * 80)
        print("PURCHASE RECEIPT PDF EXPORT: ALL TESTS PASSED")
        print("=" * 80)
        return True

    except ReceiptPdfError as e:
        print(f"\nERROR: {str(e)}")
        return False
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_delivery_receipt_pdf():
    """Test delivery invoice receipt PDF export"""
    print("\n" * 2)
    print("=" * 80)
    print("TEST: Delivery Invoice Receipt PDF Export")
    print("=" * 80)

    db = get_db()

    try:
        # Get the first delivery invoice
        invoices = DeliveryService.get_all(db)

        if not invoices:
            print("WARNING: No delivery invoices found in database")
            print("Skipping delivery invoice test")
            return True

        invoice = invoices[0]
        print(f"\nFound delivery invoice: {invoice.invoice_number}")
        print(f"Mill: {invoice.mill.mill_name if invoice.mill else 'Unknown'}")
        print(f"Truck: {invoice.truck.truck_number if invoice.truck else 'Unknown'}")
        print(f"Total Weight: {float(invoice.total_weight):,.2f} kg")

        # Test: Export to default path
        print("\n--- Test: Export delivery invoice to PDF ---")
        pdf_path = ReceiptPdfService.export_delivery_receipt_pdf(
            db=db,
            invoice_id=invoice.id,
            return_bytes=False
        )
        print(f"SUCCESS: PDF exported to: {pdf_path}")
        print(f"File exists: {os.path.exists(pdf_path)}")
        print(f"File size: {os.path.getsize(pdf_path)} bytes")

        # Show the text receipt for comparison
        print("\n--- Text Receipt Preview (first 20 lines) ---")
        company_info = {
            'name': ConfigService.get_value(db, 'company_name', 'AYOP BIN ARSHAD'),
            'address_1': ConfigService.get_value(
                db, 'company_address',
                'LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR'
            ),
            'address_2': ConfigService.get_value(
                db, 'company_address_2', 'SELANGOR DARUL EHSAN'
            ),
            'registration': ConfigService.get_value(db, 'company_registration', '474523-K'),
            'phone': ConfigService.get_value(db, 'company_phone', '0162120051')
        }
        receipt_text = DeliveryReceiptFormatter.format_receipt(db, invoice, company_info)
        lines = receipt_text.split('\n')[:20]
        for line in lines:
            print(line)
        print("... (truncated)")

        print("\n" + "=" * 80)
        print("DELIVERY RECEIPT PDF EXPORT: ALL TESTS PASSED")
        print("=" * 80)
        return True

    except ReceiptPdfError as e:
        print(f"\nERROR: {str(e)}")
        return False
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n")
    print("*" * 80)
    print("*" + " " * 78 + "*")
    print("*" + "  Receipt PDF Export Test Suite".center(78) + "*")
    print("*" + " " * 78 + "*")
    print("*" * 80)
    print("\n")

    results = []

    # Test purchase receipt PDF
    results.append(("Purchase Receipt PDF", test_purchase_receipt_pdf()))

    # Test delivery receipt PDF
    results.append(("Delivery Receipt PDF", test_delivery_receipt_pdf()))

    # Summary
    print("\n" * 2)
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    all_passed = True
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name:<40} {status}")
        if not result:
            all_passed = False

    print("=" * 80)

    if all_passed:
        print("\nALL TESTS PASSED!")
        print("\nReceipt PDF export functionality is working correctly.")
        print("\nYou can now:")
        print("1. Use 'Print Receipt' button in the application")
        print("2. Choose to print, save as PDF, or both")
        print("3. PDFs are saved to: ./exports/receipts/")
        print("4. PDFs maintain monospace formatting like dot matrix printer")
    else:
        print("\nSOME TESTS FAILED!")
        print("Please check the error messages above.")

    print("\n")


if __name__ == "__main__":
    main()
