import os, shutil

class Jellyfin():

    def copy_nfo_files(self, source_root, destination_root):
        has_text = input('Do you already have a text file containing the paths for all your "nfo" files? (Y/N): ')
        if has_text.lower() == 'n':
            self.process_directory(source_root)
            text_list = os.path.join(source_root, 'nfo_files.txt')
        else:
            text_list = input('Path to text file: ')
        self.create_media_structure(source_root, destination_root)
        with open(text_list, 'r') as file:
            for line in file:
                source_file = line.strip()
                destination_file = source_file.replace(source_root, destination_root)
                shutil.copy(source_file, destination_file)

    def create_media_structure(self, source_dir, destination_dir):
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

    # Searches show directory for '.nfo' files
    def process_directory(self, directory):

        # Begin search
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.nfo'):
                    nfo_file = os.path.join(root, file)
                    self.write_to_file(nfo_file, directory)
        print('---\nDone')

    # Writes .nfo file location to text
    def write_to_file(self, text, media_dir):
        nfo_text_file = os.path.join(media_dir, 'nfo_files.txt')
        with open(nfo_text_file, 'a+', encoding='utf-8') as textFile:
            textFile.write(text + '\n')

if __name__ == "__main__":

    # Root directory path of where your media is stored (the parent folder of your Movies/Shows directories)
    input_directory = input("Enter the root directory path for your Jellyfin's media library: ")
    input_directory = r"{in_dir}".format(in_dir=input_directory)

    # All the directories from your input directory will be created within the root of this folder
    output_directory = input("Enter the root directory path of where you want to copy all the files: ")
    output_directory = r"{out_dir}".format(out_dir=output_directory)

    # Begin instance
    jf = Jellyfin()
    jf.copy_nfo_files(input_directory, output_directory)