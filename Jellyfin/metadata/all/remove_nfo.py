import os

class Jellyfin():

    # Searches show directory for '.nfo' files
    def process_directory(self, directory):

        # Begin search
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.nfo'):
                    nfo_file = os.path.join(root, file)
                    os.remove(nfo_file)
                    self.write_to_file(nfo_file, directory)
        print('---\nDone')

    # Writes .nfo file location to text
    def write_to_file(self, text, media_dir):
        nfo_text_file = os.path.join(media_dir, 'removed_nfo_files.txt')
        with open(nfo_text_file, 'a+', encoding='utf-8') as textFile:
            textFile.write("Removed: " + text + '\n')

if __name__ == "__main__":

    # Root directory path of where your media is stored (the parent folder of your Movies/Shows directories)
    media_directory = "/Volumes/Bifrost/Yggdrasil/Movies"
    media_directory = r"{dir}".format(dir=media_directory)

    # Begin instance
    jf = Jellyfin()
    jf.process_directory(media_directory)