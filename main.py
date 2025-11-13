import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QStyleFactory
from PyQt6.QtGui import QFont, QAction, QKeySequence
from flag_widget import FlagWidget
from folium_map_widget import MapWidget
import json
from glob import glob
import random
from os.path import join
from PyQt6.QtCore import Qt
import os


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.reveal_mode = True
        self.flags_folder = join("country-flags-main", "png")
        self.maps_folder = join("country_outlines", "imgs")
        self.countries_json = join("country-flags-main", "countries.json")

        self.layout = QVBoxLayout()
        self.image_layout = QHBoxLayout()
        self.button_layout = QHBoxLayout()
        self.country_names = self.load_country_names()
        self.maps_dict = self.load_map_paths()

        ctry_img, ctry_name, ctry_idx = self.get_random_country()
        self.country_idx = ctry_idx
        self.flag_widget = FlagWidget(join(self.flags_folder, ctry_img + ".png"), ctry_name, parent=self)
        self.map_widget = FlagWidget(self.maps_dict[ctry_img], ctry_name, parent=self)
        sp = self.map_widget.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self.map_widget.setSizePolicy(sp)
        self.map_widget.hide()
        self.image_layout.addWidget(self.flag_widget)
        self.image_layout.addWidget(self.map_widget)
        self.layout.addLayout(self.image_layout)
        self.name_label = QLabel("?", parent=self)
        self.reveal_button = QPushButton("Reveal", parent=self)
        self.remove_button = QPushButton("Remove", parent=self)
        sp = self.remove_button.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self.remove_button.setSizePolicy(sp)
        self.remove_button.hide()

        self.layout.addWidget(self.name_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.button_layout.addWidget(self.reveal_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.button_layout.addWidget(self.remove_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addSpacing(50)
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

        self.set_connections()

    def set_connections(self):
        self.reveal_button.clicked.connect(self.reveal_country_name)
        self.remove_button.clicked.connect(self.remove_country_from_list)

        self.shortcut = QAction(self)
        self.shortcut.setShortcut(Qt.Key.Key_Space)
        self.shortcut.triggered.connect(self.reveal_button.click)
        self.addAction(self.shortcut)

        self.shortcut = QAction(self)
        self.shortcut.setShortcut(Qt.Key.Key_Backspace)
        self.shortcut.triggered.connect(self.remove_button.click)
        self.addAction(self.shortcut)

    def reveal_country_name(self):
        if self.reveal_mode:
            self.map_widget.show()
            self.reveal_mode = False
            self.name_label.setText(self.flag_widget.ctry_name)
            self.reveal_button.setText("Next")
            self.remove_button.show()
        else:
            self.reveal_mode = True
            ctry_img = self.update_flag_widget()
            self.update_map_widget(ctry_img)
            self.name_label.setText("?")
            self.reveal_button.setText("Reveal")
            self.map_widget.hide()
            self.remove_button.hide()

    def remove_country_from_list(self):
        if len(self.country_names) <= 1:
            return
        self.country_names.pop(self.country_idx)
        self.reveal_country_name()

    def get_random_country(self):
        country_idx = random.randint(0, len(self.country_names) - 1)
        file_name, ctry_name = self.country_names[country_idx]
        self.country_idx = country_idx
        return file_name, ctry_name, country_idx

    def update_flag_widget(self):
        ctry_img, ctry_name, _ = self.get_random_country()
        self.flag_widget.set_flag_path(join(self.flags_folder, ctry_img + ".png"), ctry_name)
        return ctry_img

    def update_map_widget(self, ctry_img):
        self.map_widget.set_flag_path(self.maps_dict[ctry_img], ctry_img)

    def load_country_names(self):
        with open(self.countries_json, "r", encoding="utf-8") as f:
            names_dict = json.load(f)
            return [(key.lower(), value) for key, value in names_dict.items()]

    def load_map_paths(self):
        map_paths = glob(self.maps_folder + "/*")
        maps_dict = {}
        for key, _ in self.country_names:
            for path in map_paths:
                filename = os.path.basename(path)
                if filename.startswith(key):
                    maps_dict[key] = path
                    break
        return maps_dict


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1000, 600)
        self.setMinimumSize(200, 200)
        self.setWindowTitle("Flag Puzzle App")

        close_action = QAction("Close", self)
        close_action.setShortcut(QKeySequence.StandardKey.Close)
        close_action.triggered.connect(self.close)
        self.addAction(close_action)

        self.central_widget = CentralWidget(self)
        self.setCentralWidget(self.central_widget)


def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setFont(QFont("Sans Serif", 50))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
