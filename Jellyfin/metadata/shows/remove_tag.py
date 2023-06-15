import os

class Jellyfin:
    def process_directory(self, directory, tag):
        skip_list = {os.path.join(directory, "Game of Thrones (2011)")}

        for root, dirs, files in os.walk(directory):
            if root in skip_list:
                print(f"Skipped: {root}")
                continue

            for file in files:
                if file.endswith('tvshow.nfo'):
                    file_path = os.path.join(root, file)
                    self.process_nfo_file(file_path, tag)
                    print(f"Processed: {root}")

    def process_nfo_file(self, file_path, tag):
        lines = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if f"<tag>{tag}</tag>".strip() not in line.strip():
                    lines.append(line)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)

if __name__ == "__main__":
    show_directory = input("Enter the directory path for your Jellyfin's show library: ").strip()
    show_directory = r"{dir}".format(dir=show_directory)

    tag = input("Tag to remove: ").strip()

    jf = Jellyfin()
    jf.process_directory(show_directory, tag)
