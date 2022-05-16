#!/usr/bin/env python

##### IMPORTS ################
import sys, subprocess, warnings
import os, platform, requests, re
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QStatusBar, QWidget, QLabel, QLineEdit, QPushButton, QProgressBar, QComboBox, QMessageBox, QFileDialog, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QIcon, QCursor, QFont
from PyQt6.QtCore import Qt, QDir, QCoreApplication
from bs4 import BeautifulSoup
from datetime import timedelta
##### Dismiss the 'XML' warning
warnings.filterwarnings("ignore", 
category=UserWarning, module='bs4')
#############################

##### INFORMATION ##########

## Takes an RSS feed url as input
## Returns metadata in readable format

###### Created by need4swede
###### Portfolio: https://mafshari.work/
###### GitHub: https://github.com/need4swede
############################################

## GUI
class PodRacingGUI(QWidget):
    def __init__(self):
        super().__init__()
        # setup some flags
        self.isFetching = False
        self.isDownloading = False
        self.setFont(QFont('Helvetica'))

        self.episode_titles = []
        self.episode_count = 0

        ## APPLICATION DIRECTORY
        self.appDir = f'{QDir.homePath()}/podRacing'
        self.input_file = self.appDir + "/input.txt"
        self.output_file = self.appDir + "/output.txt"
        self.links_file = self.appDir + "/links.txt"
        self.episodes_file = self.appDir + "/episodes.txt"

        # setup some window specific things
        self.setWindowTitle('Podcast Obtainable Data Racer')
        self.setWindowIcon(QIcon('icon.ico'))

        # parent layout
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 10)
        self.setLayout(layout)

        # top bar layout
        topBar = QHBoxLayout()

        # detail section
        detailSec = QHBoxLayout()
        metaSec = QVBoxLayout()

        # download section
        downloadSec = QHBoxLayout()
        downloadBtn = QVBoxLayout()

        ## OUTPUT PATH
        self.outputBtn = QPushButton('📂  Save to...')
        self.outputBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.outputBtn.setToolTip(self.appDir)
        self.outputBtn.clicked.connect(self.setOutputPath)

        # status bar
        self.statusBar = QStatusBar()

        # message box
        self.message = QMessageBox()

        ## ADDRESS BAR & FETCH BUTTON
        self.urlBox = QLineEdit()
        self.urlBox.setPlaceholderText('Paste RSS Feed URL...')
        self.button = QPushButton('Fetch')
        self.button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        # self.button.clicked.connect(podRacing.main)

        ## METADATA TAGS
        self.title = QLabel('Title')
        self.author = QLabel('Author')
        self.length = QLabel('Episode Count')
        self.publish_date = QLabel('Last Updated')
        self.credit = QLabel('PODRacer | by Mike Afshari')
        self.credit.setStyleSheet('font-size: 11px; font-weight: bold;')

        # progress bar
        self.progress_bar = QProgressBar()
        
        # # download options
        self.downloadBtn = QPushButton('Download')
        # self.download = QComboBox()
        # self.download.setPlaceholderText('Download')
        self.downloadBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        # self.download.activated.connect(self.download_audio)
        self.downloadBtn.setEnabled(False)
        self.downloadBtn.clicked.connect(self.download_audio)
        self.button.clicked.connect(self.enable_dl)
        self.button.clicked.connect(self.fetch_RSS)

        # add widgets and layouts
        topBar.addWidget(self.urlBox)
        topBar.addWidget(self.button)

        # detail section
        metaSec.addWidget(self.title)
        metaSec.addWidget(self.author)
        metaSec.addWidget(self.length)
        metaSec.addWidget(self.publish_date)
        metaSec.addSpacing(10)
        metaSec.addWidget(self.credit)
        detailSec.addLayout(metaSec)

        # download section
        downloadBtn.addWidget(self.downloadBtn)
        downloadSec.addWidget(self.progress_bar)
        downloadSec.addSpacing(20)
        downloadSec.addLayout(downloadBtn)

        # status bar
        self.statusBar.setSizeGripEnabled(False)
        self.statusBar.addPermanentWidget(self.outputBtn)

        # add content to parent layout
        layout.addLayout(topBar)
        layout.addSpacing(20)
        layout.addLayout(detailSec)
        layout.addSpacing(5)
        layout.addLayout(downloadSec)
        layout.addWidget(self.statusBar)

    def enable_dl(self):
        self.downloadBtn.setEnabled(True)

    # set output path slot
    def setOutputPath(self):
        # update the output path
        path = str(QFileDialog.getExistingDirectory(self, "Select Output Directory"))
        if path:
            self.appDir = path
            # update tooltip
            self.outputBtn.setToolTip(path)

    # finished slot
    def finished_slot(self):
        # remove progress bar busy indication
        self.progress_bar.setRange(0, 100)
        # unset fetching flag
        self.isFetching = False

    # download finished slot
    def download_finished_slot(self):
        # set back the button text
        self.button.setText('Fetch')
        # now enable the download options
        self.downloadBtn.setDisabled(False)
        # unset downloading flag
        self.isDownloading = False
        # reset pogress bar
        self.progress_bar.reset()

    # download response slot
    def download_response_slot(self, per):
        # update progress bar
        self.progress_bar.setValue(per)
        # adjust the font color to maintain the contrast
        if per > 89:
            self.progress_bar.setStyleSheet('QProgressBar { color: #28ab00 }')
        else:
            self.progress_bar.setStyleSheet('QProgressBar { color: #fff }')
    
    # download complete slot
    def download_complete_slot(self, location):
        # use native separators
        location = QDir.toNativeSeparators(location)
        # show the success message
        if self.message.information(
            self,
            'Downloaded',
            f'Download complete!\nFile was successfully downloaded to :\n{location}\n\nOpen the downloaded file now ?',
            QMessageBox.StandardButtons.Open,
            QMessageBox.StandardButtons.Cancel
        ) is QMessageBox.StandardButtons.Open: subprocess.Popen(f'explorer /select,{location}')
    
    def remove_html_tags(self, text):
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    ##### FETCH RSS
    ## Retrieves RSS data from URL
    def fetch_RSS(self):
        rss_url = self.urlBox.text()
        if rss_url == '':
            print(self.urlBox.placeholderText())
        else:
            try:
                QCoreApplication.processEvents()
                rss_feed = requests.get(rss_url)
                rss_data = BeautifulSoup(rss_feed.content, features="lxml")
            except Exception:
                self.urlBox.clear()
                self.urlBox.setPlaceholderText('Invalid URL!')
                return
            
            ## REMOVE PREVIOUS TXT FILES
            if os.path.isfile(self.episodes_file):
                os.remove(self.episodes_file)
            if os.path.isfile(self.links_file):
                os.remove(self.links_file)

            ## SHOW METADATA
            items = rss_data.findAll('item')
            show_title = rss_data.find('title').text
            show_author = rss_data.find('itunes:author').text
            latest_ep_date = rss_data.find('pubdate').text.split('-')[0]
            self.title.setText(f"{show_title}")
            self.author.setText(f"{show_author}")
            self.publish_date.setText(f"{latest_ep_date}")

            rss_items = []
            # cleanRSS = self.remove_html_tags(rss_data.text)
            
            
            for item in items:
                rss_item = {}
                rss_item['title'] = item.title.get_text(strip=False).replace('\n', '')
                self.episode_titles.append(rss_item['title'])
                self.episode_count = len(items)
                rss_item['title'] = item.title.get_text(strip=False).replace('\n', ' ')
                rss_item['description'] = item.description.text
                rss_item['description'] = self.remove_html_tags(rss_item['description'])
                
                with open(self.episodes_file, "a+") as episodesText:
                    episodesText.write('\n\n----------------------------------------------------------\n')
                    episodesText.write('\n//////////////////////////////////////////////////////////\n') ## EPISODE DIVIDER
                    episodesText.write('\n----------------------------------------------------------\n\n')
                    episodesText.write('############## EPISODE TITLE ##############\n\n')
                    episodesText.write(rss_item['title']) ## TITLE TEXT
                    episodesText.write('\n\n################ DESCRIPTION ##############\n\n')
                    episodesText.write(rss_item['description']) ## DESCRIPTION TEXT
                rss_items.append(rss_item)

            ##### LINKS
            list_links = []
            for link in rss_data.findAll('enclosure'):
                list_links.append(link)
            with open(self.input_file, "w") as inputText:
                inputText.write(rss_data.prettify(formatter="html"))

            link_count = 0
            

            for x in range(len(list_links)):
                link_count += 1
                dl_link = str(list_links[x]).split('url="')[1].split('">')[0]
                with open(self.links_file, "a+") as linksText:
                    linksText.write(dl_link + "\n")
                


            self.length.setText(f"Episodes: {link_count}")
            self.urlBox.clear()
            self.urlBox.setPlaceholderText('Paste RSS Feed URL...')

    ##### DOWNLOAD PODCAST
    ## Retrieves audio files from RSS data
    def download_audio(self):

        ## INITIALIZE A COUNTER AND TOTAL
        count = 0
        count_length = self.episode_count

        ## REMOVE SPECIAL CHARACTERS FROM SHOW TITLE AND SET SHOW DIR
        QCoreApplication.processEvents()
        self.downloadBtn.setEnabled(False)
        show_title = self.title.text()
        show_title = re.sub(r"[^a-zA-Z0-9]+"," ",show_title)
        show_dir = (f"{self.appDir}/{show_title}")
        
        ## CREATE DOWNLOAD DIR WITH SHOW TITLE AS NAME
        if not os.path.isdir(show_dir):
            os.makedirs(show_dir)
        
        ## GET DL LINK FROM 'LINKS.TXT' FILE
        ## DOWNLOAD EACH FILE AND RENAME TO MATCH EPISODE NAME
        with open(self.links_file) as linksText:
            for l_no, line in enumerate(linksText):

                ## SET PROGRESS BAR
                QCoreApplication.processEvents()
                count_per = (count / count_length) * 100
                self.download_response_slot(count_per)

                ## GET EPISODE TITLE
                ## IF TITLE IS BLANK, TITLE THEM NUMERICALLY IN ASC. ORDER
                episode_title = self.episode_titles[l_no]
                if episode_title == '':
                    episode_title = f"Episode {l_no + 1}"
                
                ## GET DL LINK AND REMOVE TEXT AFTER AUDIO FORMAT
                link = line
                if not link.endswith('.mp3') or link.endswith('.wav') or link.endswith('.flac'):
                    link = link.split('?')[0]
                
                ## GETS AUDIO FORMAT
                format = link.split('.')[-1]
                format = re.sub(r"[^a-zA-Z0-9.]+","",format)

                ## DOWNLOAD AUDIO FILE WITH EPISODE NAME TO SHOW DIR
                r = requests.get(link, allow_redirects=True, stream=True)
                QCoreApplication.processEvents()
                open(f"{show_dir}/{episode_title}.{format}", 'wb').write(r.content)
                count += 1
                
        
        ## WHEN DONE
        if count_length == self.episode_count:
            self.download_finished_slot()
            self.finished_slot()

