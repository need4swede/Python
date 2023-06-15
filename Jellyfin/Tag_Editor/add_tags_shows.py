import os

class Jellyfin():

    # Searches show directory for 'tvshow.nfo' files
    def process_directory(self, directory, tag):

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
                        self.process_nfo_file(file_path)
                        print(f'Processed: {root}', tag)
                else:
                    print(f'Skipped: {root}')

    # Adds tag to found 'tvshow.nfo' file
    def process_nfo_file(self, file_path, tag):
        with open(file_path, 'r+', encoding='utf-8') as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if line.startswith('  <tag>'):
                    lines.insert(i + 1, f'  <tag>{tag}</tag>\n')
                    break
                elif line.startswith('  <studio>'):
                    lines.insert(i + 1, f'  <tag>{tag}</tag>\n')
                    break
                elif line.startswith('  <genre>'):
                    lines.insert(i + 1, f'  <tag>{tag}</tag>\n')
                    break
            else:
                pass

            file.seek(0)
            file.writelines(lines)
            file.truncate()

if __name__ == "__main__":

    # Directory path of where your shows are stored
    show_directory = input("Enter the directory path for your Jellyfin's show folder: ")
    show_directory = r"{dir}".format(dir=show_directory)

    # Tag that you want added to all of your shows
    tag = input("Tag to add: ")

    # Begin instance
    jf = Jellyfin()
    jf.process_directory(show_directory, tag)