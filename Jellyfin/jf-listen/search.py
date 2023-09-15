
## IMPORTS
if 'Imports':

    if 'Standard':
        import config, re, json

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

class JFListen():

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

movie_added = "/Movies/The Lion King (1994)/The Lion King (1994).mkv"
match = re.search(r'^(.+) \((\d{4})\)\.mkv$', movie_added.split('/')[-1])

if match:
    movie_title = match.group(1)
    movie_year = int(match.group(2))
    jf_listen = JFListen()
    results = jf_listen.search(
        title=movie_title,
        media_type='Movie',
        year=1994,
        data='title'
    )
    print(results)


