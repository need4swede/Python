##### IMPORTS ################
import sys, subprocess, warnings
import os, platform, requests, re, time, base64, shutil
import pandas as pd
from pathlib import Path
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QStatusBar, QWidget, QLabel, QLineEdit, QPushButton, QProgressBar, QMessageBox, QFileDialog, QVBoxLayout, QHBoxLayout, QCheckBox
from PyQt6.QtGui import QIcon, QCursor, QFont
from PyQt6.QtCore import Qt, QDir, QCoreApplication, QObject, QRunnable, pyqtSlot, QThreadPool
from bs4 import BeautifulSoup
##### Dismiss the 'XML' warning
warnings.filterwarnings("ignore", 
category=UserWarning, module='bs4')
#############################

##### TODO

### MAKE QUIT = STOP DOWNLOAD WHILE DOWNLOAD == TRUE ; ELSE QUIT = SYS.EXIT() AND FILE DELETION
# LINE 595

### FIXED PROGRESS BAR TO EMIT SIGNAL DURING DOWNLOAD
# LINE 650

## RSS FEED SAMPLES
# https://rss.art19.com/apology-line
# http://rss.art19.com/the-daily
# https://feeds.fireside.fm/bibleinayear/rss

############################################

class WorkerSignals(QObject):
    finished = QtCore.pyqtSignal() # create a signal
    result = QtCore.pyqtSignal(object) # create a signal that gets an object as argument

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn # Get the function passed in
        self.args = args # Get the arguments passed in
        self.kwargs = kwargs # Get the keyward arguments passed in
        self.signals = WorkerSignals() # Create a signal class

    @pyqtSlot()
    def run(self): # our thread's worker function
        result = self.fn(*self.args, **self.kwargs) # execute the passed in function with its arguments
        self.signals.result.emit(result)  # return result
        self.signals.finished.emit()  # emit when thread ended

