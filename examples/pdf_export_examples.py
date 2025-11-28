"""
PDF Export Service - Integration Examples
Demonstrates how to use PdfExportService in your application
"""
import os
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.pdf_export_service import (
    PdfExportService,
    PurchaseBillNotFoundError,
    DeliveryInvoiceNotFoundError,
    InvalidDateRangeError,
    PdfExportError
)


# Database setup (adjust connection string to your environment)
def get_db_session():
    """Create database session"""
    DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@" \
                   f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()


# Example 1: Export single purchase bill to file
def example_export_purchase_bill_to_file():
    """Export a single purchase bill to PDF file"""
    db = get_db_session()
    try:
        bill_id = 1  # Replace with actual bill ID

        # Export to auto-generated filename in export directory
        file_path = PdfExportService.export_purchase_bill(
            db=db,
            bill_id=bill_id,
            return_bytes=False
        )

        print(f"Purchase bill PDF exported successfully: {file_path}")
        return file_path

    except PurchaseBillNotFoundError as e:
        print(f"Error: {e}")
    except PdfExportError as e:
        print(f"PDF export failed: {e}")
    finally:
        db.close()


# Example 2: Export purchase bill with custom output path
def example_export_purchase_bill_custom_path():
    """Export purchase bill to custom file path"""
    db = get_db_session()
    try:
        bill_id = 1
        custom_path = "/path/to/custom/directory/bill_13001.pdf"

        file_path = PdfExportService.export_purchase_bill(
            db=db,
            bill_id=bill_id,
            output_path=custom_path,
            return_bytes=False
        )

        print(f"Purchase bill PDF saved to: {file_path}")
        return file_path

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


# Example 3: Export purchase bill to bytes (for email/download)
def example_export_purchase_bill_to_bytes():
    """Export purchase bill to bytes for immediate use"""
    db = get_db_session()
    try:
        bill_id = 1

        pdf_bytes = PdfExportService.export_purchase_bill(
            db=db,
            bill_id=bill_id,
            return_bytes=True
        )

        print(f"PDF generated: {len(pdf_bytes)} bytes")

        # Use bytes for various purposes:
        # 1. Send as email attachment
        # 2. Return in API response
        # 3. Store in cloud storage
        # 4. Send to client for download

        return pdf_bytes

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


# Example 4: Export delivery invoice to file
def example_export_delivery_invoice():
    """Export delivery invoice to PDF"""
    db = get_db_session()
    try:
        invoice_id = 1  # Replace with actual invoice ID

        file_path = PdfExportService.export_delivery_invoice(
            db=db,
            invoice_id=invoice_id,
            return_bytes=False
        )

        print(f"Delivery invoice PDF exported: {file_path}")
        return file_path

    except DeliveryInvoiceNotFoundError as e:
        print(f"Invoice not found: {e}")
    except PdfExportError as e:
        print(f"PDF export failed: {e}")
    finally:
        db.close()


# Example 5: Batch export multiple purchase bills
def example_batch_export_multiple_bills():
    """Export multiple purchase bills in single PDF"""
    db = get_db_session()
    try:
        bill_ids = [1, 2, 3, 4, 5]  # Multiple bill IDs

        file_path = PdfExportService.export_multiple_bills_batch(
            db=db,
            bill_ids=bill_ids,
            return_bytes=False
        )

        print(f"Batch PDF with {len(bill_ids)} bills exported: {file_path}")
        return file_path

    except PdfExportError as e:
        print(f"Batch export failed: {e}")
    finally:
        db.close()


# Example 6: Export purchase bills report for date range
def example_export_purchase_report():
    """Export purchase bills report for specific date range"""
    db = get_db_session()
    try:
        # Last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        file_path = PdfExportService.export_date_range_report(
            db=db,
            start_date=start_date,
            end_date=end_date,
            report_type='purchase',
            return_bytes=False
        )

        print(f"Purchase report exported: {file_path}")
        return file_path

    except InvalidDateRangeError as e:
        print(f"Invalid date range: {e}")
    except PdfExportError as e:
        print(f"Report generation failed: {e}")
    finally:
        db.close()


