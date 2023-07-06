import os, sys, subprocess

## INSTALL PACKAGES
def install(cwd):

    # Install required packages
    print('Installing Packages...')
    subprocess.run(["pip", "install", "-r", "requirements.txt", "--quiet"])
    print("Packages Installed.\nSee 'packages.txt' for a complete list\n-----------------")
    os.rename(os.path.join(cwd, 'requirements.txt'), os.path.join(cwd, 'packages.txt'))
    config(cwd)

## RUN CONFIG
def config(cwd):

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

    ## SET REFRESH MODE
    print('\n\nSet your Refresh Mode. This can be updated later by re-running the setup')
    set_refresh_mode(cwd)

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

## SET REFRESH MODE
def set_refresh_mode(cwd):
    changes = input('\n1. Scan for Changes\n2. Scan for Missing Metadata\n3. Replace all Metadata (leave images)\n4. Replaces all Images (leave metadata)\n5. Replace all Metadata and Images\n\nInput: ')
    try:
        if int(changes) == 1:
            change_refresh_mode(os.path.join(cwd, 'listen.py'), 9, "REFRESH_MODE = config.refresh_mode['default']")
        elif int(changes) == 2:
            change_refresh_mode(os.path.join(cwd, 'listen.py'), 9, "REFRESH_MODE = config.refresh_mode['missing']")
        elif int(changes) == 3:
            change_refresh_mode(os.path.join(cwd, 'listen.py'), 9, "REFRESH_MODE = config.refresh_mode['replace_metadata']")
        elif int(changes) == 4:
            change_refresh_mode(os.path.join(cwd, 'listen.py'), 9, "REFRESH_MODE = config.refresh_mode['replace_images']")
        elif int(changes) == 5:
            change_refresh_mode(os.path.join(cwd, 'listen.py'), 9, "REFRESH_MODE = config.refresh_mode['replace_all']")
        else:
            print('Invalid input!\nExiting...')
            sys.exit()
        print('\nRefresh Mode Updated!')
    except ValueError:
        print('\n\nInvalid input!\nExiting...')
        sys.exit()

## UPDATE REFRESH MODE
def change_refresh_mode(file_path, line_number, refresh_mode):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    if line_number < 1 or line_number > len(lines):
        print(f"Invalid line number: {line_number}")
        return

    lines[line_number - 1] = refresh_mode + '\n'

    with open(file_path, 'w') as file:
        file.writelines(lines)

## GET CURRENT DIR
cwd = os.getcwd()

## RUN INSTALL OR CONFIG
if os.path.isfile(os.path.join(cwd, 'requirements.txt')):
    install(cwd)
else:
    mode = input('1. Change Config\n2. Change Refresh Mode\n\nInput: ')
    try:
        if int(mode) == 1:
            config(cwd)
        elif int(mode) == 2:
            set_refresh_mode(cwd)
        else:
            print('Invalid input!\nExiting...')
            sys.exit()
    except ValueError:
        print('\n\nInvalid input!\nExiting...')
        sys.exit()