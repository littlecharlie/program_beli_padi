"""
ESC/P Commands Generator
Generates Epson Standard Code for Printers (ESC/P) commands for Epson LQ-310
"""


class EscposCommands:
    """ESC/P command generator for dot matrix printers"""

    # Escape character
    ESC = chr(27)

    # Printer initialization
    INIT_PRINTER = ESC + '@'

    # Font styles
    BOLD_ON = ESC + 'E'
    BOLD_OFF = ESC + 'F'

    UNDERLINE_ON = ESC + '-' + chr(1)
    UNDERLINE_OFF = ESC + '-' + chr(0)

    ITALIC_ON = ESC + '4'
    ITALIC_OFF = ESC + '5'

    # Line spacing
    LINE_SPACING_6 = ESC + '2'  # 6 lines per inch
    LINE_SPACING_8 = ESC + '0'  # 8 lines per inch

    # Character pitch (for 80 columns on standard paper)
    PICA_10CPI = ESC + 'P'  # 10 characters per inch
    ELITE_12CPI = ESC + 'M'  # 12 characters per inch
    CONDENSED_ON = ESC + chr(15)  # Condensed mode
    CONDENSED_OFF = ESC + chr(18)  # End condensed mode

    # Alignment (for dot matrix, these may not work)
    LEFT_ALIGN = ESC + 'a' + chr(0)
    CENTER_ALIGN = ESC + 'a' + chr(1)
    RIGHT_ALIGN = ESC + 'a' + chr(2)

    # Feed paper
    FORM_FEED = chr(12)  # Eject page
    LINE_FEED = chr(10)  # New line

    # Cut paper (if printer supports it)
    CUT_PAPER = ESC + 'i'

    @staticmethod
    def generate_command(command_type: str, *args) -> str:
        """
        Generate ESC/P command

        Args:
            command_type: Type of command to generate
            *args: Arguments for the command

        Returns:
            ESC/P command string
        """
        commands = {
            'init': EscposCommands.INIT_PRINTER,
            'bold_on': EscposCommands.BOLD_ON,
            'bold_off': EscposCommands.BOLD_OFF,
            'underline_on': EscposCommands.UNDERLINE_ON,
            'underline_off': EscposCommands.UNDERLINE_OFF,
            'italic_on': EscposCommands.ITALIC_ON,
            'italic_off': EscposCommands.ITALIC_OFF,
            'left_align': EscposCommands.LEFT_ALIGN,
            'center_align': EscposCommands.CENTER_ALIGN,
            'right_align': EscposCommands.RIGHT_ALIGN,
            'form_feed': EscposCommands.FORM_FEED,
            'cut_paper': EscposCommands.CUT_PAPER,
        }

        return commands.get(command_type, '')

    @staticmethod
    def format_line(text: str, width: int = 80, alignment: str = 'left') -> str:
        """
        Format text line to fit within width

        Args:
            text: Text to format
            width: Line width in characters
            alignment: 'left', 'center', or 'right'

        Returns:
            Formatted line
        """
        text = str(text)

        if alignment == 'center':
            padding = max(0, (width - len(text)) // 2)
            return ' ' * padding + text

        elif alignment == 'right':
            padding = max(0, width - len(text))
            return ' ' * padding + text

        else:  # left align
            return text.ljust(width)

    @staticmethod
    def separator(width: int = 80, char: str = '-') -> str:
        """Generate separator line"""
        return char * width

    @staticmethod
    def format_columns(columns: list, widths: list, separator: str = '  ') -> str:
        """
        Format multiple columns with specified widths

        Args:
            columns: List of column texts
            widths: List of column widths
            separator: Separator between columns

        Returns:
            Formatted line with columns
        """
        formatted_cols = []
        for col, width in zip(columns, widths):
            col_str = str(col)
            if len(col_str) > width:
                col_str = col_str[:width-1]
            formatted_cols.append(col_str.ljust(width))

        return separator.join(formatted_cols)

    @staticmethod
    def bold_text(text: str) -> str:
        """Wrap text with bold commands"""
        return EscposCommands.BOLD_ON + text + EscposCommands.BOLD_OFF

    @staticmethod
    def underline_text(text: str) -> str:
        """Wrap text with underline commands"""
        return EscposCommands.UNDERLINE_ON + text + EscposCommands.UNDERLINE_OFF

    @staticmethod
    def format_currency(value: float) -> str:
        """Format value as currency (RM)"""
        return f"RM {value:,.2f}"

    @staticmethod
    def format_number(value: float, decimals: int = 2) -> str:
        """Format number with decimal places"""
        if decimals == 0:
            return f"{value:,.0f}"
        return f"{value:,.{decimals}f}"