# Example 7: Export delivery invoices report for date range
def example_export_delivery_report():
    """Export delivery invoices report for specific date range"""
    db = get_db_session()
    try:
        # Current month
        today = date.today()
        start_date = date(today.year, today.month, 1)
        end_date = today

        file_path = PdfExportService.export_date_range_report(
            db=db,
            start_date=start_date,
            end_date=end_date,
            report_type='delivery',
            return_bytes=False
        )

        print(f"Delivery report exported: {file_path}")
        return file_path

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


# Example 8: Integration with PyQt5 UI - Export button handler
def example_ui_integration_export_button(bill_id: int):
    """
    Example of integrating PDF export with PyQt5 button click
    This would be called from your UI button click handler
    """
    from PyQt5.QtWidgets import QMessageBox, QFileDialog

    db = get_db_session()
    try:
        # Ask user where to save
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Save Purchase Bill PDF",
            f"purchase_bill_{bill_id}.pdf",
            "PDF Files (*.pdf)"
        )

        if file_path:
            # Export to selected path
            result_path = PdfExportService.export_purchase_bill(
                db=db,
                bill_id=bill_id,
                output_path=file_path,
                return_bytes=False
            )

            QMessageBox.information(
                None,
                "Success",
                f"PDF exported successfully to:\n{result_path}"
            )

    except Exception as e:
        QMessageBox.critical(
            None,
            "Error",
            f"Failed to export PDF:\n{str(e)}"
        )
    finally:
        db.close()


# Example 9: Integration with FastAPI - API endpoint
def example_fastapi_endpoint():
    """
    Example FastAPI endpoint that returns PDF as response
    Add this to your api/main.py
    """
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import Response

    app = FastAPI()

    @app.get("/api/purchase-bills/{bill_id}/pdf")
    def download_purchase_bill_pdf(bill_id: int):
        """Download purchase bill as PDF"""
        db = get_db_session()
        try:
            pdf_bytes = PdfExportService.export_purchase_bill(
                db=db,
                bill_id=bill_id,
                return_bytes=True
            )

            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=purchase_bill_{bill_id}.pdf"
                }
            )

        except PurchaseBillNotFoundError:
            raise HTTPException(status_code=404, detail="Purchase bill not found")
        except PdfExportError as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()

    @app.get("/api/reports/purchase")
    def download_purchase_report(start_date: str, end_date: str):
        """
        Download purchase report for date range

        Query params:
        - start_date: YYYY-MM-DD format
        - end_date: YYYY-MM-DD format
        """
        db = get_db_session()
        try:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()

            pdf_bytes = PdfExportService.export_date_range_report(
                db=db,
                start_date=start,
                end_date=end,
                report_type='purchase',
                return_bytes=True
            )

            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=purchase_report_{start_date}_{end_date}.pdf"
                }
            )

        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        except InvalidDateRangeError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except PdfExportError as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()


# Example 10: Automated daily report generation
def example_automated_daily_report():
    """
    Generate daily report automatically
    This could be scheduled with cron or Windows Task Scheduler
    """
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    db = get_db_session()
    try:
        # Yesterday's report
        yesterday = date.today() - timedelta(days=1)

        logger.info(f"Generating daily report for {yesterday}")

        # Purchase bills report
        purchase_report = PdfExportService.export_date_range_report(
            db=db,
            start_date=yesterday,
            end_date=yesterday,
            report_type='purchase',
            return_bytes=False
        )
        logger.info(f"Purchase report generated: {purchase_report}")

        # Delivery invoices report
        delivery_report = PdfExportService.export_date_range_report(
            db=db,
            start_date=yesterday,
            end_date=yesterday,
            report_type='delivery',
            return_bytes=False
        )
        logger.info(f"Delivery report generated: {delivery_report}")

        # Optional: Send reports via email
        # send_email_with_attachments([purchase_report, delivery_report])

    except Exception as e:
        logger.error(f"Daily report generation failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    """Run examples"""
    print("PDF Export Service - Integration Examples")
    print("=" * 50)

    # Uncomment the examples you want to run:

    # example_export_purchase_bill_to_file()
    # example_export_purchase_bill_to_bytes()
    # example_export_delivery_invoice()
    # example_batch_export_multiple_bills()
    # example_export_purchase_report()
    # example_export_delivery_report()
    # example_automated_daily_report()

    print("\nExamples completed!")
