"""
Unit tests for PDF Export Service
"""
import os
import pytest
from datetime import datetime, date, timedelta
from pathlib import Path
from io import BytesIO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base
from models.purchase_bill import PurchaseBill
from models.delivery_invoice import DeliveryInvoice
from models.farmer import Farmer
from models.rice_mill import RiceMill
from models.truck import Truck
from models.harvest_area import HarvestArea
from services.pdf_export_service import (
    PdfExportService,
    PurchaseBillNotFoundError,
    DeliveryInvoiceNotFoundError,
    InvalidDateRangeError,
    PdfExportError
)


@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_farmer(db_session):
    """Create sample farmer"""
    farmer = Farmer(
        ic_number='123456789012',
        name='Ahmad bin Ali',
        address='Lot 123, Pasir Panjang, Sekinchan',
        phone='0123456789',
        registration_number='REG12345',
        subsidy_code='SUB12345',
        bank_account='1234567890'
    )
    db_session.add(farmer)
    db_session.commit()
    return farmer


@pytest.fixture
def sample_truck(db_session):
    """Create sample truck"""
    truck = Truck(
        truck_number='WXY 1234',
        tare_weight=5000.00
    )
    db_session.add(truck)
    db_session.commit()
    return truck


@pytest.fixture
def sample_harvest_area(db_session):
    """Create sample harvest area"""
    area = HarvestArea(
        # area_name='A01',
        area_name='Pasir Panjang'
    )
    db_session.add(area)
    db_session.commit()
    return area


@pytest.fixture
def sample_rice_mill(db_session):
    """Create sample rice mill"""
    mill = RiceMill(
        mill_code='M001',
        mill_name='Kilang Beras ABC',
        address='Jalan Industri, Kuala Selangor',
        phone='0333445566'
    )
    db_session.add(mill)
    db_session.commit()
    return mill


@pytest.fixture
def sample_purchase_bill(db_session, sample_farmer, sample_truck, sample_harvest_area):
    """Create sample purchase bill"""
    bill = PurchaseBill(
        bill_number='13001',
        farmer_id=sample_farmer.id,
        truck_id=sample_truck.id,
        harvest_area_id=sample_harvest_area.id,
        bill_date=datetime.now(),
        gross_weight=10000.00,
        discount_wap_basah=7.00,
        discount_hampa_padi=7.00,
        discount_padi_muda=6.00,
        total_discount_percent=20.00,
        discount_weight=2000.00,
        net_weight=8000.00,
        rice_price_per_1000kg=1500.00,
        total_payment=12000.00,
        subsidy_estimate=4000.00,
        weighbridge_receipt='WB12345'
    )
    db_session.add(bill)
    db_session.commit()
    return bill


@pytest.fixture
def sample_delivery_invoice(db_session, sample_rice_mill, sample_truck, sample_purchase_bill):
    """Create sample delivery invoice"""
    invoice = DeliveryInvoice(
        invoice_number='01001',
        mill_id=sample_rice_mill.id,
        truck_id=sample_truck.id,
        invoice_date=datetime.now(),
        total_weight=8000.00
    )
    db_session.add(invoice)
    db_session.commit()

    # Link purchase bill to delivery invoice
    sample_purchase_bill.is_delivered = True
    sample_purchase_bill.delivery_invoice_id = invoice.id
    db_session.commit()

    return invoice


