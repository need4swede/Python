
## IMPORTS
if "Imports":
    import os, time, re
    from jf_listen import JFListen
    from datetime import datetime, timedelta
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

## LISTENS FOR CHANGES TO A DIRECTORY
class ListenForChanges(FileSystemEventHandler):

    ## INITIALIZE CLASS
    def __init__(self, directory):
        super().__init__()
        self.directory = directory
        self.jf_listen = JFListen()

    ## START LISTENING
    def start(self):

        ## START OBSERVER
        observer = Observer()
        observer.schedule(listening, self.directory, recursive=True)
        observer.start()

        ## PRINT TO TERMINAL
        print('\nListening for changes to movies...\n(Press "CTRL+C" to quit)\n')

        ## RUNNING...
        try:
            while True:
                ## CHECKS FOR CHANGES EVERY SECOND
                time.sleep(1)
        except KeyboardInterrupt:
            ## STOPS ON KEY INPUT
            observer.stop()

        ## WAIT FOR OBSERVER TO COMPLETE
        observer.join()

    ## INFO OF CHANGED FILE
    def read_file_info(self, change):
        filepath, filename = os.path.split(change.src_path)
        filetype = str(filename).split('.')[-1]
        return filepath, filename, filetype

    ## CHECKS IF A PATH IS A FILE
    def is_file(self, path):
        _, extension = os.path.splitext(path)
        return bool(extension)

    ## RETURNS NAME OF A FOLDER FROM A PATH
    def dirname(self, path):

        ## REMOVE TRAILING SLASHES
        path = path.rstrip(os.path.sep)

        ## GET DIRNAME
        dirname = os.path.basename(path)
        return dirname

    ## HANDLE CHANGES
    def on_any_event(self, event):

        ## GET FILE INFO
        self.filepath, self.filename, self.filetype = self.read_file_info(event)

        ## API CALL BOOL
        call_api = False

        ## FILTER OUT METADATA FILES
        if self.filetype not in ['jpg', 'nfo', 'srt', 'png']:

            ## WHEN A FILE IS CREATED, MOVED OR DELETED
            if event.event_type in ['created', 'moved', 'deleted'] and not event.is_directory:
                call_api = True

        ## IF VALID EVENT, CALL API
        if call_api and self.is_file(self.filename):

            ## REMOVE EXTENSION FROM FILENAME
            filename_pattern = re.compile(r"^(.+)\.[^\.]+$")
            filename_match = filename_pattern.match(self.filename)
            filename = filename_match.group(1) if filename_match else None

            ## GET TITLE AND YEAR
            title_year_pattern = re.compile(r"^(.+) \((\d{4})\)$")
            title_year_match = title_year_pattern.match(filename)
            title = title_year_match.group(1) if title_year_match else None
            year = int(title_year_match.group(2)) if title_year_match else None

            ## CALL API
            self.jf_listen.event(title, year, event.event_type, event.src_path)

## RUN CODE
if __name__ == '__main__':

    ## CREATE LISTENING INSTANCE
    listening = ListenForChanges('/Users/afshari/Pictures/JFLISTEN')
    listening.start()

