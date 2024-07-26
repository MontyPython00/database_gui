from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QMessageBox
from widget_lacznik import Lacznik
from widget_edytor import Edytor


class MatkaTablica(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1024, 700)
        self.setWindowTitle('Edytor bazy danych')
        self.tablica_lacznik = Lacznik()
        self.tablica_edytor = Edytor()
        #Zakladki
        matka_tablica = QTabWidget(self)
        matka_tablica.addTab(self.tablica_lacznik, 'Dostep do bazy')
        matka_tablica.addTab(self.tablica_edytor, 'Edytor bazy danych')
        matka_tablica.setStyleSheet('QTabWidget {alignment:center}')
        vbox = QVBoxLayout()
        vbox.addWidget(matka_tablica)

        self.setLayout(vbox)


    def closeEvent(self, event):
        if self.tablica_edytor.polaczenie_aktywne:
            self.tablica_edytor.zamknij_polaczenie()
            zapisz_dane_komunikat = QMessageBox.question(self, 'Baza danych', 'Zapisac dane do autoryzacji polaczenia?', QMessageBox.Ok | QMessageBox.Cancel)
            if zapisz_dane_komunikat != QMessageBox.Ok:
                with open('database.ini', 'w') as file:
                    file.write('')


