import sys
import os
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QCheckBox, QPushButton, QDialog, 
    QDialogButtonBox, QMessageBox
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QTimer, QSize

if getattr(sys,"frozen",False):
    import pyi_splash

def download_file(url, save_path):
    try:
        response = requests.get(url, stream=True)
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return True
    except Exception as e:
        return False

def find_star_citizen_installations():
    valid_folders = []
    for drive in ['C:\\', 'D:\\', 'E:\\', 'F:\\']:
        for root, dirs, files in os.walk(drive):
            if 'StarCitizen' in root:
                if 'Data.p4k' in files:
                    folder_name = os.path.basename(root)
                    valid_folders.append((folder_name, root))
 
    if getattr(sys, "frozen", False):
        pyi_splash.close()
 
    return valid_folders

def start_installation(selected_folders):
    if not selected_folders:
        return "yellow"

    file_url = "https://drive.google.com/uc?export=download&id=1nS6AvSXgctANr-enrFg5XkZVUdY4N5qH"
    for folder_name, folder_path in selected_folders:
        data_folder = os.path.join(folder_path, "data", "Localization", "italian_(italy)")
        os.makedirs(data_folder, exist_ok=True)
        save_path = os.path.join(data_folder, "global.ini")
        success = download_file(file_url, save_path)

        config_path = os.path.join(folder_path, "user.cfg")
        with open(config_path, 'w') as cfg_file:
            cfg_file.write("g_language=italian_(italy)\n")
            cfg_file.write("g_LanguageAudio=english\n")

        if success:
            return "green"
    return "red"

def remove_translation(selected_folders):
    if not selected_folders:
        return "yellow"

    for folder_name, folder_path in selected_folders:
        data_folder = os.path.join(folder_path, "data")
        config_path = os.path.join(folder_path, "user.cfg")

        if os.path.exists(config_path):
            os.remove(config_path)

        if os.path.exists(data_folder):
            localization_folder = os.path.join(data_folder, "Localization")
            if os.path.exists(localization_folder):
                italian_folder = os.path.join(localization_folder, "italian_(italy)")
                if os.path.exists(italian_folder):
                    for root, dirs, files in os.walk(italian_folder, topdown=False):
                        for file in files:
                            os.remove(os.path.join(root, file))
                        for dir in dirs:
                            os.rmdir(os.path.join(root, dir))
                    os.rmdir(italian_folder)

                if not os.listdir(localization_folder):
                    os.rmdir(localization_folder)

            if not os.listdir(data_folder):
                os.rmdir(data_folder)

        return "red"
    return "yellow"

class WarningWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Installer di MrRevo")
        self.setFixedSize(800, 400)  # Dimensione aumentata
        verticalLayout = QVBoxLayout()
        verticalLayout.setObjectName(u"verticalLayout")
        label = QLabel(""" 
Attenzione:
Questo è un installer creato da MrRevo.
Continuando, accetti di assumerti la piena responsabilità per l'uso di questo software,
poiché non è un installer certificato.
Usa questo strumento a tuo rischio.
        """)
        label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)

        verticalLayout.addWidget(label)

        self.checkBox = QCheckBox("Accetto i termini*")
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setMinimumSize(QSize(0, 70))
        font1 = QFont()
        font1.setPointSize(16)
        font1.setBold(False)
        self.checkBox.setFont(font1)
        self.checkBox.setAutoFillBackground(False)

        verticalLayout.addWidget(self.checkBox)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        verticalLayout.addWidget(button_box)


        self.setLayout(verticalLayout)

    def accept(self):
        if self.checkBox.isChecked():
            super().accept()
        else:
            QMessageBox.warning(self, "Attenzione", "Devi accettare i termini per continuare.")

class FolderSelectionWindow(QWidget):
    def __init__(self, valid_folders):
        super().__init__()
        self.setWindowTitle("Seleziona le cartelle di installazione")
        self.setWindowIcon(QIcon("MrRevo.ico"))

        layout = QVBoxLayout()

        self.setStyleSheet("background-color: #2c3e50;")

        self.selected_folders = []
        self.checkboxes = {}

        instruction_label = QLabel("SELEZIONA LA VERSIONE DI STAR CITIZEN\nDALLA QUALE VUOI AGGIUNGERE O RIMUOVERE LA TRADUZIONE")
        instruction_label.setStyleSheet("color: black; font-size: 20px; font-weight: bold;")
        instruction_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(instruction_label)

        for folder_name, folder_path in valid_folders:
            checkbox = QCheckBox(folder_name)
            checkbox.folder_path = folder_path
            checkbox.setStyleSheet("font-size: 18px; padding: 10px;")  # Dimensione e padding aumentati
            layout.addWidget(checkbox)
            self.checkboxes[checkbox] = (folder_name, folder_path)

        install_button = QPushButton("Installa traduzione")
        install_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                font-weight: bold; 
                font-size: 18px; 
                padding: 10px 20px; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            """
        )
        install_button.clicked.connect(self.install)
        layout.addWidget(install_button)

        remove_button = QPushButton("Rimuovi traduzione")
        remove_button.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336; 
                color: white; 
                font-weight: bold; 
                font-size: 18px; 
                padding: 10px 20px; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
            """
        )
        remove_button.clicked.connect(self.remove_translation)
        layout.addWidget(remove_button)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: black; padding: 10px; font-weight: bold;")
        self.status_label.hide()
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def install(self):
        selected_folders = [(name, path) for checkbox, (name, path) in self.checkboxes.items() if checkbox.isChecked()]
        result = start_installation(selected_folders)

        if result == "green":
            self.show_status("Traduzione installata\nCHIUSURA IMMINENTE", "rgba(0, 255, 0, 128)")
            QTimer.singleShot(10000, self.close)
        elif result == "yellow":
            self.show_status("Per piacere seleziona una versione", "rgba(255, 255, 0, 128)")

    def remove_translation(self):
        selected_folders = [(name, path) for checkbox, (name, path) in self.checkboxes.items() if checkbox.isChecked()]
        result = remove_translation(selected_folders)

        if result == "red":
            self.show_status("Traduzione rimossa\nCHIUSURA IMMINENTE", "rgba(255, 0, 0, 128)")
            QTimer.singleShot(5000, self.close)
        elif result == "yellow":
            self.show_status("Per piacere seleziona una versione", "rgba(255, 255, 0, 128)")

    def show_status(self, message, color):
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"background-color: {color}; color: black; padding: 10px;")
        self.status_label.show()

def run_installer():
    app = QApplication(sys.argv)
    valid_folders = find_star_citizen_installations()
    if not valid_folders:
        QMessageBox.warning(None, "Nessuna cartella trovata", "Non sono state trovate cartelle di Star Citizen con il file Data.p4k.")
        return

    warning_window = WarningWindow()
    if warning_window.exec_() == QDialog.Accepted:
        folder_window = FolderSelectionWindow(valid_folders)
        folder_window.show()
        sys.exit(app.exec_())


run_installer()