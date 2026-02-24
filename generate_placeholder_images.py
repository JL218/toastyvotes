from PIL import Image, ImageDraw, ImageFont
import os

def create_logo(filename, size=(300, 100), text="ToastyVotes", bg_color=(255, 255, 255), text_color=(255, 140, 0)):
    # Create a white image
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw text in center
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
    
    draw.text(position, text, fill=text_color, font=font)
    
    # Save the image
    img.save(filename)

def create_icon(filename, size=(100, 100), icon_type="vote", bg_color=(255, 255, 255), icon_color=(255, 140, 0)):
    # Create a white image
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw different icon shapes based on type
    if icon_type == "vote":
        # Draw a simple checkmark
        points = [(20, 50), (40, 70), (80, 30)]
        draw.line(points, fill=icon_color, width=5)
    elif icon_type == "timer":
        # Draw a simple clock
        draw.ellipse([(20, 20), (80, 80)], outline=icon_color, width=3)
        draw.line([(50, 50), (50, 30)], fill=icon_color, width=3)
        draw.line([(50, 50), (65, 65)], fill=icon_color, width=3)
    elif icon_type == "trophy":
        # Draw a simple trophy
        draw.rectangle([(35, 60), (65, 80)], fill=icon_color)
        draw.rectangle([(45, 20), (55, 60)], fill=icon_color)
        draw.ellipse([(25, 20), (45, 40)], fill=icon_color)
        draw.ellipse([(55, 20), (75, 40)], fill=icon_color)
    
    # Save the image
    img.save(filename)

def main():
    # Ensure directory exists
    images_dir = os.path.join('static', 'voting', 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    # Create logo images
    create_logo(os.path.join(images_dir, 'toastyvotes-logo-large.png'), size=(600, 200))
    create_logo(os.path.join(images_dir, 'toastyvotes-logo.png'), size=(300, 100))
    
    # Create icon images
    create_icon(os.path.join(images_dir, 'vote-icon.png'), icon_type="vote")
    create_icon(os.path.join(images_dir, 'timer-icon.png'), icon_type="timer")
    create_icon(os.path.join(images_dir, 'trophy-icon.png'), icon_type="trophy")
    create_icon(os.path.join(images_dir, 'trophy.png'), icon_type="trophy", size=(50, 50))
    
    print("Placeholder images created successfully!")

if __name__ == "__main__":
    main()
