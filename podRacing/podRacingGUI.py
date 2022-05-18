#!/usr/bin/env python

##### IMPORTS ################
import sys, subprocess, warnings
import os, platform, requests, re, time
import pandas as pd
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QStatusBar, QWidget, QLabel, QLineEdit, QPushButton, QProgressBar, QMessageBox, QFileDialog, QVBoxLayout, QHBoxLayout, QCheckBox
from PyQt6.QtGui import QIcon, QCursor, QFont
from PyQt6.QtCore import Qt, QDir, QCoreApplication
from bs4 import BeautifulSoup
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
        self.episodes_list_file = self.appDir + "/episode_titles.txt"

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
        
        ## QUIT SECTION
        self.quitBtn = QPushButton('Quit')
        self.quitBtn.setFixedSize(60,32)
        self.quitBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.quitBtn.clicked.connect(self.quit)

        ## OUTPUT PATH
        self.outputBtn = QPushButton('📂 Save Directory')
        self.outputBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.outputBtn.setToolTip(self.appDir)
        self.outputBtn.clicked.connect(self.set_download_dir)
        self.outputBtn.setEnabled(False)

        ## FLOATING TOOLS
        self.option_overwrite = QCheckBox('Overwrite', self)
        self.option_overwrite.move(15, 255)
        self.option_overwrite.show()
        self.option_overwrite.setCursor(QCursor(Qt.CursorShape.DragCopyCursor))
        self.option_overwrite.setToolTip(
            "Overwrites existing episodes\n"
            "Default behavior is to skip an episode if it has already been downloaded")

        ## ADDITIONAL OPTIONS BAR
        self.additionalOptions = QStatusBar()

        ## MESSAGE BOX
        self.message = QMessageBox()

        ## ADDRESS BAR & FETCH BUTTON
        self.urlBox = QLineEdit()
        self.urlBox.setFixedSize(300, 33)
        self.urlBox.setPlaceholderText('Paste RSS Feed URL...')
        self.button = QPushButton('Fetch')
        self.button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        ## METADATA TAGS
        self.title = QLabel('Title')
        self.author = QLabel('Author')
        self.length = QLabel('Episode Count')
        self.publish_date = QLabel('Last Updated:')
        self.credit = QLabel('PODRacer | by Mike Afshari')
        self.credit.setStyleSheet('font-size: 11px; font-weight: bold;')

        ## DOWNLOAD PROGRESS BAR
        self.progress_bar = QProgressBar()
        
        ## DOWNLOAD BUTTON
        self.downloadBtn = QPushButton('Download')
        self.downloadBtn.setFixedSize(120,32)
        self.downloadBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
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
        downloadSec.addWidget(self.quitBtn)
        downloadBtn.addWidget(self.downloadBtn)
        downloadSec.addWidget(self.progress_bar)
        downloadSec.addSpacing(20)
        downloadSec.addLayout(downloadBtn)
        
        ## ADDITIONAL OPTIONS
        self.additionalOptions.setSizeGripEnabled(False)
        self.additionalOptions.addPermanentWidget(self.outputBtn)

        # add content to parent layout
        layout.addLayout(topBar)
        layout.addSpacing(5)
        layout.addLayout(detailSec)
        layout.addSpacing(5)
        layout.addLayout(downloadSec)
        layout.addSpacing(35)
        layout.addWidget(self.outputBtn)

    ## RETRIEVES RSS DATA FROM URL
    def fetch_RSS(self):

        ## GET RSS FEED
        rss_url = self.urlBox.text()
        if rss_url == '':
            print(self.urlBox.placeholderText())
        else:
            
            ## VALIDATE RSS FEED
            try: ## GOOD!
                QCoreApplication.processEvents()
                rss_feed = requests.get(rss_url)
                rss_data = BeautifulSoup(rss_feed.content, features="lxml")
            except Exception: ## BAD!
                self.urlBox.clear()
                self.urlBox.setPlaceholderText('Invalid URL!')
                return

            ## GET METADATA
            items = rss_data.findAll('item')
            show_title = rss_data.find('title').text
            try:
                show_author = rss_data.find('itunes:author').text
            except AttributeError:
                try:
                    show_author = self.shorten_text(rss_data.find('description').text, 50)
                except AttributeError:
                    self.reset_gui()
                    self.urlBox.clear()
                    self.urlBox.setPlaceholderText('Invalid URL!')
                    return
            latest_ep_date = rss_data.find('pubdate').text
            if '-' in latest_ep_date:
                latest_ep_date = rss_data.find('pubdate').text.split('-')[0]
            elif '+' in latest_ep_date:
                latest_ep_date = rss_data.find('pubdate').text.split('+')[0]

            ## REMOVE PREVIOUS TXT FILES AND CLEAR EPISODE TITLES / COUNT
            self.clear_RSS()
            self.episode_titles = []
            self.episode_count = 0

            ## EXPORT EPISODE DATA TO FILE
            rss_items = []
            for item in items:

                ## GET EPISODE TITLE & DESCRIPTION
                rss_item = {}
                rss_item['title'] = item.title.get_text(strip=False).replace('\n', '')
                self.episode_titles.append(rss_item['title'])
                self.episode_count = len(items)
                rss_item['title'] = item.title.get_text(strip=False).replace('\n', ' ')
                rss_item['description'] = item.description.text
                rss_item['description'] = self.clean_text(rss_item['description'], 'html')
                
                ## WRITE EPISODE TITLES TO FILE
                with open(self.episodes_list_file, "a+") as titlesText:
                    titlesText.write(rss_item['title'])
                    titlesText.write('\n')

                ## WRITE TO FILE
                with open(self.episodes_file, "a+") as episodesText:
                    episodesText.write('\n\n----------------------------------------------------------\n')
                    episodesText.write('\n//////////////////////////////////////////////////////////\n') ## EPISODE DIVIDER
                    episodesText.write('\n----------------------------------------------------------\n\n')
                    episodesText.write('############## EPISODE TITLE ##############\n\n')
                    episodesText.write(rss_item['title']) ## TITLE TEXT
                    episodesText.write('\n\n################ DESCRIPTION ##############\n\n')
                    episodesText.write(rss_item['description']) ## DESCRIPTION TEXT
                
                ## REMOVE '\n' FROM DESCRIPTION AND APPEND METADATA
                rss_item['description'] = rss_item['description'].replace('\n', ' ')
                rss_items.append(rss_item)

            ## GET AUDIO LINKS
            link_count = 0
            list_links = []
            for link in rss_data.findAll('enclosure'):
                list_links.append(link)
            with open(self.input_file, "w") as inputText:
                inputText.write(rss_data.prettify(formatter="html"))

            ## EXPORT AUDIO LINKS TO FILE
            for x in range(len(list_links)):
                link_count += 1
                dl_link = str(list_links[x]).split('url="')[1].split('">')[0]
                with open(self.links_file, "a+") as linksText:
                    linksText.write(dl_link + "\n")
            
            ## BUILD HTML
            rss_html = pd.DataFrame(rss_items, columns=['title', 'description'])
            rss_html.to_html(self.appDir + '/fetch.html',index=0, encoding='utf-8')
            self.build_html(rss_html)
            
            ## UPDATE GUI
            if show_title == '':
                show_title = 'Unknown'
            self.title.setText(f"{show_title}")
            if show_author == '':
                show_author = 'Unknown'
            self.author.setText(f"{show_author}")
            self.publish_date.setText(f"Last Updated: {latest_ep_date}")
            self.length.setText(f"Episodes: {link_count}")
            self.urlBox.clear()
            self.urlBox.setPlaceholderText('Paste RSS Feed URL...')
            self.outputBtn.setEnabled(True)

    ## BUILD HTML FROM FETCHED RSS
    def build_html(self, rss):
        pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>

        css_string = '''
/* includes alternating gray and white with on-hover color *
.mystyle {
    font-size: 11pt; 
    font-family: Arial;
    border-collapse: collapse; 
    border: 1px solid silver;

}

.mystyle td, th {
    padding: 5px;
}

.mystyle tr:nth-child(even) {
    background: #E0E0E0;
}

.mystyle tr:hover {
    background: silver;
    cursor: pointer;
}
'''

        html_string = '''
<html>
    <head>
        <title>PODRacing Export</title>
        <link rel="stylesheet" type="text/css" href="style.css"/>
        <style>
            #STYLING
        </style>
    </head>
    <body>
        {table}
    </body>
</html>
'''

        ## OUTPUT AN HTML FILE
        with open(self.appDir+ '/index.html', 'w') as htmlFile:
            htmlFile.write(html_string.format(table=rss.to_html(classes='mystyle')))
        
        ## OUTPUT A CSS FILE
        with open(self.appDir+ '/style.css', 'w') as cssFile:
            cssFile.write(css_string)

        return

    ## CLEAR RSS DATA
    def clear_RSS(self):
        if os.path.isfile(self.input_file):
            os.remove(self.input_file)
        if os.path.isfile(self.episodes_file):
            os.remove(self.episodes_file)
        if os.path.isfile(self.links_file):
            os.remove(self.links_file)
        if os.path.isfile(self.episodes_list_file):
            os.remove(self.episodes_list_file)
        return

    ## SET DOWNLOAD DIR
    def set_download_dir(self):
        # update the output path
        path = str(QFileDialog.getExistingDirectory(self, "Select Output Directory"))
        if path:
            self.appDir = path
            # update tooltip
            self.outputBtn.setToolTip(path)

    ## ENABLE DOWNLOAD BUTTON
    def enable_dl(self):
        self.downloadBtn.setEnabled(True)

    ## SHORTENS TEXT TO A SET LIMIT
    def shorten_text(self, text, length, suffix='...'):
        if len(text) <= length:
            return text
        else:
            return ' '.join(text[:length+1].split(' ')[0:-1]) + suffix

    ## REMOVE SPECIAL CHARACTERS FROM TEXT
    def clean_text(self, text, type):
        if type.lower() == 'html':
            clean = re.compile('<.*?>')
            return re.sub(clean, '', text).strip()
        if type.lower() == '_title':
            clean = re.sub(r"[^a-zA-Z0-9 ,*\u2019-]+"," ",text)
            return clean

    ## GENERATE DOWNLOAD LINK
    def generate_link(self, link):
        podtrac = 'www.podtrac.com/pts/redirect.mp3/'
        radiolab = 'radiolab_podcast'
        if podtrac in link:
            link = f"http://{link.split(podtrac)[-1]}"
        if radiolab in link:
            link = link.split('/radiolab_podcast/')[1]
            link = f"http://wnyc-origin-iad.streamguys1.com/radiolab_podcast/{link}"
            link = link.split('?')[0]
        return link

    ## DETECT AUDIO FORMAT
    def audio_format(self, file):
        self.format = file.split('.')[-1]
        self.format = re.sub(r"[^a-zA-Z0-9.]+","",self.format)
        return self.format

    ## DOWNLOAD PODCAST AUDIO
    def download_audio(self):

        ## INITIALIZE A COUNTER AND TOTAL
        count = 0
        skip_count = 0
        count_length = self.episode_count

        ## UPDATE GUI STATUS
        print(f"\nBeginning Download...\n\nEpisodes Found: {count_length}\n")
        QCoreApplication.processEvents()
        self.downloadBtn.setText('Downloading')
        self.urlBox.setPlaceholderText('Please Wait...')
        self.button.setDisabled(True)
        self.outputBtn.setEnabled(False)
        self.downloadBtn.setEnabled(False)

        ## REMOVE SPECIAL CHARACTERS FROM SHOW TITLE AND SET SHOW DIR
        show_title = self.title.text()
        show_title = self.clean_text(show_title, '_title')
        show_dir = (f"{self.appDir}/{show_title}")
        
        ## CREATE DOWNLOAD DIR WITH SHOW TITLE AS NAME
        if not os.path.isdir(show_dir):
            os.makedirs(show_dir)
        
        ## GET DL LINK FROM 'LINKS.TXT' FILE
        ## DOWNLOAD EACH FILE AND RENAME TO MATCH EPISODE NAME
        timer_start = time.perf_counter()
        with open(self.links_file) as linksText:
            for l_no, line in enumerate(linksText):

                ## SET PROGRESS BAR
                timer_add = time.perf_counter()
                QCoreApplication.processEvents()
                count_per = (count / count_length) * 100
                self.download_progress(count_per)

                ## GET EPISODE TITLE
                ## IF TITLE IS BLANK, TITLE THEM NUMERICALLY IN ASC. ORDER
                episode_title = self.episode_titles[l_no]
                if episode_title == '':
                    episode_title = f"Episode {l_no + 1}"
                
                ## GET DOWNLOAD LINK
                link = line
                link = self.generate_link(link)
                if not link.endswith('.mp3') or link.endswith('.wav') or link.endswith('.flac'):
                    link = link.split('?')[0]
                
                ## GET AUDIO FORMAT
                format = self.audio_format(link)

                ## DOWNLOAD AUDIO FILE WITH EPISODE NAME TO SHOW DIR
                r = requests.get(link, allow_redirects=True, stream=True)
                QCoreApplication.processEvents()

                ## OVERWRITE EXISTING DOWNLOADS
                if self.option_overwrite.isChecked():
                    if count < 1:
                        confirm_overwrite = QMessageBox.question(self, 'Warning', 'This will overwrite existing files\nDo you wish to continue?',
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
                    if confirm_overwrite == QMessageBox.StandardButton.Yes:
                        print(f"{episode_title}")
                        episode_title = self.clean_text(episode_title, '_title')
                        open(f"{show_dir}/{episode_title}.{format}", 'wb').write(r.content)
                        count += 1
                    else:
                        self.reset_gui()
                        return

                ## IF DOWNLOAD EXISTS, SKIP TO NEXT ONE (NO-OVERWRITING)
                else:
                    if not os.path.isfile(f"{show_dir}/{episode_title}.{format}"):
                        print(f"{episode_title}")
                        episode_title = self.clean_text(episode_title, '_title')
                        open(f"{show_dir}/{episode_title}.{format}", 'wb').write(r.content)
                        count += 1
                    else:
                        print(f"SKIPPED: [{episode_title}]")
                        count += 1
                        skip_count +=1

        ## WHEN DONE
        if count_length == self.episode_count:
            timer_duration_sec = (timer_add - timer_start)
            timer_duration_min = (timer_add - timer_start) / 60
            print('\nDownload Complete!\n')
            print(
                f"{count - skip_count}/{count_length} Files Downloaded | "
                f"{skip_count}/{count_length} Skipped | "
                f"Duration {int(timer_duration_min)} minutes and {timer_duration_sec:0.1f} seconds"
            )
            self.reset_gui()

    ## DOWNLOAD PROGRESS
    def download_progress(self, per):
        # update progress bar
        self.progress_bar.setValue(int(per))
        # adjust the font color to maintain the contrast
        self.progress_bar.setStyleSheet('QProgressBar { color: #fff }')
            
    ## DOWNLOAD COMPLETE
    def download_complete(self, location):
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
    
    ## RESET DEFAULT GUI PARAMETERS
    def reset_gui(self):
        
        ## ACTIVATE 'FETCH' AND 'DIRECTORY' BUTTONS
        self.button.setEnabled(True)
        self.outputBtn.setEnabled(False)
        self.button.setText('Fetch')
        self.urlBox.setPlaceholderText('Paste RSS Feed URL...')

        ## DE-ACTIVATE 'DOWNLOAD' BUTTON
        self.downloadBtn.setDisabled(True)
        self.downloadBtn.setText('Download')

        ## DOWNLOAD STATUS
        self.isDownloading = False

        ## RESET PROGRESS BAR
        self.progress_bar.reset()

    ## QUIT APPLICATION
    def quit(self):
        sys.exit()

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