## IMPORTS
if 'Imports':

    if 'Standard':
        import sys, re
        from datetime import datetime
        from functools import partial

    if 'PyQt6':
        from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QCheckBox, QStackedWidget,
                                    QLineEdit, QPushButton, QComboBox, QMessageBox)
        from PyQt6.QtGui import QFontMetrics
        from PyQt6.QtCore import Qt, QDir

## SETTINGS
if 'Settings':

    ## APP INFO
    APP_NAME = "JF Listen - Setup"

    ## APP VERSION
    APP_VERSION = 1.0

    ## APP DEVS
    APP_DEVS = "need4swede"

    ## APP YEAR
    APP_YEAR = datetime.today().strftime("%Y")

## GLOBAL VARIABLES
if 'Global Variables':

    ## USER DIR
    USER = f"{QDir.homePath()}"

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

        ## STORED VARIABLES
        self.server_address = ''
        self.api_key = ''

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
        self.init_api_page()
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

    ## INITIALIZE API KEY PAGE
    def init_api_page(self):
        api_layout = QVBoxLayout()
        self.add_centered_label('Jellyfin API Key', api_layout)
        self.api_key_input = QLineEdit()

        ## SERVER API INPUT - VALIDATION
        self.api_key_input.textChanged.connect(partial(self.validate_inputs, self.api_key_input))
        self.api_key_input.editingFinished.connect(partial(self.default_input, self.api_key_input))

        api_layout.addWidget(self.api_key_input)
        api_page = QWidget()
        api_page.setLayout(api_layout)
        self.pages.addWidget(api_page)

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

            ## API KEY PAGE
            if currentPageIndex == 2:

                ## INVALIDATE KEYS THAT ARE TOO SHORT
                if len(element.text()) > 30:
                    self.next_button.setEnabled(True)
                else:
                    self.next_button.setEnabled(False)
        else:
            self.next_button.setEnabled(False)

    ## HANDLE PAGE NAVIGATION
    def next_page(self):

        ## CURRENT PAGE
        current_index = self.pages.currentIndex()

        ## CHECK FOR PORT ON NEXT PAGE IF ADDRESS IS AN IP
        if current_index == 0:
            match = re.match(r"^(.*?):(\d{1,4})$", self.address_input.text())
            if match or not re.match(r"^[0-9]{3}\.", self.address_input.text()):
                if match:
                    self.server_address, self.server_port = match.groups()
                else:
                    self.server_address = self.address_input.text()
                self.pages.setCurrentIndex(current_index + 2)
                return

        ## HANDLE NAVIGATION
        if current_index + 1 < self.pages.count():
            self.next_button.setEnabled(False)
            self.pages.setCurrentIndex(current_index + 1)
            if self.pages.currentIndex() == 2:
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

    def save_config(self):
        # This is just a placeholder. You'd gather data from the fields and call your config() function.
        QMessageBox.information(self, 'Info', 'Configuration Saved.')

## RUN
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main_window = SetupApp()
    sys.exit(app.exec())