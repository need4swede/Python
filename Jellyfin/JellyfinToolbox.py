###### IMPORTS
if 'Imports':

    if 'Standard':
        import subprocess, warnings, linecache, os, sys, traceback
        import requests, datetime, multiprocessing, webbrowser
        from datetime import datetime

    if 'Libraries':
        from n4s import fs, strgs, term, web
        from pathlib import Path as _dir
        from bs4 import BeautifulSoup
        from pyffmpeg import FFmpeg
        from rfeed import *
        import Cocoa, urllib.request
        import pandas as pd
        import html, whisper
        from openpyxl import Workbook, load_workbook
        from openpyxl.styles import Font, PatternFill, DEFAULT_FONT

    if 'PyQt6':
        from PyQt6.QtWidgets import (QApplication, QStatusBar, QComboBox, QPlainTextEdit, QMenuBar, QTextEdit,
                                    QMenu, QWidget, QLabel, QLineEdit, QPushButton, QProgressBar,
                                    QMessageBox, QFileDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QDialog, QDialogButtonBox)
        from PyQt6.QtCore import Qt, QDir, QCoreApplication, QObject, QRunnable, pyqtSlot, pyqtSignal, QThreadPool
        from PyQt6.QtGui import QIcon, QCursor, QFont, QShortcut, QKeySequence, QAction, QTextCursor
        from PyQt6 import QtCore

###### SETTINGS
if 'Settings':

    if 'Code Settings':
        CODE_enable_version_tooltip = 0
        CODE_enable_developer_tools_menu = 1
        CODE_enable_WIP = 0

    if 'Application Settings':

        ## APP INFO
        APP_name = "JellyBox"
        APP_domain = "app"
        APP_web = f"https://www.{APP_name.lower()}.{APP_domain}"
        APP_allow = f"{APP_web}/get/app/allow.txt"
        APP_latest = f"{APP_web}/get/app/version.txt"

        ## BETA VERSION
        APP_beta = 0
        APP_beta_ver_add = 0 ## LEAVE AT 0
        if APP_beta:
            APP_beta_ver_add = 0.1

        ## APP VERSION
        _app_version = 1.0 + APP_beta_ver_add
        APP_beta_text = f'''{APP_name} Version {_app_version} Beta:
'''

######## GLOBAL VARIABLES #####################
if 'Global Variables':                        # HIDE VARS
    OS_VERSION = float(fs.system('info')[1])  # MACOS VERSION
    RSS_URL = ''                              # LAST RSS URL
    RSS_TITLE = ''                            # LAST RSS TITLE
    RSS_ARTWORK = ''                          # RSS ART FILE
    RSS_DATA = ''                             # RSS DATA FROM FETCH
    FETCH_TIME = ''                           # TIME OF LAST FETCH
    SHOW_TITLE_LOWER = ''                     # TITLE OF SHOW IN DIR
    DOWNLOAD_QUEUE = 0                        # MAX DL COUNT
    COUNT = 0                                 # DOWNLOAD COUNTER
    SKIP_COUNT = 0                            # SKIP COUNTER
    RUN_DOWNLOAD = False                      # DL FLAG
    ACTIVE_DOWNLOAD = False                   # DL ACTIVITY FLAG
    STOP_BUTTON = ''                          # STOP DL BUTTON
    DOWNLOAD_QUEUE_LIST = []                  # RSS FEEDS IN DL QUEUE
    ACTIVE_DOWNLOAD_QUEUE = False             # DL QUEUE FLAG
    NETWORK = False                           # CHECK NETWORK
    SESSIONS = 0                              # ACTIVE SESSIONS
    LOAD_MESSAGE = ''                         # LOADING SCREEN
    USER = f"{QDir.homePath()}"               # USER DIR
    APP_DIR = f"{USER}/{APP_name}"            # PODRACER DIRECTORY
    LIB_DIR = f"{USER}/Library/{APP_name}"    # LIBRARY DIR
    PROFILE_DIR = f"{LIB_DIR}/profile"        # PROFILE DIR
    PROCESS_DIR = f"{LIB_DIR}/process"        # PROCESS DIR
    SCREEN_WIDTH = ''                         # SCREEN WIDTH
    SCREEN_HEIGHT = ''                        # SCREEN HEIGHT
###############################################