class TestPdfExportService:
    """Test cases for PdfExportService"""

    def test_format_currency(self):
        """Test currency formatting"""
        assert PdfExportService._format_currency(1234.56) == "RM 1,234.56"
        assert PdfExportService._format_currency(1000000.00) == "RM 1,000,000.00"
        assert PdfExportService._format_currency(0.50) == "RM 0.50"

    def test_format_weight(self):
        """Test weight formatting"""
        assert PdfExportService._format_weight(1234.56) == "1,234.56 kg"
        assert PdfExportService._format_weight(10000.00) == "10,000.00 kg"

    def test_format_date(self):
        """Test date formatting"""
        test_date = datetime(2025, 11, 26, 15, 30, 0)
        assert PdfExportService._format_date(test_date) == "26/11/2025"

        test_date_only = date(2025, 11, 26)
        assert PdfExportService._format_date(test_date_only) == "26/11/2025"

    def test_get_export_directory(self, tmp_path):
        """Test export directory creation"""
        # Set temporary path
        os.environ['PDF_EXPORT_DIR'] = str(tmp_path / 'test_exports')

        export_dir = PdfExportService._get_export_directory()
        assert export_dir.exists()
        assert export_dir.is_dir()

    def test_export_purchase_bill_to_bytes(self, db_session, sample_purchase_bill):
        """Test exporting purchase bill to bytes"""
        pdf_bytes = PdfExportService.export_purchase_bill(
            db_session,
            sample_purchase_bill.id,
            return_bytes=True
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        # PDF files start with %PDF
        assert pdf_bytes[:4] == b'%PDF'

    def test_export_purchase_bill_to_file(self, db_session, sample_purchase_bill, tmp_path):
        """Test exporting purchase bill to file"""
        os.environ['PDF_EXPORT_DIR'] = str(tmp_path)

        file_path = PdfExportService.export_purchase_bill(
            db_session,
            sample_purchase_bill.id,
            return_bytes=False
        )

        assert os.path.exists(file_path)
        assert file_path.endswith('.pdf')
        assert 'purchase_bill_13001' in file_path

    def test_export_purchase_bill_not_found(self, db_session):
        """Test exporting non-existent purchase bill"""
        with pytest.raises(PurchaseBillNotFoundError):
            PdfExportService.export_purchase_bill(
                db_session,
                99999,
                return_bytes=True
            )

    def test_export_delivery_invoice_to_bytes(self, db_session, sample_delivery_invoice):
        """Test exporting delivery invoice to bytes"""
        pdf_bytes = PdfExportService.export_delivery_invoice(
            db_session,
            sample_delivery_invoice.id,
            return_bytes=True
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF'

    def test_export_delivery_invoice_to_file(self, db_session, sample_delivery_invoice, tmp_path):
        """Test exporting delivery invoice to file"""
        os.environ['PDF_EXPORT_DIR'] = str(tmp_path)

        file_path = PdfExportService.export_delivery_invoice(
            db_session,
            sample_delivery_invoice.id,
            return_bytes=False
        )

        assert os.path.exists(file_path)
        assert file_path.endswith('.pdf')
        assert 'delivery_invoice_01001' in file_path

    def test_export_delivery_invoice_not_found(self, db_session):
        """Test exporting non-existent delivery invoice"""
        with pytest.raises(DeliveryInvoiceNotFoundError):
            PdfExportService.export_delivery_invoice(
                db_session,
                99999,
                return_bytes=True
            )

    def test_export_multiple_bills_batch(self, db_session, sample_purchase_bill, tmp_path):
        """Test batch export of multiple purchase bills"""
        # Create additional bills
        farmer = db_session.query(Farmer).first()
        truck = db_session.query(Truck).first()

        bill2 = PurchaseBill(
            bill_number='13002',
            farmer_id=farmer.id,
            truck_id=truck.id,
            bill_date=datetime.now(),
            gross_weight=5000.00,
            discount_wap_basah=7.00,
            discount_hampa_padi=7.00,
            discount_padi_muda=6.00,
            total_discount_percent=20.00,
            discount_weight=1000.00,
            net_weight=4000.00,
            rice_price_per_1000kg=1500.00,
            total_payment=6000.00,
            subsidy_estimate=2000.00
        )
        db_session.add(bill2)
        db_session.commit()

        os.environ['PDF_EXPORT_DIR'] = str(tmp_path)

        file_path = PdfExportService.export_multiple_bills_batch(
            db_session,
            [sample_purchase_bill.id, bill2.id],
            return_bytes=False
        )

        assert os.path.exists(file_path)
        assert 'purchase_bills_batch' in file_path

    def test_export_multiple_bills_batch_to_bytes(self, db_session, sample_purchase_bill):
        """Test batch export to bytes"""
        pdf_bytes = PdfExportService.export_multiple_bills_batch(
            db_session,
            [sample_purchase_bill.id],
            return_bytes=True
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF'

    def test_export_multiple_bills_empty_list(self, db_session):
        """Test batch export with empty bill list"""
        with pytest.raises(PdfExportError):
            PdfExportService.export_multiple_bills_batch(
                db_session,
                [],
                return_bytes=True
            )

    def test_export_date_range_report_purchase(self, db_session, sample_purchase_bill, tmp_path):
        """Test date range report for purchase bills"""
        os.environ['PDF_EXPORT_DIR'] = str(tmp_path)

        today = date.today()
        start_date = today - timedelta(days=7)
        end_date = today + timedelta(days=1)

        file_path = PdfExportService.export_date_range_report(
            db_session,
            start_date,
            end_date,
            report_type='purchase',
            return_bytes=False
        )

        assert os.path.exists(file_path)
        assert 'purchase_report' in file_path

    def test_export_date_range_report_delivery(self, db_session, sample_delivery_invoice, tmp_path):
        """Test date range report for delivery invoices"""
        os.environ['PDF_EXPORT_DIR'] = str(tmp_path)

        today = date.today()
        start_date = today - timedelta(days=7)
        end_date = today + timedelta(days=1)

        file_path = PdfExportService.export_date_range_report(
            db_session,
            start_date,
            end_date,
            report_type='delivery',
            return_bytes=False
        )

        assert os.path.exists(file_path)
        assert 'delivery_report' in file_path

    def test_export_date_range_invalid_range(self, db_session):
        """Test date range report with invalid date range"""
        start_date = date(2025, 11, 26)
        end_date = date(2025, 11, 20)  # Before start date

        with pytest.raises(InvalidDateRangeError):
            PdfExportService.export_date_range_report(
                db_session,
                start_date,
                end_date,
                report_type='purchase',
                return_bytes=True
            )

    def test_export_date_range_report_to_bytes(self, db_session, sample_purchase_bill):
        """Test date range report to bytes"""
        today = date.today()
        start_date = today - timedelta(days=7)
        end_date = today + timedelta(days=1)

        pdf_bytes = PdfExportService.export_date_range_report(
            db_session,
            start_date,
            end_date,
            report_type='purchase',
            return_bytes=True
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF'
