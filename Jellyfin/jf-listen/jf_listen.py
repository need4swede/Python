
## IMPORTS
if 'Imports':

    if 'Standard':
        import config, os

    if 'Libraries':
        from jellyfin_apiclient_python import JellyfinClient

## SETTINGS
if 'Settings':

    ## APP INFO
    APP_NAME = config.local['app']

    ## APP VERSION
    APP_VERSION = config.local['version']

    ## DEVICE NAME
    DEVICE_NAME = config.local['device']

    ## DEVICE ID
    DEVICE_ID = config.local['id']

    ## JELLYFIN SERVER
    ADDRESS = config.server['address']

    ## JELLYFIN USERNAME
    USER = config.server['user']

    ## JELLYFIN PASSWORD
    PASSWORD = config.server['password']

## MAIN APP
class JFListen():

    ## INITIALIZE
    def __init__(self):
        super().__init__()
        self.client = JellyfinClient()
        self.client_config()
        self.login()

    ## SET CLIENT CONFIGURATION
    def client_config(self):
        self.client.config.app(APP_NAME, APP_VERSION, DEVICE_NAME, DEVICE_ID)
        self.client.config.data["auth.ssl"] = True

    ## LOGIN TO JELLYFIN SERVER
    def login(self):
        self.client.auth.connect_to_address(ADDRESS)
        self.client.auth.login(ADDRESS, USER, PASSWORD)

    ## UPDATE CONFIG FILE WITH ADDITIONAL SERVER INFO
    def update_config(self):

        media_libraries = self.get_libraries()
        config.server['movie_library'] = media_libraries['Movies']
        config.server['show_library'] = media_libraries['Shows']

    ## EVENT HANDLER TO TRIGGER REFRESH
    def event(self, title, year, event_type=None, event_path=None):

        ## GET CONTENT TYPE
        content = str(event_path).split(os.path.sep)

        ## GENERATE MESSAGE
        if 'Movies' in content:
            print(f"'{title} ({year})' has been {event_type}\n{event_path}\n")
        if 'Shows' in content:
            print(f"An episode of '{content[-3]}' has been {event_type}:\n"
                f"{os.path.splitext(content[-1])[0]}\n")

        ## GET ITEM ID
        # item_id = self.search(title=title, year=year, data='id')

    ## SEARCH FOR A LIBRARY ITEM
    def search(self, title:str, media_type:str=None, year:int=None, data:str=None):
        if data == 'id':
            results = self.client.jellyfin.search_media_items(
                        term=title, media=media_type, limit=1, year=year)
            items_list = results.get('Items', [])
            ids = [item.get('Id', '') for item in items_list]
            return ids[0]
        if data == 'title':
            results = self.client.jellyfin.search_media_items(
                        term=title, media=media_type, limit=1, year=year)
            items_list = results.get('Items', [])
            ids = [item.get('Name', '') for item in items_list]
            return ids[0]
        else:
            return self.client.jellyfin.search_media_items(
                        term=title, media=media_type, limit=1, year=year)

    ## GET THE MOST RECENTLY ADDED ITEM
    def recently_added(self, data:str=None, limit=1):
        results = self.client.jellyfin.get_recently_added(limit=limit)
        if data == 'id':
            results = results[0].get('Id', None)
        return results

    ## RETURNS A DICT OF ALL LIBRARIES ON SERVER
    def get_libraries(self):
        media_libraries = self.client.jellyfin.get_media_folders()
        libraries = [(item['Name'], item['Id']) for item in media_libraries['Items'] if item['Name'] != 'Collections']
        return dict(libraries)

    ## RUN REFRESH ON SERVER
    def refresh_items(self, item_id, preset=None):
        return self.client.jellyfin.refresh_item(item_id, preset=preset)