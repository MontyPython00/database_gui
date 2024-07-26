from PySide6.QtWidgets import QApplication
from widget_matka import MatkaTablica
import sys


app = QApplication(sys.argv)

widget = MatkaTablica()
widget.show()

sys.exit(app.exec())