## GUI
class PodRacingGUI(QWidget):
    def __init__(self, *args, **kwargs):
        super(QWidget, self).__init__(*args, **kwargs)
        self.threadpool = QThreadPool() 
        # setup some flags
        self.isFetching = False
        self.isDownloading = False

        self.episode_titles = []
        self.episode_count = 0
        self.download_count = 1

        ## APPLICATION DIRECTORY
        self.appDir = f'{QDir.homePath()}/podRacing'
        self.input_file = self.appDir + "/input.txt"
        self.output_file = self.appDir + "/output.txt"
        self.links_file = self.appDir + "/links.txt"
        self.episodes_file = self.appDir + "/episodes.txt"
        self.episodes_list_file = self.appDir + "/episode_titles.txt"

        # setup some window specific things
        self.setWindowTitle('podRacer - RSS Data Parser')
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
        self.option_overwrite.move(15, 215)
        self.option_overwrite.hide()
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
        self.credit = QLabel('podRacer | by Mike Afshari')
        self.version = QLabel('Version 0.8 Beta')
        self.version.setToolTip(f"{self.version.text().replace('Version ', 'v').replace(' Beta', '')} changes:"
            "\n- Fixed 'Not Responding' bug during downloads"
            "\n- Downloads are now passed through a secondary thread process"
            )
        self.credit.setStyleSheet('font-size: 11px; font-weight: bold;')
        self.version.setStyleSheet('''
            font-size: 10px; 
            background: none; 
            text-align: left; 
            padding: 0; 
            width: 2px;
            ''')

        ## DOWNLOAD PROGRESS BAR
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        
        ## DOWNLOAD BUTTON
        self.downloadBtn = QPushButton('Download')
        self.downloadBtn.setFixedSize(120,32)
        self.downloadBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.downloadBtn.setEnabled(False)
        # self.btn_thread.pressed.connect(self.threadRunner)
        self.downloadBtn.clicked.connect(self.threadRunner)
        self.button.clicked.connect(self.enable_dl)
        self.button.clicked.connect(self.fetch_RSS)

        # add widgets and layouts
        topBar.addWidget(self.urlBox)
        topBar.addWidget(self.quitBtn)
        topBar.addWidget(self.button)

        # detail section
        metaSec.addWidget(self.title)
        metaSec.addWidget(self.author)
        metaSec.addWidget(self.length)
        metaSec.addWidget(self.publish_date)
        metaSec.addSpacing(10)
        metaSec.addWidget(self.credit)
        metaSec.addWidget(self.version)
        detailSec.addLayout(metaSec)

        # download section
        downloadBtn.addWidget(self.downloadBtn)
        downloadSec.addWidget(self.progress_bar)
        # downloadSec.addSpacing(20)
        downloadSec.addLayout(downloadBtn)
        
        ## ADDITIONAL OPTIONS
        self.additionalOptions.setSizeGripEnabled(False)
        self.additionalOptions.addPermanentWidget(self.outputBtn)

        # add content to parent layout
        layout.addLayout(topBar)
        layout.addSpacing(5)
        layout.addLayout(detailSec)
        layout.addSpacing(20)
        layout.addLayout(downloadSec)
        # layout.addSpacing(35)
        layout.addWidget(self.outputBtn)

    def thread_finished(self):
        print("Finished signal emited.")
        self.urlBox.setPlaceholderText("Done!")
        try:
            self.download_complete(SHOW_title, SHOW_dir)
        except Exception:
            print("\nNOPE")
            pass
        self.reset_gui()

        # we'll use this function when 'result' signal is emited
    def thread_result(self, s):
        # add a label to layout
        pass
        # add a new label to window with the returned result from our thread

    def threadRunner(self):
        self.worker = Worker(self.download_audio) # create our thread and give it a function as argument with its args
        self.worker_progress = Worker(self.download_progress)
        self.worker.signals.result.connect(self.thread_result) # connect result signal of our thread to thread_result
        self.worker.signals.finished.connect(self.thread_finished) # connect finish signal of our thread to thread_complete
        self.threadpool.start(self.worker) # start thread
        self.threadpool.start(self.worker_progress)

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
                rss_feed = PodRacingApp.fetch_rss(PodRacingApp, rss_url)
                rss_data = BeautifulSoup(rss_feed.content, features="lxml")
            except Exception: ## BAD!
                self.urlBox.clear()
                self.urlBox.setPlaceholderText('Invalid URL!')
                return

            ## GET METADATA
            items = rss_data.findAll('item')
            show_title = rss_data.find('title').text
            global SHOW_title
            SHOW_title = show_title
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

            ## CREATE SHOW DIRECTORY
            show_dir = f"{self.appDir}/{self.clean_text(show_title, '_title')}"
            if not os.path.isdir(show_dir):
                os.makedirs(show_dir)
            global SHOW_dir
            SHOW_dir = show_dir
            ## EXPORT EPISODE DATA TO FILE
            rss_items = []
            for item in items:

                ## GET EPISODE TITLE & DESCRIPTION
                rss_item = {}
                rss_item['title'] = item.title.get_text(strip=False).replace('\n', '')
                self.episode_titles.append(rss_item['title'])
                self.episode_count = len(items)
                rss_item['title'] = item.title.get_text(strip=False).replace('\n', ' ').replace('\r', '')
                rss_item['description'] = item.description.text.replace('\r', '')
                rss_item['description'] = self.clean_text(rss_item['description'], 'html')
                rss_item['pubdate'] = item.pubdate.text.split(',')[1]
                if '-' in rss_item['pubdate']:
                    rss_item['pubdate'] = rss_item['pubdate'].split('-')[0][:13]
                elif '+' in rss_item['pubdate']:
                    rss_item['pubdate'] = rss_item['pubdate'].split('+')[0][:13]
                
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
            rss_html = pd.DataFrame(rss_items, columns=['title', 'pubdate', 'description'])
            rss_html.index +=1
            rss_html.index = rss_html.index.values[::-1]
            self.build_html(rss_html, self.clean_text(show_title, '_title'), show_dir)
            
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
            self.downloadBtn.show()
            self.option_overwrite.show()

            ## COPY TXT FILES TO SHOW METADATA FOLDER
            show_title = self.clean_text(show_title, '_title').lower().replace(' ', '')
            shutil.copy(self.episodes_file, f"{show_dir}/metadata/{show_title}_episodes.txt")
            shutil.copy(self.episodes_list_file, f"{show_dir}/metadata/{show_title}_episode_titles.txt")
            shutil.copy(self.links_file, f"{show_dir}/metadata/{show_title}_links.txt")

    ## BUILD HTML FROM FETCHED RSS
    def build_html(self, rss, title, directory):

        title = title.lower().replace(' ', '')
        directory = f"{directory}/metadata"
        if not os.path.isdir(directory):
            os.makedirs(directory)
        if not os.path.isdir(f"{directory}/assets"):
            os.makedirs(f"{directory}/assets")

        pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>

        js_string = "const header = document.querySelector('tr');const columns = header.children;columns[0].innerText = 'EPISODE ORDER';let title = columns[1].innerText.toUpperCase();title = title.replace('TITLE', 'EPISODE TITLE');columns[1].innerText = title;columns[2].innerText = columns[2].innerText.toUpperCase();description = columns[3].innerText.toUpperCase();description = description.replace('DESCRIPTION', 'EPISODE DESCRIPTION');columns[3].innerText = description;"

        dark_theme_css = '''
body {
    background: black;
    text-align: center;
}
.podracing-style-dark {
    font-size: 11pt; 
    font-family: 'Sans Sarif';
    border-collapse: collapse; 
    border: 1px solid silver;
    background: #19191a;
    color: #ededed;
}
.podracing-style-dark td, th {
    font-family: 'PT Sans', sans-serif;
    font-weight: 700;
    padding: 25px 15px;
    margin: 10px;
    text-align: center;
}
.podracing-style-dark td + td {
    font-weight: 400;
    text-align: left;
}
.podracing-style-dark tr:nth-child(even) {
    background: #2b2b2b;
}
.podracing-style-dark tr:hover {
    background: black;
    color: white;
    cursor: pointer;
}
'''

        html_string = '''
<html>
    <head>
        <title>PODRacing Export</title>
        <link rel="stylesheet" type="text/css" href="assets/style.css"/>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@600&family=PT+Sans:wght@400;700&display=swap" rel="stylesheet">
            #STYLING
        </style>
    </head>
    <body>
        {table}
    </body>
    <script src="assets/script.js"></script>
</html>
'''
        # html_string = html_string.replace('href="assets/style.css"', f'href="{directory}/assets/style.css')

        ## OUTPUT AN HTML FILE
        with open(f"{directory}/{title}.html", 'w+') as htmlFile:
            htmlFile.write(html_string.format(table=rss.to_html(classes='podracing-style-dark')))
        
        ## OUTPUT A CSS FILE
        with open(f"{directory}/assets/style.css", 'w+') as cssFile:
            cssFile.write(dark_theme_css)
        
        ## OUTPUT JAVASCRIPT FILE
        with open(f"{directory}/assets/script.js", 'w+') as jsFile:
            jsFile.write(js_string)

        self.merge_html(f"{directory}/{title}.html", f"{directory}/assets/style.css", f"{directory}/assets/script.js", directory, title)
        return
    
    ## MERGE WEB FILES INTO A SINGLE DOC
    def merge_html(self, html_input, css_input, js_input, directory, title):
        
        html_file = Path(f'{html_input}').read_text(encoding="utf-8")

        soup = BeautifulSoup(html_file, features='lxml')
        # Find link tags. example: <link rel="stylesheet" href="css/somestyle.css">
        for tag in soup.find_all('link', href=True):
            if tag.has_attr('href'):
                css_file = Path(f'{css_input}').read_text(encoding="utf-8")

                # remove the tag from soup
                tag.extract()
        
                # insert style element
                new_style = soup.new_tag('style')
                new_style.string = css_file
                soup.html.head.append(new_style)
        
        
        # Find script tags. example: <script src="js/somescript.js"></script>
        for tag in soup.find_all('script', src=True):
            if tag.has_attr('src'):
                js_file = Path(f'{js_input}').read_text(encoding="utf-8")

                # remove the tag from soup
                tag.extract()
        
                # insert script element
                new_script = soup.new_tag('script')
                new_script.string = js_file
                soup.html.body.append(new_script)
        
        # Find image tags.
        for tag in soup.find_all('img', src=True):
            if tag.has_attr('src'):
                file_content = Path(tag['src']).read_bytes()
        
                # replace filename with base64 of the content of the file
                base64_file_content = base64.b64encode(file_content)
                tag['src'] = "data:image/png;base64, {}".format(base64_file_content.decode('ascii'))

        # Save onefile
        with open(f"{directory}/{title}.html", "w", encoding="utf-8") as outfile:
            outfile.write(str(soup))
        
        if os.path.isdir(f"{directory}/assets"):
            shutil.rmtree(f"{directory}/assets")

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
            clean = re.sub(r"[^a-zA-Z0-9 ,*\u2019-]+"," ",text).strip()
            return clean

    ## GENERATE DOWNLOAD LINK
    def generate_link(self, link):
        podtrac = 'www.podtrac.com/pts/redirect.mp3/'
        radiolab = 'radiolab_podcast'
        patreon = 'patreonusercontent'
        self.hosted_patreon = False
        if podtrac in link:
            link = f"http://{link.split(podtrac)[-1]}"
        if radiolab in link:
            link = link.split('/radiolab_podcast/')[1]
            link = f"http://wnyc-origin-iad.streamguys1.com/radiolab_podcast/{link}"
            link = link.split('?')[0]
        if patreon in link:
            link = link.replace('&amp;', '&')
            self.hosted_patreon = True
        return link

    ## DETECT AUDIO FORMAT
    def audio_format(self, file):
        self.format = file.split('.')[-1]
        self.format = re.sub(r"[^a-zA-Z0-9.]+","",self.format)
        if 'tokentime' in self.format:
            self.format = self.format.split('tokentime')[0]
        return self.format

    ## DOWNLOAD PODCAST AUDIO
    def download_audio(self):

        self.isDownloading = True

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
        self.option_overwrite.hide()

        ## REMOVE SPECIAL CHARACTERS FROM SHOW TITLE AND SET SHOW DIR
        show_title = self.title.text()
        show_title = self.clean_text(show_title, '_title')

        ## CHECK SAVE DIR CHOICE
        if not self.appDir == f'{QDir.homePath()}/podRacing':
            shutil.move(f'{QDir.homePath()}/podRacing/{show_title}', f"{self.appDir}/{show_title}")

        show_dir = (f"{self.appDir}/{show_title}")
        
        ## CREATE DOWNLOAD DIR WITH SHOW TITLE AS NAME
        if not os.path.isdir(show_dir):
            os.makedirs(show_dir)
        if not os.path.isdir(f"{show_dir}/audio"):
            os.makedirs(f"{show_dir}/audio")
        
        ## GET DL LINK FROM 'LINKS.TXT' FILE
        ## DOWNLOAD EACH FILE AND RENAME TO MATCH EPISODE NAME
        timer_start = time.perf_counter()
        self.progress_bar.show()
        with open(self.links_file) as linksText:
            for l_no, line in enumerate(linksText):

                ## SET PROGRESS BAR
                timer_add = time.perf_counter()
                QCoreApplication.processEvents()
                count_per = (count / count_length) * 100
                # self.download_progress(count_per) # ERROR!

                ## GET EPISODE TITLE
                ## IF TITLE IS BLANK, TITLE THEM NUMERICALLY IN ASC. ORDER
                episode_title = self.episode_titles[l_no]
                if episode_title == '':
                    episode_title = f"Episode {l_no + 1}"
                _title = self.clean_text(episode_title, '_title')
                
                ## GET DOWNLOAD LINK
                link = line
                link = self.generate_link(link)
                if not link.endswith('.mp3') or link.endswith('.wav') or link.endswith('.flac'):
                    if not self.hosted_patreon:
                        link = link.split('?')[0]
                
                ## GET AUDIO FORMAT
                format = self.audio_format(link)

                ## DOWNLOAD AUDIO FILE WITH EPISODE NAME TO SHOW DIR
                # r = (QtNetwork.QNetworkRequest(QUrl(link)))
                r = requests.get(link, allow_redirects=True, stream=True)
                # r = PodRacingApp.download_audio(PodRacingApp, link)
                QCoreApplication.processEvents()

                ## OVERWRITE EXISTING DOWNLOADS
                if self.option_overwrite.isChecked():
                    # if count < 1:
                    #     confirm_overwrite = QMessageBox.question(self, 'Warning', 'This will overwrite existing files\nDo you wish to continue?',
                    #                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
                    # if confirm_overwrite == QMessageBox.StandardButton.Yes:
                    print(f"{episode_title}")
                    open(f"{show_dir}/audio/{_title}.{format}", 'wb').write(r.content)
                    count += 1
                    # else:
                    #     self.reset_gui()
                    #     return

                ## IF DOWNLOAD EXISTS, SKIP TO NEXT ONE (NO-OVERWRITING)
                else:
                    if not os.path.isfile(f"{show_dir}/audio/{_title}.{format}"):
                        print(f"{episode_title}")
                        open(f"{show_dir}/audio/{_title}.{format}", 'wb').write(r.content)
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
            # self.download_complete(show_title, show_dir)
            # self.reset_gui()

    ## DOWNLOAD PROGRESS
    def download_progress(self):
        # update progress bar
        self.progress_bar.setValue(int(99))
        # adjust the font color to maintain the contrast
        self.progress_bar.setStyleSheet('QProgressBar { color: #fff; }')

    ## DOWNLOAD COMPLETE
    def download_complete(self, title, location):

        ## USE NATIVE SEPARATORS
        location = QDir.toNativeSeparators(location)

        ## PROMPT TO OPEN DIRECTORY
        if self.message.information(
            self,
            'Downloaded',
            f'Download Complete!\n\n{title} has been saved to:\n{location}\n\nNavigate to folder?',
            QMessageBox.StandardButton.Open,
            QMessageBox.StandardButton.Cancel
        ) is QMessageBox.StandardButton.Open: subprocess.Popen(["open", str(location)])

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
        self.progress_bar.hide()

    ## QUIT APPLICATION
    def quit(self):
        if os.path.isfile(self.input_file):
            os.remove(self.input_file)
        if os.path.isfile(self.episodes_file):
            os.remove(self.episodes_file)
        if os.path.isfile(self.episodes_list_file):
            os.remove(self.episodes_list_file)
        if os.path.isfile(self.links_file):
            os.remove(self.links_file)
        sys.exit() ## CAN'T EXECUTE WHILE DOWNLOADING!!

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

    def fetch_rss(self, rss_url):
        QCoreApplication.processEvents()
        fetch_call = requests.get(rss_url)
        QCoreApplication.processEvents()
        return fetch_call

    def download_audio(self, link):
        QCoreApplication.processEvents()
        download = requests.get(link, allow_redirects=True, stream=True)
        QCoreApplication.processEvents()
        return download

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
    app.setFont(QFont('Helvetica Nue'))
    app.setStyleSheet("QLabel{font-family: 'Helvetica Nue';}")
    podRacingGUI.show()
    podRacing = PodRacingApp(init())
    # podRacing.clear()
    podRacing.create_appDir()
    

    sys.exit(app.exec())