## APP
class PodRacingApp(PodRacingGUI):
    def __init__(self, directory):
        self.directory = directory
        self.appDir = self.directory[0]
        self.input_file = self.directory[1]
        self.output_file = self.directory[2]
        self.links_file = self.directory[3]
    
    ##### DIRECTORY
    ## Initializes the working directory
    def create_appDir(self):
        if not os.path.isdir(self.appDir):
            os.makedirs(self.appDir)
        if os.path.isfile(self.links_file):
            # print("Existing 'links.txt' file found!\n" 
            #     "Running the tool again will overwrite it\n")
            # confirm = input("Confirm overwriting current 'links' file?\nY/N : ")
            # if confirm.lower() == 'Y'.lower():
            #     os.remove(self.links_file)
            # else:
            #     sys.exit()
            os.remove(self.links_file)
        if not os.path.isfile(self.input_file):
            with open(self.input_file, 'w', encoding="utf8") as inputText:
                inputText.write('')
                inputText.close()
        
    ##### LIST DIRECTORY
    ## Prints a list of the application's files and directories
    def list(self, arg):
        if 'dir' in arg:
            print(f"App Directory: {self.appDir}\n"
                    f"Input File: {self.input_file}\n"
                    f"Output File: {self.output_file}\n"
                    f"Links File: {self.links_file}\n")
        else:
            print('Undefined argument')
    
    ##### CLEAR TERMINAL
    ## Clears the terminal window based on OS platform
    def clear(self):
        if platform.system() == "Windows":
                clear = lambda: os.system('cls')
                clear()
                print()
        if platform.system() == "Darwin":
                os.system("clear")
                print()

    ##### HELP ME
    ## Prints application instructions to the terminal
    def help(self):
        self.clear()
        instructions = ["0. Run podRacing.py once to create 'input.txt' file (ignore if it's there)",
                        "1. Paste the RSS header data into the 'input.txt' file and save the file",
                        "2. Run podRacing.py",
                        "3. Open 'links.txt' to view results"
                        ]
        for x in range(len(instructions)):
            print(instructions[x])

    ##### ERROR HANDLING
    ## Error Message Outputs
    def errors(self, arg):
        self.clear()
        if "no input" in arg:
            print("Paste your RSS header into 'input.txt' and run the tool again")
        elif "input empty" in arg:
            print("Your 'input.txt' file is empty!\n" 
                    "Please enter some data first and run the tool again")
        sys.exit()

    ##### COUNTER
    ## Counts episode numbers and links
    def counter(self, type, count):
            counter = 0
            if type == 'show':
                return
            if type == 'episode':
                for x in range(count):
                    counter += 1
            print(counter)
            return
    
    ##### FETCH LINKS VIA INPUT FILE
    ## Parses through RSS header and gets links based on 'enclosure url=' tags inside 'input.txt'
    def fetch_links(self):

        ## Parameters
        count = 0
        link_tag = "enclosure url="
        
        if os.path.getsize(self.input_file) < 1:
            self.errors('no input')
        
        ## If an existing output is found, just count the episodes - but don't write to the file
        if os.path.isfile(self.output_file):
            with open(self.input_file, 'r') as inputText:
                for l_no, line in enumerate(inputText):
                    if link_tag in line:
                        count = count + 1
                print('\nEpisode Count:', count)
                inputText.close()
            return

        ## If no existing output is found, count the episodes - and write the link tags to the file
        with open(self.input_file, 'r', encoding="utf8") as inputText:
            for l_no, line in enumerate(inputText):
                if link_tag in line:
                    count = count + 1
                    links = line.split(link_tag + '"')[1].split('"')[0]
                    with open(self.output_file, 'a') as output:
                        output.write(links + "\n")
            print('\nEpisode Count:', count)

