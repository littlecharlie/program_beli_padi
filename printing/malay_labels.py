"""
Malay Language Labels
Centralized labels for receipt generation in Malay language
"""


class MalayLabels:
    """Centralized Malay language labels for receipts"""

    # ===== HEADER LABELS =====
    HEADER_SUBSIDI_PADI = "SUBSIDI PADI"
    TITLE_BIL_BELIAN = "BIL BELIAN PADI"

    # ===== COMPANY INFORMATION =====
    LICENSE_NUMBER = "NO LESEN"
    PHONE_NUMBER = "NO. TELEFON"

    # ===== BILL INFORMATION =====
    BILL_NUMBER = "BIL BELIAN"
    DATE = "TARIKH"

    # ===== FARMER INFORMATION =====
    FARMER_NAME = "NAMA PETANI"
    ADDRESS = "ALAMAT"
    FARMER_REGISTRATION = "NO DAFTAR PESAWAH"
    SUBSIDY_CARD = "NO KAD SUBSIDI"
    IC_NUMBER = "NO KAD PENGENALAN"
    BANK_ACCOUNT = "NO AKAUN BANK"

    # ===== TRANSPORT INFORMATION =====
    TRUCK_NUMBER = "NO LORI"
    WEIGHBRIDGE_RECEIPT = "NO RESIT TIMBANG"

    # ===== DISCOUNT BREAKDOWN =====
    DISCOUNT_WAP_BASAH = "Wap Basah"
    DISCOUNT_HAMPA_PADI = "Hampa Padi"
    DISCOUNT_PADI_MUDA = "Padi Muda/Rosak"

    # ===== WEIGHT SECTION =====
    GROSS_WEIGHT = "BERAT TIMBANGAN"
    DISCOUNT = "POTONGAN"
    NET_WEIGHT = "BERAT BERSIH"
    PRICE_1000KG = "HARGA (1000KG)"
    RICE_VALUE = "NILAI PADI"

    # ===== CALCULATION SUMMARY =====
    SUBSIDY_ESTIMATE = "Anggaran Subsidi"
    HARVEST_AREA = "KAWASAN TUAIAN"
    TOTAL_PAYMENT = "JUMLAH BAYARAN"

    # ===== FOOTER =====
    PREPARED_BY = "DISEDIAKAN OLEH"
    RECEIVER_SIGNATURE = "T. TANGAN PENERIMA"

    # ===== DELIVERY INVOICE LABELS =====
    DELIVERY_INVOICE = "INVOIS HANTARAN"
    RICE_MILL = "KILANG PADI"
    MILL_ADDRESS = "ALAMAT KILANG"
    TRUCK_DRIVER = "PEMANDU"
    DELIVERY_DATE = "TARIKH HANTARAN"
    TOTAL_BILLS = "JUMLAH BIL"
    BILL_LIST = "SENARAI BIL"
    DESTINATION = "DESTINASI"

    # ===== UNIT LABELS =====
    UNIT_KG = "KG"
    UNIT_RM = "RM"

    # ===== OTHER LABELS =====
    NOTES = "CATATAN"
    SIGNATURE = "TANDATANGAN"
    DATE_SIGNED = "TARIKH TANDATANGAN"

    @staticmethod
    def get_all_labels() -> dict:
        """
        Get all labels as a dictionary

        Returns:
            Dictionary of all label constants
        """
        labels = {}
        for attr_name in dir(MalayLabels):
            if not attr_name.startswith('_') and attr_name.isupper():
                labels[attr_name] = getattr(MalayLabels, attr_name)
        return labels

    @staticmethod
    def translate(key: str, default: str = "") -> str:
        """
        Get label by key (for flexibility)

        Args:
            key: Label key (uppercase)
            default: Default value if key not found

        Returns:
            Label value or default
        """
        return getattr(MalayLabels, key.upper(), default)
