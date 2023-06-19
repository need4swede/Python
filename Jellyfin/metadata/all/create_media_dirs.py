import os
import shutil

# Creates all the directories within the root of the source_dir within the destination_dir
def create_folder_structure(source_dir, destination_dir):
    # Get the absolute paths of the source and destination directories
    source_dir = os.path.abspath(source_dir)
    destination_dir = os.path.abspath(destination_dir)

    # Walk through the source directory recursively
    for root, dirs, files in os.walk(source_dir):
        # Get the relative path of the current directory from the source directory
        relative_path = os.path.relpath(root, source_dir)

        # Construct the corresponding destination directory path
        destination_path = os.path.join(destination_dir, relative_path)

        # Create the destination directory if it doesn't exist
        os.makedirs(destination_path, exist_ok=True)


# Usage example:
source_directory = input('Source Directory: ')
destination_directory = input('Destination Directory: ')
create_folder_structure(source_directory, destination_directory)