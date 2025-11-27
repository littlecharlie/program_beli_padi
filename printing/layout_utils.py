"""
Receipt Layout Utilities
Provides utilities for precise receipt formatting and alignment
"""


class ReceiptLayoutUtils:
    """Utilities for precise receipt formatting (80 characters max)"""

    LINE_WIDTH = 80

    @staticmethod
    def format_label_value(
        label: str,
        value: str,
        label_width: int = 35,
        total_width: int = 80
    ) -> str:
        """
        Format label:value pair with precise alignment

        Args:
            label: Label text
            value: Value text (will be right-aligned)
            label_width: Width for label column
            total_width: Total line width

        Returns:
            Formatted line with label and right-aligned value
        """
        value_width = total_width - label_width - 3  # 3 for " : "
        return f"{label:<{label_width}} : {value:>{value_width}}"

    @staticmethod
    def format_two_columns(
        left_label: str,
        left_value: str,
        right_label: str,
        right_value: str,
        total_width: int = 80
    ) -> str:
        """
        Format two label:value pairs side by side

        Args:
            left_label: Left label
            left_value: Left value
            right_label: Right label
            right_value: Right value
            total_width: Total line width

        Returns:
            Formatted line with two columns
        """
        mid_point = total_width // 2
        left_part = f"{left_label}: {left_value}"
        right_part = f"{right_label}: {right_value}"

        # Pad left part and add right part
        left_padded = left_part.ljust(mid_point)
        return f"{left_padded}{right_part}"

    @staticmethod
    def format_discount_line(
        wap: float,
        hampa: float,
        muda: float,
        total: float
    ) -> str:
        """
        Format discount breakdown line

        Args:
            wap: Wap Basah percentage
            hampa: Hampa Padi percentage
            muda: Padi Muda/Rosak percentage
            total: Total discount percentage

        Returns:
            Formatted discount line
        """
        # Display as integers (no decimals) like sample PDF
        return (f"Wap Basah {int(wap)}  "
                f"Hampa Padi {int(hampa)}  "
                f"Padi Muda/Rosak {int(muda)}  "
                f"= {int(total)}%")

    @staticmethod
    def format_columns(
        values: list,
        widths: list,
        alignment: list = None
    ) -> str:
        """
        Format multiple columns with specified widths and alignments

        Args:
            values: List of values to format
            widths: List of column widths
            alignment: List of alignments ('left', 'right', 'center')

        Returns:
            Formatted line with aligned columns
        """
        if alignment is None:
            alignment = ['left'] * len(values)

        cols = []
        for val, width, align in zip(values, widths, alignment):
            val_str = str(val)
            if align == 'right':
                cols.append(f"{val_str:>{width}}")
            elif align == 'center':
                cols.append(f"{val_str:^{width}}")
            else:  # left
                cols.append(f"{val_str:<{width}}")

        return ''.join(cols)

    @staticmethod
    def separator_line(char: str = '-') -> str:
        """
        Generate separator line

        Args:
            char: Character to use for separator

        Returns:
            Separator line of LINE_WIDTH characters
        """
        return char * ReceiptLayoutUtils.LINE_WIDTH

    @staticmethod
    def center_text(text: str, total_width: int = 80) -> str:
        """
        Center text within specified width

        Args:
            text: Text to center
            total_width: Width to center within

        Returns:
            Centered text
        """
        text_str = str(text)
        padding = max(0, (total_width - len(text_str)) // 2)
        return ' ' * padding + text_str

    @staticmethod
    def pad_right(text: str, width: int = 80) -> str:
        """
        Pad text to right (left align)

        Args:
            text: Text to pad
            width: Target width

        Returns:
            Right-padded text
        """
        return str(text).ljust(width)

    @staticmethod
    def format_money(value: float) -> str:
        """
        Format value as Malaysian Ringgit

        Args:
            value: Numeric value

        Returns:
            Formatted currency string (e.g., "RM 1,234.56")
        """
        return f"RM {value:,.2f}"

    @staticmethod
    def format_weight(value: float) -> str:
        """
        Format weight value with comma separator

        Args:
            value: Weight in kg

        Returns:
            Formatted weight string (e.g., "1,234.56")
        """
        return f"{value:,.2f}"

    @staticmethod
    def format_percentage(value: float, decimals: int = 0) -> str:
        """
        Format percentage value

        Args:
            value: Percentage value
            decimals: Number of decimal places

        Returns:
            Formatted percentage string
        """
        if decimals == 0:
            return f"{int(value)}%"
        return f"{value:.{decimals}f}%"

    @staticmethod
    def truncate_text(text: str, max_width: int) -> str:
        """
        Truncate text to fit within max width

        Args:
            text: Text to truncate
            max_width: Maximum width

        Returns:
            Truncated text
        """
        text_str = str(text)
        if len(text_str) > max_width:
            return text_str[:max_width - 1]
        return text_str