## APP UPDATES
class AppUpdate(QWidget):

    ## GLOBAL VARIABLE
    global SCREEN_WIDTH, SCREEN_HEIGHT
    changelog = ''

    ## INITIALIZE WINDOW
    def __init__(self):
        super().__init__()

        ## KEEP WINDOW ON TOP
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.move(self.geometry().center())

        ## CHECK FOR UPDATES
        update_available = self.check_update()
        if update_available:

            ## WINDOW LABELS
            self.show()
            self.setFixedSize(625, 500)
            layout = QVBoxLayout()
            prompt_section = QHBoxLayout() # INSTALL / CANCEL

            ## CANCEL BTN
            self.cancel = QPushButton('Cancel')
            self.cancel.setFixedSize(120,32)
            self.cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.cancel.clicked.connect(self.close)

            ## INSTALL BTN
            self.install = QPushButton('Install')
            self.install.setFixedSize(120,32)
            self.install.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.install.clicked.connect(self.install_update)

            ## CHANGELOG & PROMPT FOR UPDATE
            self.view_update()

            ## DISPLAY CHANGELOG
            view_changelog = QTextEdit()
            view_changelog.setFixedSize(575, 400)
            view_changelog.setReadOnly(True)
            view_changelog.setHtml(changelog)

            ## CREATE LAYOUT
            layout.addWidget(view_changelog)
            prompt_section.addWidget(self.cancel)
            prompt_section.addWidget(self.install)
            layout.addLayout(prompt_section)
            self.setLayout(layout)
        else: ## LATEST VERSION ALREADY INSTALLED
            QMessageBox.move(self, int(SCREEN_WIDTH/3), int(SCREEN_HEIGHT/3))
            QMessageBox.about(self, f"{APP_name}", "Latest version already installed")

    ## CHECK FOR APP UPDATES
    def check_update(self):

        ## GET VALUE OF LATEST APP VERSION
        read_app_version = urllib.request.urlopen(APP_latest)

        ## READ THE VALUE OF LATEST APP VERSION
        for line in read_app_version:
            latest_app_version = line.decode("utf-8")

        ## CHECK IF LATEST VERSION IS INSTALLED
        if _app_version < float(latest_app_version):
            return True
        else:
            return False

    ## VIEW CHANGELOG AND PROMPT FOR UPDATE
    def view_update(self):

        ## IMPORT GLOBAL VARIABLE
        global changelog

        ## GET CHANGELOG
        get_changelog = f"{APP_web}/get/app/changelog.html"
        read_changelog = urllib.request.urlopen(get_changelog)

        ## READ CHANGELOG
        change_log_txt = []
        for line in read_changelog:
            decoded_line = line.decode("utf-8")
            if 'Edit Lines':
                # if '<h4>' in decoded_line:
                #     temp = decoded_line
                #     decoded_line = "<span style=\"* font-size:50px;\" >"
                #     decoded_line += temp
                #     decoded_line += "</span>"
                #     print(decoded_line)
                pass
            change_log_txt.append(decoded_line)

        ## UPDATE GLOBAL VARIABLE
        changelog=' '.join(change_log_txt)

    ## INSTALL UPDATE
    def install_update(self):

        ## UPDATE PARAMETERS
        download_url = f'{APP_web}/get/{APP_name}_installer.zip'
        download_zip = f'{QDir.homePath()}/Downloads/{APP_name}_updater.zip'
        download_app = f'{QDir.homePath()}/Downloads/{APP_name} Installer.app'
        download_app_request = requests.get(download_url, allow_redirects=True)
        download_app_location = QDir.toNativeSeparators(download_zip)


        ## REMOVE PREVIOUS INSTALLERS
        fs.remove_file(download_zip)
        fs.remove_dir(download_app)

        ## DOWNLOAD LATEST INSTALLER
        term.wait(1)
        open(download_zip, 'wb').write(download_app_request.content)

        ## UNZIP INSTALLER
        subprocess.Popen(["open", str(download_app_location)])
        term.wait(1)

        ## RUN INSTALLER
        subprocess.Popen(["open", download_app])

        ## QUIT APP
        app.exit()

    ## ROLLBACK TO PREVIOUS INSTALL
    def install_rollback(self):

        ## IMPORT GLOBAL VARIABLE
        global APP_beta

        ## LINK PARAMETERS
        if APP_beta:
            download_url = 'https://drive.google.com/uc?export=download&id=1sBhhmEkmV2vFuSF7ioZZSEbg95V-KPcb'
            download_zip = f'{QDir.homePath()}/Downloads/{APP_name}_installer.zip'
            download_app = f'{QDir.homePath()}/Downloads/{APP_name} Installer.app'
            download_app_request = requests.get(download_url, allow_redirects=True)
            download_app_location = QDir.toNativeSeparators(download_zip)
        else:
            download_url = 'https://drive.google.com/uc?export=download&id=1j6yCVogmToGhSIa_WkVUA614K9h8dDKt'
            download_zip = f'{QDir.homePath()}/Downloads/{APP_name} Downgrade Tool.zip'
            download_app = f'{QDir.homePath()}/Downloads/{APP_name} Downgrade Tool.app'
            download_app_request = requests.get(download_url, allow_redirects=True)
            download_app_location = QDir.toNativeSeparators(download_zip)

        ## REMOVE PREVIOUS INSTALLERS
        fs.remove_file(download_zip)
        fs.remove_dir(download_app)

        ## DOWNLOAD LATEST INSTALLER
        term.wait(1)
        open(download_zip, 'wb').write(download_app_request.content)

        ## UNZIP INSTALLER
        subprocess.Popen(["open", str(download_app_location)])
        term.wait(1)

        ## RUN INSTALLER
        subprocess.Popen(["open", download_app])

        ## QUIT APP
        app.exit()

