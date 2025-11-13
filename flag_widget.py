from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class FlagWidget(QWidget):
    def __init__(self, flag_path: str, ctry_name: str, parent=None):
        super().__init__(parent)
        self.flag_path = flag_path
        self.ctry_name = ctry_name

        self.pixmap_original = QPixmap(self.flag_path)

        self.img_container = QLabel(self)
        self.img_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.img_container)
        self.setLayout(self.layout)

        self.update_pixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_pixmap()

    def set_flag_path(self, flag_path: str, ctry_name: str):
        """Update the image path and reload the pixmap."""
        if flag_path == self.flag_path:
            return
        self.flag_path = flag_path
        self.ctry_name = ctry_name
        self.pixmap_original = QPixmap(self.flag_path)
        self.update_pixmap()

    def update_pixmap(self):
        if self.pixmap_original.isNull():
            self.img_container.clear()
            return

        available = self.img_container.size()
        if available.width() <= 0 or available.height() <= 0:
            return

        scaled = self.pixmap_original.scaled(
            available,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.img_container.setPixmap(scaled)
