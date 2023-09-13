
## IMPORTS
if "Imports":
    import config_movies, os, requests, time
    from datetime import datetime, timedelta
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

## JELLYFIN INFO AND ACTIONS
class Jellyfin():

    ## INITIALIZE CLASS
    def __init__(self):
        self.port = config_movies.server['port']
        self.address = config_movies.server['address']
        self.url = f"{self.address}:{self.port}"

        self.api_key = config_movies.server['api_key']
        self.library = config_movies.server['library_id']
        self.refresh_mode = config_movies.refresh_mode['missing']
        self.content_dir = config_movies.server['content_dir']
        self.logfile = config_movies.server['log_file']
        self.last_refresh = None

    ## RUN REFRESH
    def refresh(self):

        ## GENERATE REQUEST
        endpoint = f"{self.url}/Items/{self.library}/{self.refresh_mode}"
        headers = {
            "X-MediaBrowser-Token": self.api_key,
            "Content-Type": "application/json"
        }

        ## MAKE REQUEST
        try:
            response = requests.post(endpoint, headers=headers)
            response.raise_for_status()
            self.last_refresh = datetime.now()
        except requests.exceptions.RequestException as e:
            print(f"...ERROR: {e}")

## LISTENS FOR CHANGES TO A DIRECTORY
class ListenForChanges(FileSystemEventHandler):

    ## INITIALIZE CLASS
    def __init__(self, jellyfin):
        self.jellyfin = jellyfin

    ## START LISTENING
    def start(self):

        ## START OBSERVER
        observer = Observer()
        observer.schedule(listening, directory, recursive=True)
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

        ## CALCULATE TIME
        now = datetime.now()
        event_timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
        if self.jellyfin.last_refresh:
            time_diff = now - self.jellyfin.last_refresh
            minutes_diff = int(time_diff.total_seconds() / 60)
            seconds_diff = int(time_diff.total_seconds())

        ## REFRESH BOOL
        run_refresh = False

        ## FILTER OUT METADATA FILES
        if self.filetype not in ['jpg', 'nfo', 'srt', 'png']:

            ## WHEN A FILE IS CREATED, MOVED OR DELETED
            if event.event_type in ['created', 'moved', 'deleted'] and not event.is_directory:
                run_refresh = True

        ## IF VALID EVENT, RUN REFRESH
        if run_refresh:

            ## CHECK IF A FILE WAS CHANGED
            if self.is_file(self.filename):

                ## GET FOLDER NAME OF JELLYFIN CONTENT DIR
                jelly_dir = self.dirname(self.jellyfin.content_dir)

                ## IF THE FILE IS WITHIN A FOLDER, USE FOLDER INSTEAD
                temp_filename = os.path.basename(os.path.dirname(event.src_path))
                if not temp_filename == jelly_dir:
                    self.filename = temp_filename

            ## PRINT DESCRIPTION, WITH TIMESTAMP
            event_message = f"'{self.filename}' has been {event.event_type}\n{event.src_path}\n"

            ## WRITE EVENT TO LOGFILE
            with open(self.jellyfin.logfile, "a+") as logFile:
                logFile.write(f"{event_timestamp}\n{event_message}\n\n")

            ## CHECK IF REFRESH LAST RAN WITHIN TIME FRAME
            if self.jellyfin.last_refresh and (now - self.jellyfin.last_refresh) < timedelta(minutes=int(config_movies.server['refresh_delay'])):
                if minutes_diff < 1:
                    print(event_timestamp + f" - Refresh Skipped! Last ran {seconds_diff} seconds ago [Delay: {config_movies.server['refresh_delay']}min]" + '\n' + event_message)
                else:
                    print(event_timestamp + f" - Refresh Skipped! Last ran {minutes_diff} minutes ago [Delay: {config_movies.server['refresh_delay']}min]" + '\n' + event_message)
                return
            else:
                ## REFRESH JELLYFIN
                print(event_timestamp + '\n' + event_message)
                self.jellyfin.refresh()



## RUN CODE
if __name__ == '__main__':

    ## CREATE JELLYFIN INSTANCE
    jellyfin = Jellyfin()
    directory = jellyfin.content_dir

    ## CREATE LISTENING INSTANCE
    listening = ListenForChanges(jellyfin)
    listening.start()

