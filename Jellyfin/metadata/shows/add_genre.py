import os

class Jellyfin():

    # Searches show directory for 'tvshow.nfo' files
    def process_directory(self, directory, genre):

        # Include folders you do not want to include in your search
        skip_list = [
        f"{directory}\\Game of Thrones (2011)"
        ]

        # Begin search
        for root, dirs, files in os.walk(directory):
            for file in files:
                if not root in skip_list:
                    if file.endswith('tvshow.nfo'):
                        file_path = os.path.join(root, file)
                        self.process_nfo_file(file_path, genre)
                        print(f'Processed: {root}')
                else:
                    print(f'Skipped: {root}')

    # Adds genre to found 'tvshow.nfo' file
    def process_nfo_file(self, file_path, genre):
        with open(file_path, 'r+', encoding='utf-8') as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if line.startswith('  <genre>'):
                    lines.insert(i + 1, f'  <genre>{genre}</genre>\n')
                    break
                elif line.startswith('  <studio>'):
                    lines.insert(i + 1, f'  <tag>{genre}</tag>\n')
                    break
                elif line.startswith('  <genre>'):
                    lines.insert(i + 1, f'  <tag>{genre}</tag>\n')
                    break
            else:
                pass

            file.seek(0)
            file.writelines(lines)
            file.truncate()

if __name__ == "__main__":

    # Directory path of where your shows are stored
    show_directory = input("Enter the directory path for your Jellyfin's show library: ")
    show_directory = r"{dir}".format(dir=show_directory)

    # Tag that you want added to all of your shows
    genre = input("Genre to add: ")

    # Begin instance
    jf = Jellyfin()
    jf.process_directory(show_directory, genre)