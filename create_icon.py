"""
Create application icon for Rice Billing System
Generates a simple .ico file for the Windows executable
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    """Create a simple application icon"""

    # Create multiple sizes for Windows icon (256x256, 128x128, 64x64, 48x48, 32x32, 16x16)
    sizes = [256, 128, 64, 48, 32, 16]
    images = []

    for size in sizes:
        # Create new image with transparent background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Colors - green for rice/agriculture theme
        bg_color = (76, 175, 80)  # Material green
        text_color = (255, 255, 255)  # White
        border_color = (56, 142, 60)  # Darker green

        # Draw rounded rectangle background
        margin = max(2, size // 16)
        draw.rounded_rectangle(
            [(margin, margin), (size - margin, size - margin)],
            radius=size // 8,
            fill=bg_color,
            outline=border_color,
            width=max(1, size // 32)
        )

        # Draw rice/grain symbol (simplified)
        # Draw a grain/rice grain shape in the center
        center_x, center_y = size // 2, size // 2
        grain_width = size // 3
        grain_height = size // 2

        # Draw oval for rice grain
        grain_bbox = [
            center_x - grain_width // 2,
            center_y - grain_height // 2,
            center_x + grain_width // 2,
            center_y + grain_height // 2
        ]
        draw.ellipse(grain_bbox, fill=text_color, outline=border_color, width=max(1, size // 64))

        # Add text "RB" for Rice Billing (only for larger sizes)
        if size >= 48:
            try:
                # Try to use a font, fallback to default if not available
                font_size = size // 4
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                except:
                    font = ImageFont.load_default()

                text = "RB"
                # Get text bounding box
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                # Position text at bottom
                text_x = (size - text_width) // 2
                text_y = size - text_height - margin * 2

                # Draw text with shadow for better visibility
                shadow_offset = max(1, size // 64)
                draw.text((text_x + shadow_offset, text_y + shadow_offset), text, font=font, fill=(0, 0, 0, 128))
                draw.text((text_x, text_y), text, font=font, fill=text_color)
            except Exception as e:
                print(f"Note: Could not add text to {size}x{size} icon: {e}")

        images.append(img)

    # Save as .ico file
    output_path = os.path.join(os.path.dirname(__file__), 'resources', 'app_icon.ico')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the icon with multiple sizes
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in images],
        append_images=images[1:]
    )

    print(f"✓ Icon created successfully: {output_path}")

    # Also save a PNG version for reference
    png_path = output_path.replace('.ico', '.png')
    images[0].save(png_path, format='PNG')
    print(f"✓ PNG version saved: {png_path}")

    return output_path


if __name__ == "__main__":
    print("Creating Rice Billing System application icon...")
    icon_path = create_app_icon()
    print(f"\nIcon ready for PyInstaller: {icon_path}")
    print("\nYou can replace this with a custom icon if desired.")
    print("Icon requirements for Windows:")
    print("  - .ico format")
    print("  - Multiple sizes: 256x256, 128x128, 64x64, 48x48, 32x32, 16x16")
    print("  - Recommended: Professional design with your logo/branding")
