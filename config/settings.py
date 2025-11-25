"""
Application Settings
Loads configuration from environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseConfig:
    """Database configuration"""
    HOST = os.getenv('DB_HOST', 'localhost')
    PORT = os.getenv('DB_PORT', '5432')
    NAME = os.getenv('DB_NAME', 'rice_billing_db')
    USER = os.getenv('DB_USER', 'postgres')
    PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

    @classmethod
    def get_connection_string(cls):
        """Generate PostgreSQL connection string"""
        return f"postgresql://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.NAME}"


class AppConfig:
    """Application configuration"""
    NAME = os.getenv('APP_NAME', 'Rice Billing System')
    VERSION = os.getenv('APP_VERSION', '1.0.0')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'


class PrinterConfig:
    """Printer configuration"""
    NAME = os.getenv('PRINTER_NAME', 'EPSON LQ-310')
    INTERFACE = os.getenv('PRINTER_INTERFACE', 'usb')


class BusinessConfig:
    """Business configuration"""
    DEFAULT_RICE_PRICE = float(os.getenv('DEFAULT_RICE_PRICE', '1500.00'))
    DEFAULT_SUBSIDY_RATE = float(os.getenv('DEFAULT_SUBSIDY_RATE', '0.50'))
    DEFAULT_DISCOUNT_WAP_BASAH = float(os.getenv('DEFAULT_DISCOUNT_WAP_BASAH', '7.00'))
    DEFAULT_DISCOUNT_HAMPA_PADI = float(os.getenv('DEFAULT_DISCOUNT_HAMPA_PADI', '7.00'))
    DEFAULT_DISCOUNT_PADI_MUDA = float(os.getenv('DEFAULT_DISCOUNT_PADI_MUDA', '6.00'))


class CompanyConfig:
    """Company information"""
    NAME = os.getenv('COMPANY_NAME', 'AYOP BIN ARSHAD')
    ADDRESS_1 = os.getenv('COMPANY_ADDRESS_1', 'LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR')
    ADDRESS_2 = os.getenv('COMPANY_ADDRESS_2', 'SELANGOR DARUL EHSAN')
    REGISTRATION = os.getenv('COMPANY_REGISTRATION', '474523-K')
    PHONE = os.getenv('COMPANY_PHONE', '0162120051')
    MANAGER = os.getenv('COMPANY_MANAGER', 'AH SENG')
