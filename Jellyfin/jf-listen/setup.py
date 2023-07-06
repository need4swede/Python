import os, sys, subprocess

## INSTALL PACKAGES
def install(cwd):

    # Install required packages
    print('Installing Packages...')
    subprocess.run(["pip", "install", "-r", "requirements.txt", "--quiet"])
    print("Packages Installed.\nSee 'packages.txt' for a complete list\n-----------------")
    os.rename(os.path.join(cwd, 'requirements.txt'), os.path.join(cwd, 'packages.txt'))
    config()

## RUN CONFIG
def config():

    ## GET INITIAL DATA
    with open('config.py', 'r') as configFile:
        initial_data = ''.join(configFile.readlines())

    ## BACKUP CONFIG
    with open('config.py.bak', 'w+') as configBackup:
        configBackup.write(initial_data)

    ## START
    print("\nWelcome to the 'Listen' Initial Setup\nThis will overwrite the existing config!\n")
    cont = input('Continue? (y/n): ')
    if not cont.lower() == 'y':
        print('Exiting Setup...')
        sys.exit()

    ## ADDRESS
    address = input('\n\nAddress of your Jellyfin server (including protocol, like "http://"): ')
    if ':' in address:
        address = address.split(':')[0]
    address = address.strip()

    ## PORT
    port = input('Port: ')
    port = port.strip()

    ## API
    api_key = input('API Key: ')

    ## CONTENT DIR
    content_dir = input('Root folder of your media, (ex. "User/Videos/Jellyfin/Movies"): ')
    content_dir = content_dir.strip()

    ## LIBRARY ID
    library_id = input('Your Library ID (the characters after "topParentId=" when viewing your library through a browser): ')
    library_id = library_id.strip()

    ## LOG FILE
    log_file = input('Where should I save your logs? (Path to a folder): ')
    log_file = log_file.strip()
    log_file = os.path.join(log_file, 'log.txt')

    ## UPDATED CONFIG DATA
    configured_data = f"""server = dict(
    address = "{address}",
    port = "{port}",
    api_key = "{api_key}",
    content_dir = "{content_dir}",
    library_id = "{library_id}",
    log_file = "{log_file}"
)

refresh_mode = dict(
    default = "Refresh",
    missing = "Refresh?Recursive=true&ImageRefreshMode=FullRefresh&MetadataRefreshMode=FullRefresh&ReplaceAllImages=false&ReplaceAllMetadata=false",
    replace_images = "Refresh?Recursive=true&ImageRefreshMode=FullRefresh&MetadataRefreshMode=FullRefresh&ReplaceAllImages=true&ReplaceAllMetadata=false",
    replace_metadata = "Refresh?Recursive=true&ImageRefreshMode=FullRefresh&MetadataRefreshMode=FullRefresh&ReplaceAllImages=false&ReplaceAllMetadata=true",
    replace_all = "Refresh?Recursive=true&ImageRefreshMode=FullRefresh&MetadataRefreshMode=FullRefresh&ReplaceAllImages=true&ReplaceAllMetadata=true"
)
"""

    ## SAVE NEW CONFIG
    with open('config.py', 'w') as configFile:
        configFile.write(configured_data)

    ## COMPLETE
    print('\nSetup is now complete!\nYou can now run "listen.py"')

## GET CURRENT DIR
cwd = os.getcwd()

## RUN INSTALL OR CONFIG
if os.path.isfile(os.path.join(cwd, 'requirements.txt')):
    install(cwd)
else:
    config()