## IMPORTS
if 'Imports':

    if 'Standard':
        import os, sys, re, socket
        from datetime import datetime
        from functools import partial

    if 'Libraries':
        from n4s import fs, strgs

    if 'PyQt6':
        from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QCheckBox, QStackedWidget,
                                    QLineEdit, QPushButton, QComboBox, QMessageBox)
        from PyQt6.QtGui import QFontMetrics
        from PyQt6.QtCore import Qt, QDir

## SETTINGS
if 'Settings':

    ## APP INFO
    APP_NAME = "jf-listen"

    ## APP VERSION
    APP_VERSION = 1.0

    ## APP DEVS
    APP_DEVS = "need4swede"

    ## APP YEAR
    APP_YEAR = datetime.today().strftime("%Y")

    ## APP DIR
    APP_DIR = os.path.join(QDir.homePath(), 'jf-listen')

    ## SCREEN WIDTH
    SCREEN_WIDTH = ''

    ## SCREEN HEIGHT
    SCREEN_HEIGHT = ''

## APP SETUP
class SetupApp(QWidget):

    ## INITIALIZE SETUP
    def __init__(self):
        super().__init__()

        ## SET STARTING WIDTH (DYNAMICALLY ADJUSTS)
        self.setFixedWidth(275)
        self.setFixedHeight(140)

        ## STORED VARIABLES
        self.server_address = ''

        ## CHECKS
        self.is_ip = False

        ## LAUNCH GUI
        self.init_ui()

    ## INITIALIZE GUI
    def init_ui(self):

        ## SET LAYOUT
        layout = QVBoxLayout()
        self.pages = QStackedWidget()

        ## INITIALIZE PAGES
        self.init_address_page()
        self.init_port_page()
        self.init_auth_page()
        layout.addWidget(self.pages)

        ## NEXT BUTTON
        self.next_button = QPushButton('Next')
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)
        layout.addWidget(self.next_button)

        ## SET LAYOUT
        self.setLayout(layout)
        self.setWindowTitle(APP_NAME)
        self.show()

    ## INTIALIZE ADDRESS PAGE
    def init_address_page(self):

        ## SERVER PROTOCOL AND ADDRESS PAGE
        address_layout = QHBoxLayout()
        address_page_layout = QVBoxLayout()
        self.add_centered_label('Server Address', address_page_layout)

        ## SERVER PROTOCOL INPUT
        self.protocol_input = QComboBox()
        self.protocol_input.addItems(['http://', 'https://'])
        address_layout.addWidget(self.protocol_input)

        ## SERVER ADDRESS INPUT
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("192.168.0.")

        ## SERVER ADDRESS INPUT - VALIDATION
        self.address_input.textChanged.connect(partial(self.validate_inputs, self.address_input))
        self.address_input.textChanged.connect(partial(self.adjust_page_width, self.address_input))
        self.address_input.editingFinished.connect(partial(self.default_input, self.address_input))

        ## ADD TO LAYOUT
        address_layout.addWidget(self.address_input)
        address_page_layout.addLayout(address_layout)

        ## GENERATE PAGE
        address_page = QWidget()
        address_page.setLayout(address_page_layout)
        self.pages.addWidget(address_page)

    ## INITIALIZE PORT PAGE
    def init_port_page(self):
        port_layout = QVBoxLayout()
        self.add_centered_label('Port', port_layout)
        self.port_input = QLineEdit()
        self.port_input.setMaxLength(4)
        self.port_input.setPlaceholderText("8096")

        ## SERVER PORT INPUT - VALIDATION
        self.port_input.textChanged.connect(partial(self.validate_inputs, self.port_input))
        self.port_input.editingFinished.connect(partial(self.default_input, self.port_input))

        port_layout.addWidget(self.port_input)
        port_page = QWidget()
        port_page.setLayout(port_layout)
        self.pages.addWidget(port_page)

    ## INITIALIZE AUTH PAGE
    def init_auth_page(self):

        ## SET LAYOUT
        auth_layout = QVBoxLayout()

        ## USERNAME
        self.add_centered_label('Username', auth_layout)
        self.user_input = QLineEdit()
        self.user_input.textChanged.connect(partial(self.validate_inputs, self.user_input))
        self.user_input.editingFinished.connect(partial(self.default_input, self.user_input))
        auth_layout.addWidget(self.user_input)
        auth_layout.addSpacing(15)

        ## PASSWORD
        self.add_centered_label('Password', auth_layout)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.textChanged.connect(partial(self.validate_inputs, self.password_input))
        self.password_input.editingFinished.connect(partial(self.default_input, self.password_input))
        auth_layout.addWidget(self.password_input)

        ## CREATE PAGE
        auth_page = QWidget()
        auth_page.setLayout(auth_layout)
        self.pages.addWidget(auth_page)

    ## DYNAMICALLY ADJUST WINDOW SIZE BASED ON TEXT LENGHT
    def adjust_page_width(self, element):

        ## GET WIDTH OF THE INPUT TEXT
        fm = QFontMetrics(element.font())
        text_width = fm.horizontalAdvance(element.text())

        ## ADJUST WINDOW WIDTH
        new_width = max(text_width + 130, 275)  # +40 for some padding
        self.setFixedWidth(new_width)

    ## CREATE A CENTERED QLABEL
    def add_centered_label(self, text, layout):
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addSpacing(20)

    ## VALIDATE USER INPUTS ON EACH PAGE
    def validate_inputs(self, element):

        ## VALIDATE INPUT
        if element.hasFocus() and element.text():

            ## PAGE INDEX
            currentPageIndex = self.pages.currentIndex()

            ## ADDRESS PAGE
            if currentPageIndex == 0:

                ## CHECKS IF INPUT IS A VALID IP OR DOMAIN
                ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
                is_ip = re.match(ip_pattern, element.text())
                valid_domain_endings = ['com', 'net', 'org']
                is_domain = any(element.text().endswith('.' + domain) for domain in valid_domain_endings)
                if not element.text()[-1] == '.' and (is_ip or is_domain):
                    self.next_button.setEnabled(True)
                else:
                    self.next_button.setEnabled(False)

            ## PORT PAGE
            if currentPageIndex == 1:

                ## CHECKS IF INPUT IS A VALID PORT NUMBER
                if re.match("^[0-9]+$", element.text()):
                    self.next_button.setEnabled(True)
                else:
                    self.next_button.setEnabled(False)

            ## LOGIN PAGE
            if currentPageIndex == 2:

                ## INVALIDATE KEYS THAT ARE TOO SHORT
                if len(element.text()) > 1:
                    self.next_button.setEnabled(True)
                else:
                    self.next_button.setEnabled(False)
        else:
            self.next_button.setEnabled(False)

    ## HANDLE PAGE NAVIGATION
    def next_page(self):

        ## CURRENT PAGE
        current_index = self.pages.currentIndex()

        ## SKIP PORT INPUT ON NON-IP INPUTS
        if current_index == 0:
            ip_address = re.match(r"^[0-9]{3}\.", self.address_input.text())
            if not ip_address:
                self.setFixedHeight(220)
                self.pages.setCurrentIndex(current_index + 2)
                return
            else:
                self.is_ip = True

        ## HANDLE NAVIGATION
        if current_index + 1 < self.pages.count():
            self.next_button.setEnabled(False)
            self.pages.setCurrentIndex(current_index + 1)
            if self.pages.currentIndex() == 2:
                self.setFixedHeight(220)
                self.next_button.setText('Save Config')
            else:
                self.next_button.setText('Next')
        else:
            self.save_config()

    ## USE DEFAULT INPUT ON 'RETURN' PRESS
    def default_input(self, element):
        if element.hasFocus():
            if not element.text():
                element.setText(element.placeholderText())
            else:
                self.next_button.click()

    ## BUILDS SERVER ADDRESS FROM INPUTS
    def build_address(self):
        if self.is_ip:
            self.server_address = f"{self.protocol_input.currentText()}{self.address_input.text()}:{self.port_input.text()}"
        else:
            self.server_address = f"{self.protocol_input.currentText()}{self.address_input.text()}"

        self.device_name = socket.gethostname().replace('.local', '')

    ## BUILDS FILE DIRECTORIES
    def build_directories(self):

        ## BUILD APP DIR
        fs.path_exists(APP_DIR, Make=True)

        ## LOG DIRS
        fs.path_exists(os.path.join(APP_DIR, 'logs'), Make=True)
        fs.path_exists(os.path.join(APP_DIR, 'logs', 'all'), Make=True)
        fs.path_exists(os.path.join(APP_DIR, 'logs', 'errors'), Make=True)

        ## LOG FILES
        self.log_file = os.path.join(APP_DIR, 'logs', 'all', 'log.txt')
        self.error_log_file = os.path.join(APP_DIR, 'logs', 'errors', 'error_log.txt')

    ## GENERATE CONFIG FILE
    def save_config(self):

        ## GENERATE SERVER ADDRESS
        self.build_address()

        ## GENERATE APP DIRECTORIES
        self.build_directories()

        ## CREATE CONFIG FILE
        current_file_directory = os.path.dirname(os.path.abspath(__file__))
        config_py_file = os.path.join(current_file_directory, 'config.py')
        config_content = f"""server = dict(
    address = "{self.server_address}",
    user = "{self.user_input.text()}",
    password = "{self.password_input.text()}"
)

local = dict(
    app = "{APP_NAME}",
    version = "{APP_VERSION}",
    device = "{self.device_name}",
    id = "{self.device_name}_{APP_VERSION}",
    log = "{self.log_file}",
    error_log = "{self.error_log_file}"
)

refresh_mode = dict(
    default = "Refresh",
    missing = "Refresh?Recursive=true&ImageRefreshMode=FullRefresh&MetadataRefreshMode=FullRefresh&ReplaceAllImages=false&ReplaceAllMetadata=false",
    replace_images = "Refresh?Recursive=true&ImageRefreshMode=FullRefresh&MetadataRefreshMode=FullRefresh&ReplaceAllImages=true&ReplaceAllMetadata=false",
    replace_metadata = "Refresh?Recursive=true&ImageRefreshMode=FullRefresh&MetadataRefreshMode=FullRefresh&ReplaceAllImages=false&ReplaceAllMetadata=true",
    replace_all = "Refresh?Recursive=true&ImageRefreshMode=FullRefresh&MetadataRefreshMode=FullRefresh&ReplaceAllImages=true&ReplaceAllMetadata=true"
)
"""

        ## WRITE CONFIG TO FILE
        with open(config_py_file, "w") as py_file:
            py_file.write(config_content)

        ## SHOW COMPLETION MESSAGE
        QMessageBox.information(self, 'Info', 'Configuration Saved.')
        self.close()

## RUN
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main_window = SetupApp()
    sys.exit(app.exec())