## MAIN APP
class Jellyfin(QWidget):

    ## INITIALIZE APPLICATION & GUI
    def __init__(self, *args, **kwargs):
        super(QWidget, self).__init__(*args, **kwargs)

        ############################################################## GLOBAL FLAGS
        if 'Global Flags':
            today_date = datetime.now().strftime("%B %d, %Y")

        ############################################################## MAIN WINDOW
        if 'Main Window':

            ## WINDOW TITLE
            self.setWindowTitle(f'{APP_name}')

            # MAIN LAYOUT
            self.layout = QVBoxLayout()

            # HEIGHT:                 WIDTH:
            self.setFixedHeight(125); self.setFixedWidth(315)

            # MARGINS
            self.layout.setContentsMargins(15, 15, 15, 10)

            ## WINDOW ALWAYS ON TOP
            self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)

            ## GET SCREEN DIMENSIONS
            screen = QApplication.primaryScreen()
            rect = screen.availableGeometry()
            self.screen_width = rect.width()
            self.screen_height = rect.height()

            ## UPDATE GLOBAL SCREEN DIMENSIONS
            global SCREEN_WIDTH, SCREEN_HEIGHT
            SCREEN_WIDTH = self.screen_width
            SCREEN_HEIGHT = self.screen_height

            ## ON WINDOW CLOSE
            app.aboutToQuit.connect(lambda: self.quit(True))

            # SET LAYOUT
            self.setLayout(self.layout)

        ############################################################## MENU BAR
        if 'Menu Bar':

            ## MAIN MENU BAR
            self.menuBar = QMenuBar()

            ## MENU - FILE
            self.fileMenu = QMenu('File')
            if 'File Menu':

                ## MENU - FILE - Restart
                self.fileMenu.addAction(' &Restart', self.restart)

            ## MENU - EDIT
            self.editMenu = QMenu('Edit')
            if 'Edit Menu':

                ## MENU - EDIT - TERMINAL
                self.editMenu.addAction(' &New Terminal', lambda: fs.system('app-terminal'))

                ## MENU - EDIT - TEXTFILE
                self.editMenu.addAction(' &New Text File', lambda: fs.system('app-textedit'))
                self.editMenu.addSeparator()

            ## MENU - HELP
            self.helpMenu = QMenu('Help')
            if 'Help Menu':

                ## MENU - HELP - VIEW DOCUMENTATION
                self.helpMenu.addAction(f' &{APP_name} Help', lambda: webbrowser.open(f'{APP_web}/documentation/'))

                ## MENU - HELP - VIEW CHANGELOG
                self.helpMenu.addAction(' &Full Changelog', lambda: webbrowser.open(f'{APP_web}/documentation/support.html#changelog'))
                self.helpMenu.addSeparator()

                ## MENU - HELP - UPDATE / DOWNGRADE
                if APP_beta:
                    self.helpMenu.addAction(f' &Leave {APP_name} Beta', lambda: self.information_window('rollback_version'))
                else:
                    self.helpMenu.addAction(' &Check for Updates', self.check_update)
                    self.helpMenu.addAction(' &Downgrade Version', lambda: self.information_window('rollback_version'))
                self.helpMenu.addSeparator()

            ## MENU - HELP - CONTACT
            self.helpMenuContact = QMenu(' &Contact Developer', self)
            if 'Help Contact':

                ## PRE-SCRIPTED CONTACT TEMPLATES
                contact_dev_options = [
                    f"Date: {today_date}\n{APP_name} Version: {_app_version}\n{fs.system()}\n\n",
                    f"Hi Mike!\n\nMy name is {str(fs.root()).split('/Users/')[1]} and I have a question about {APP_name}.\n\n",
                    ]

                self.helpMenu.addMenu(self.helpMenuContact)
                self.helpMenuContact.addAction(' &General Inquiry', lambda: fs.mail('contact@mafshari.work', f'{APP_name} Inquiry', contact_dev_options[0] + contact_dev_options[1]))
                self.helpMenuContact.addAction(' &Report a Bug', lambda: fs.mail('contact@mafshari.work', f'{APP_name} Bug Report', contact_dev_options[0] + 'Bug Report:\n\n'))
                self.helpMenuContact.addAction(' &Request a Feature', lambda: fs.mail('contact@mafshari.work', f'{APP_name} Feature Request', contact_dev_options[0] + 'Feature Request:\n\n'))
                self.helpMenu.addSeparator()

                        ## CLEAR MENUBAR
            self.menuBar.clear()

            ## FILE
            self.menuBar.addMenu(self.fileMenu)

            ## EDIT
            self.menuBar.addMenu(self.editMenu)

            ## HELP
            self.menuBar.addMenu(self.helpMenu)

        ############################################################## LAYOUT SECTIONS
        if 'Layout Sections':

            ########################################################## TOP SECTION
            topBar = QHBoxLayout() # URL / FETCH

            ####################################################### MIDDLE SECTION
            self.detailSec = QHBoxLayout() # METADATA SECTION
            self.metaSec = QVBoxLayout() # METADATA

            ################################################### ADDITIONAL OPTIONS
            self.additionalOptions = QStatusBar() # OVERWRITE

            ####################################################### BOTTOM SECTION
            downloadSec = QHBoxLayout() # DOWNLOAD SECTION
            self.progress_bar = QProgressBar() # PROGRESS BAR
            downloadBtn = QVBoxLayout() # DOWNLOAD BTN
            downloadMeta = QVBoxLayout() # DOWNLOAD METADATA

            ########################################################## MESSAGE BOX
            self.message = QDialog() # MESSAGE PROMPTS
            self.message.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            self.message.move(self.geometry().center())

        ############################################################## MAIN WINDOW
        if 'Main Window Layout':

            ########################################################## URL BOX
            self.urlBox = QLineEdit()
            self.urlBox.setFixedSize(140, 23.3)
            self.urlBox.setPlaceholderText('Jellyfin Media Folder...')

            ########################################################## FETCH BUTTON
            self.button = QPushButton('Swim')
            # self.button.clicked.connect(self.fetch_RSS)
            self.button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

            ########################################################## QUIT BUTTON
            self.quitBtn = QPushButton('Quit')
            self.quitBtn.setFixedSize(60,32)
            self.quitBtn.clicked.connect(lambda: self.quit(True))
            self.quitBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

            ########################################################## METADATA TAGS

            ## CREATE LABELS
            self.credit = QLabel(f'{APP_name} | by Mike Afshari')
            self.version = QLabel(f'Version {_app_version}')

            ## BETA TAG AND INFO TEXT
            if APP_beta:
                self.version.setText(self.version.text() + ' Beta')
                self.beta_info = QPlainTextEdit()
                beta_text = APP_beta_text
                self.beta_info.setPlainText(beta_text)

            ## ADD VERSION TOOLTIP
            if CODE_enable_version_tooltip:
                self.version.setToolTip(f"{self.version.text().replace('Version ', 'v').replace(' Beta', '')} "
                "changes:"
                    "\n- Added Integrated Updater"
                    "\n- New 'History' Tool (beta)"
                    "\n- Various optimizations")

            ## SET CREDIT STYLING
            self.credit.setStyleSheet('font-size: 11px; font-weight: bold;')

            ## SET VERSION STYLING
            self.version.setStyleSheet('''
                font-size: 10px;
                background: none;
                text-align: left;
                padding: 0;
                width: 2px;
                ''')

            ########################################################## DOWNLOAD PROGRESS BAR
            self.progress_bar.setFixedHeight(4)
            self.progress_bar.hide()

            ########################################################## DOWNLOAD METADATA
            self.current_download = QLabel()
            self.current_download.hide()

        ############################################################## ADDING SECTIONS
        if 'Build Window Layout':

            ########################################################## TOP SECTION
            topBar.addWidget(self.urlBox)
            topBar.addWidget(self.quitBtn)
            topBar.addWidget(self.button)

            ########################################################## METADATA SECTION
            self.metaSec.addWidget(self.credit)
            self.metaSec.addWidget(self.version)
            self.detailSec.addLayout(self.metaSec)

            ########################################################## CREATE LAYOUT

            ## ADD LAYOUT TO WINDOW
            self.layout.addLayout(topBar)
            self.layout.addLayout(self.detailSec)
            self.layout.addLayout(downloadMeta)

            ## ADD BETA INFO
            if APP_beta:
                self.setFixedHeight(225)
                self.layout.addWidget(self.beta_info)

        ############################################################## KEYBOARD SHORTCUT
        if 'Keyboard Shortcuts':

            ## PODSEARCH SHORTCUT
            self.shortcut_find = QShortcut(QKeySequence('Ctrl+p'), self)
            self.shortcut_find.activated.connect(lambda: self.podsearch('search'))

            ## HISTORY SHORTCUT
            self.shortcut_history = QShortcut(QKeySequence('Ctrl+o'), self)
            self.shortcut_history.activated.connect(lambda: self.history_RSS('View'))

            ## BOOKMARK SHORTCUT
            self.shortcut_bookmarks = QShortcut(QKeySequence('Ctrl+b'), self)
            self.shortcut_bookmarks.activated.connect(lambda: self.bookmark_manager('add'))

            ## 'ENTER' TO FETCH
            self.click_fetch = QShortcut(QKeySequence('Return'), self)
            self.click_fetch.activated.connect(self.button.click)

            ## CLOSE WINDOW SHORTCUT
            self.shortcut_close = QShortcut(QKeySequence('Ctrl+m'), self)
            self.shortcut_close.activated.connect(lambda: self.close())

        ############################################################## MULTITHREADING
        if 'Multithreading':
            self.thread={}
            self.threadpool = QThreadPool()
            self.quitBtn.clicked.connect(app.exit)

        ############################################################## STARTUP CHECKS
        if 'Startup Checks':

            ## CLEAR TERMINAL
            term.clear()

    ## AUTO CHECK FOR UPDATES
    def auto_check_update(self):

        ## IMPORT GLOBAL VARIABLE
        global NETWORK

        ## CHECK NETWORK CONNECTION
        NETWORK = web.network_test()

        ## IF CONNECTED TO NETWORK
        if NETWORK:

            ## GET VALUE OF LATEST APP VERSION
            read_app_version = urllib.request.urlopen(APP_latest)

        else:
            self.restart()
            return

        ## READ THE VALUE OF LATEST APP VERSION
        for line in read_app_version:
            latest_app_version = line.decode("utf-8")

        ## CHECK IF LATEST VERSION IS INSTALLED
        if _app_version < float(latest_app_version):
            QMessageBox.move(self, int(self.screen_width/3), int(self.screen_height/3))
            prompt_for_update = QMessageBox.question(self, "Update Available", f"There's a newer version of {APP_name} available\n\nWould you like to install it?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
            if prompt_for_update == QMessageBox.StandardButton.Yes:
                self.check_update()
                Jellyfin.setWindowFlags(self, QtCore.Qt.WindowType.WindowType_Mask)
        else:
            pass

    ## CHECK FOR UPDATES
    def check_update(self):

        ## IMPORT GLOBAL VARIABLE
        global NETWORK

        ## UPDATE
        if NETWORK:
            self.check_for_updates = AppUpdate()
        else:
            QMessageBox.information(self, f"{APP_name}", "\nUnable to complete task!\n\nNetwork Connection Failed")

    ## RESTART APP
    def restart(self):
        fs.system('python-restart')

    ## QUIT APP PROCESS
    def quit(self, clear: bool=False):

        ## EXIT APPLICATION
        fs.system('python-exit')


if __name__ == "__main__":

    ## REQUIRED FOR MULTI-THREADED WORKFLOW
    multiprocessing.freeze_support()

    ## INITIALIZE QAPP AND SET STYLESHEET
    app = QApplication(sys.argv)
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
            font-size: 12px;
            width: 0px;
            height: 10px;
            padding: 0;
            color: #fff;
            border: none;
            background-color: #656565;
        }
        QPushButton:hover, QComboBox:hover {
            background-color: #097ed9;
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
            width: 60px;
            padding: 6px 8px;
        }
    ''')
    app.setFont(QFont('Helvetica Nue'))
    app.setStyleSheet("QLabel{font-family: 'Helvetica Nue';}")
    clipboard = app.clipboard()

    ## PODRACER APP
    jellyfin = Jellyfin()
    jellyfin.show()
    sys.exit(app.exec())
