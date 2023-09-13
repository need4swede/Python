
## IMPORTS
if 'Imports':
    import os
    import shutil
    from PIL import Image, ImageOps, UnidentifiedImageError

## SETTINGS
IMG_HEIGHT = 3000
IMG_WIDTH = 3000
IMG_FOLDER = ''

## VERIFY FILE VALIDITY
def is_valid_image(file_path):
    with open(file_path, 'rb') as f:
        header = f.read(8)
    if header.startswith(b'\x89PNG\r\n\x1a\n'):
        return True
    elif header.startswith(b'\xFF\xD8'):
        return True
    elif header[:6] in [b'GIF87a', b'GIF89a']:
        return True
    return False

## RESIZE IMAGE
def resize_and_crop(image_path):
    try:
        with Image.open(image_path).convert("RGBA") as img:
            img = ImageOps.fit(img, (IMG_WIDTH, IMG_HEIGHT), method=0, bleed=0.0)
            img.save(image_path, "PNG")
    except UnidentifiedImageError:
        print(f"Skipping {image_path}: Unidentified image format.")

## MAIN
def main(root_folder):
    # Create the ORIGINAL_IMAGES directory inside root folder
    copied_root = os.path.join(root_folder, 'ORIGINAL_IMAGES')
    if not os.path.exists(copied_root):
        os.makedirs(copied_root)

    # Traverse the directory structure
    for dirpath, dirnames, filenames in os.walk(root_folder):
        if "ORIGINAL_IMAGES" in dirpath:
            continue

        for filename in filenames:
            if filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp')):
                image_path = os.path.join(dirpath, filename)

                if is_valid_image(image_path):

                    # Determine the output folder for ORIGINAL_IMAGES
                    relative_path = os.path.relpath(dirpath, root_folder)
                    output_folder = os.path.join(copied_root, relative_path)

                    # Create output directory if not exists
                    if not os.path.exists(output_folder):
                        os.makedirs(output_folder)

                    # Copy the file to ORIGINAL_IMAGES directory
                    shutil.copy2(image_path, os.path.join(output_folder, filename))

                    # Apply resizing and cropping to the actual file
                    resize_and_crop(image_path)
                else:
                    print(f"Skipping {image_path}: Not a valid image file.")

## RUN
if __name__ == "__main__":
    main(IMG_FOLDER)