## RUN
if __name__ == '__main__':
    
    ## ARGS
    def init():
        home_directory = str(Path.home()) # USER HOME DIR
        app_directory = home_directory + '/podRacing' # APPLICATION DIR
        file_input = app_directory + '/input.txt' # INPUT FILE
        file_output = app_directory + '/output.txt' # OUTPUT FILE
        file_links = app_directory + '/links.txt' # LINKS FILE
        return [app_directory, file_input, file_output, file_links] # APPLICATION INIT ARGS
    
    # instantiate the application
    app = QApplication(sys.argv)
    # setup a custom styleSheet
    app.setStyleSheet('''
        * {
            background-color: #333;
        }
        QWidget {
            font-size: 15px;
            border-radius: 4px;
        }
        QLabel {
            font-family: 'Sans Serif';
        }
        QToolTip {
            padding: 4px; 
            border: 1px solid #bababa;
        }
        QStatusBar {
            font-size: 13px;
        }
        QStatusBar QPushButton {
            background-color: none;
            padding: 0 40px;
            color: #fff;
        }
        QStatusBar QPushButton:hover {
            background-color: none;
            color: #0078d4;
        }
        QLineEdit {
            padding: 4px 10px;
            margin-right: 10px;
            border: 2px solid #bababa;
            font-size: 16px;
            selection-background-color: #0078d4;
        }
        QLineEdit:hover {
            border-color: #808080;
        }
        QLineEdit:focus {
            border-color: #0078d4;
        }
        QMenu {
            border: 1px solid #bababa;
            padding: 5px;
        }
        QMenu::item {
            padding: 3px 25px;
            border-radius: 4px; 
        }
        QMenu::item:selected {
            color: #fff;
            background-color: #0078d4;
        }
        QPushButton {
            width: 125px;
            padding: 7px 0;
            color: #fff;
            border: none;
            background-color: #0078d4;
        }
        QPushButton:hover, QComboBox:hover {
            background-color: #00599d;
        }
        QPushButton:pressed, QComboBox:pressed {
            background-color: #00477c;
        }
        QPushButton:disabled, QComboBox:disabled {
            background-color: #77b7e9;
        }
        QComboBox {
            padding: 5.5px 30px 5.5px 45px;
            color: #fff;
            border: none;
            background-color: #0078d4;
        }
        QComboBox::drop-down {
            border-radius: 0;
        }
        QComboBox:on {
            border-bottom-left-radius: 0;
            border-bottom-right-radius: 0;
        }
        QComboBox QAbstractItemView {
            border-radius: 0;
            outline: 0;
        }
        QComboBox QAbstractItemView::item {
            height: 33px;
            padding-left: 42px;
            background-color: #fff;
        }
        QComboBox QAbstractItemView::item:selected {
            background-color: #0078d4;
        }
        QProgressBar {
            text-align: center;
        }
        QProgressBar::chunk {
            background: #0078d4;
            border-radius: 4px;
        }
        QMessageBox QLabel {
            font-size: 13px;
        }
        QMessageBox QPushButton {
            width: 50px;
            padding: 6px 25px;
        }
    ''')
    
    podRacingGUI = PodRacingGUI()
    podRacingGUI.show()
    
    podRacing = PodRacingApp(init())
    podRacing.clear()
    podRacing.create_appDir()
    

    sys.exit(app.exec())