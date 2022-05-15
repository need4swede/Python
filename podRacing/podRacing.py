#!/usr/bin/env python

##### IMPORTS ################
import os, sys, platform
from pathlib import Path
#############################

##### INFORMATION ##########

## Takes an RSS header as input and returns a 
## list of links to download the assets

###### Created by need4swede
###### Portfolio: https://mafshari.work/
###### GitHub: https://github.com/need4swede
############################################

##### INSTRUCTIONS ##########

## 0. Run podRacing.py once to create 'input.txt' file (ignore if it's there)
## 1. Paste the RSS header data into the 'input.txt' file and save the file
## 2. Run podRacing.py
## 3. Open 'links.txt' to view results

############################

##### COUNTER
## Sums the total count of episodes founds
episodes = 0

##### DIRECTORY
## Initializes a working directory, comprised of 'input.txt' and 'output.txt' files
appDir = str(Path.home()) + '/podRacing'
def create_appDir():
    if not os.path.isdir(appDir):
        os.makedirs(appDir)
    if os.path.isfile(appDir + "/links.txt"):
        print("Existing 'links.txt' file found!\n" 
            "Running the tool again will overwrite it\n")
        confirm = input("Confirm overwriting current 'links' file?\nY/N : ")
        if confirm.lower() == 'Y'.lower():
            os.remove(appDir + "/links.txt")
        else:
            sys.exit()
    if not os.path.isfile(appDir + "/input.txt"):
        with open(appDir + "/input.txt", 'w', encoding="utf8") as inputText:
            inputText.write('')
            inputText.close()
            errors('no input')

##### ERROR HANDLING
## Error Message Outputs
def errors(arg):
    clear_term()
    if "no input" in arg:
        print("Paste your RSS header into 'input.txt' and run the tool again")
    elif "input empty" in arg:
        print("Your 'input.txt' file is empty!\n" 
                "Please enter some data first and run the tool again")
    sys.exit()

##### FETCH LINKS
## Parses through RSS header and gets links based on 'enclosure url=' tags
def fetch_links():

    ## Parameters
    count = 0
    link_tag = "enclosure url="

    ## If an existing output is found, just count the episodes - but don't write to the file
    if os.path.isfile(appDir + "/output.txt"):
        with open(appDir + "/input.txt", 'r') as inputText:
            for l_no, line in enumerate(inputText):
                if link_tag in line:
                    count = count + 1
            print('\nEpisode Count:', count)
            inputText.close()
        return

    ## If no existing output is found, count the episodes - and write the link tags to the file
    with open(appDir + "/input.txt", 'r', encoding="utf8") as inputText:
        for l_no, line in enumerate(inputText):
            if link_tag in line:
                count = count + 1
                links = line.split(link_tag + '"')[1].split('"')[0]
                with open(appDir + "/output.txt", 'a') as output:
                    output.write(links + "\n")
        print('\nEpisode Count:', count)

##### FETCH TITLES
## Parses through RSS header and gets episode titles based on 'title' tags
def fetch_titles():

    ## Parameters
    count = 0
    link_tag = "enclosure url="
    title_tag = "<title>"
    show_title = ''
    episode_title = ''

    with open(appDir + "/input.txt", 'r', encoding="utf8") as inputText:
        for l_no, line in enumerate(inputText):
            if title_tag in line:
                if l_no < 6:
                    show_title = line.split(title_tag)[1].split('</title>')[0].strip()
                    filename = ''.join(filter(str.isalnum, show_title))
                    if os.path.isfile(appDir + f"/metadata_{filename}.txt"):
                        os.remove(appDir + f"/metadata_{filename}.txt")
                    with open(appDir + f"/metadata_{filename}.txt", 'a+') as metadataText:
                        metadataText.write(f"Show Title\n-\n{show_title}\n-\n")
                else:
                    episode_title = line.split(title_tag)[1].split('</title>')[0].strip()
                    if not episode_title == show_title:
                        count = count + 1
                        with open(appDir + f"/metadata_{filename}.txt", 'a+') as metadataText:
                            metadataText.write(f"\nEpisode No: {count}\n" + f"-\n{episode_title}\n-\n")

##### AMEND LINKS
## Cleans up the link to avoid redirects and unecessary tags
def amend_links():

    ## Fetch the links from RSS header in 'input.txt'
    fetch_links()

    ## Fetch the episode names from RSS header in 'input.txt'
    fetch_titles()

    ## Parameters
    https = "https://"
    http = "http://"
    redirect = '/redirect.mp3/'
    mp3 = '.mp3?'
    count = 0

    ## Amend the links retrieved from the RSS header
    ## Removes unecessary prefixes/suffixes from links
    ## Counts the number of links that needed to be amended
    ## Saves data into a newfile called 'links.txt'
    try:
        with open(appDir + "/output.txt", "r") as outputText:
            for l_no, line in enumerate(outputText):
                if redirect in line:
                    count = count + 1
                    links = line.split(redirect)[1].split("&")[0]
                    with open(appDir + "/links.txt", "a+") as linkText:
                        if http in line:
                            linkText.write(links.strip() + "\n")
                        else:
                            linkText.write(http + links.strip() + "\n")
                elif mp3 in line:
                    links = line.strip()
                    if http or https in links:
                        count = count + 1
                        links = links.split("://")[1]
                    with open(appDir + "/links.txt", "a+") as linkText:
                        linkText.write(http + links.strip() + "\n")
    except FileNotFoundError:
        errors('input empty')
    print(f"Links Amended: {count}")

##### COUNT LINKS
## Counts total number of links currently stored in 'links.txt'
def count_links():

    ## Parameters
    linkCount = 0

    ## Count links
    if os.path.isfile(appDir + "/links.txt"):
        with open(appDir + "/links.txt", "r") as linksText:
            for l_no, line in enumerate(linksText):
                linkCount = l_no + 1
            print("Saved Links Count:", linkCount)

##### CLEAN UP
## Removes temporary output file and clears 'input.txt' text content
def clean_appDir():

    ## Remove 'output.txt'
    if os.path.isfile(appDir + "/output.txt"):
        os.remove(appDir + "/output.txt")

    ## Reset 'input.txt'
    with open(appDir + "/input.txt", "w") as inputText:
        inputText.write('')

##### CLEAR TERMINAL
## Clears the terminal window based on OS platform
def clear_term():
        if platform.system() == "Windows":
                clear = lambda: os.system('cls')
                clear()
                print()
        if platform.system() == "Darwin":
                os.system("clear")
                print()

def main():
    ######### WORKFLOW #####
    clear_term()          ## CLEARS THE TERMINAL
    create_appDir()       ## CREATES APP DIRECTORIES & FILES
    amend_links()         ## FETCHES LINKS AND AMENDS THEM IF NEEDED
    clean_appDir()        ## CLEARS TEMP FILES AND RESETS INPUT PARAMS
    count_links()         ## COUNTS THE TOTAL AMOUNT OF LINKS CURRENTLY STORED
    ########################