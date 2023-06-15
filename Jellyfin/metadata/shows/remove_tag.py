import os

class Jellyfin:

    # Searches show directory for 'tvshow.nfo' files
    def process_directory(self, directory, tag):

        # Include folders you do not want to include in your search
        skip_list = {os.path.join(directory, "Game of Thrones (2011)")}

        # Begin search
        for root, dirs, files in os.walk(directory):
            if root in skip_list:
                print(f"Skipped: {root}")
                continue

            for file in files:
                if file.endswith('tvshow.nfo'):
                    file_path = os.path.join(root, file)
                    self.process_nfo_file(file_path, tag)
                    print(f"Processed: {root}")

    # Removes tag found 'tvshow.nfo' file
    def process_nfo_file(self, file_path, tag):

        tvshow_nfo = []

        # Add every line except our selected tag
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if f"<tag>{tag}</tag>".strip() not in line.strip():
                    tvshow_nfo.append(line)

        # Overwrite nfo file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(tvshow_nfo)

if __name__ == "__main__":
    show_directory = input("Enter the directory path for your Jellyfin's show library: ").strip()
    show_directory = r"{dir}".format(dir=show_directory)

    tag = input("Tag to remove: ").strip()

    jf = Jellyfin()
    jf.process_directory(show_directory, tag)
