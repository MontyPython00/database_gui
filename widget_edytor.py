from PySide6.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit, QGridLayout, \
    QMessageBox, QComboBox
from PySide6.QtCore import Qt
from configparser import ConfigParser
import psycopg2


class Edytor(QWidget):
    def __init__(self):
        super().__init__()
        self.wybrana_tablica_db = None
        self.polaczenie_aktywne = False
        self.tablice_bazy_danych = []
        self.pozycje_znalezione = 0
        self.idx_szukaj_dalej = 0
        # Wybieranie dostepnych tablic z bazy danych // funkcje korzystaja z bazy_danych_tab(QComboBox)
        self.baza_danych_tab = QComboBox()

        # Przykladowa tablica przed polaczeniem z baza danych
        self.excel = QTableWidget(self)
        self.excel.setColumnCount(3)
        self.excel.setRowCount(3)
        self.excel.setItem(0, 0, QTableWidgetItem('Przykladowa'))
        self.excel.setItem(0, 1, QTableWidgetItem('Baza danych'))

        # Dodaj rekord
        l_imie_nazwisko = QLabel('Imie i Naziwsko: ')
        self.str_imie_nazwisko = QLineEdit()

        l_wiek = QLabel('Wiek: ')
        self.str_wiek = QLineEdit()

        l_stanowisko = QLabel('Stanowisko: ')
        self.str_stanowisko = QLineEdit()
        przycisk_dodaj_rekord = QPushButton('Dodaj pracownika')
        przycisk_dodaj_rekord.clicked.connect(self.dodaj_pracownika)

        # Wyszukiwarka
        self.txt_wyszukaj = QLineEdit()
        przycisk_wyszukaj = QPushButton('Wyszukaj')
        przycisk_wyszukaj.clicked.connect(self.szukaj)
        self.przycisk_szukaj_dalej = QPushButton('Nastepny rekord')
        self.przycisk_szukaj_dalej.clicked.connect(self.szukaj_dalej)
        self.przycisk_szukaj_dalej.setHidden(True)

        # Przyciski aktualizacja i usun rekord
        przycisk_aktualizuj_excel = QPushButton('Aktualizuj baze')
        przycisk_usun_rekord = QPushButton('Usun rekord')
        przycisk_aktualizuj_excel.clicked.connect(self.aktualizuj_excel)
        przycisk_usun_rekord.clicked.connect(self.usun_rekord)

        # Layout widzetu
        grid_box = QGridLayout()
        grid_box.addWidget(self.excel, 1, 0, 5, 5)
        grid_box.addWidget(l_imie_nazwisko, 2, 6, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        grid_box.addWidget(self.str_imie_nazwisko, 2, 7, Qt.AlignmentFlag.AlignLeft)
        grid_box.addWidget(l_wiek, 3, 6, Qt.AlignmentFlag.AlignLeft)
        grid_box.addWidget(self.str_wiek, 3, 7, Qt.AlignmentFlag.AlignLeft)
        grid_box.addWidget(l_stanowisko, 4, 6, Qt.AlignmentFlag.AlignLeft)
        grid_box.addWidget(self.str_stanowisko, 4, 7, Qt.AlignmentFlag.AlignLeft)
        grid_box.addWidget(przycisk_dodaj_rekord, 5, 6)
        grid_box.addWidget(przycisk_wyszukaj, 6, 0)
        grid_box.addWidget(self.txt_wyszukaj, 6, 1, 1, 3)
        grid_box.addWidget(self.przycisk_szukaj_dalej, 6, 4)
        grid_box.addWidget(przycisk_aktualizuj_excel, 7, 0)
        grid_box.addWidget(przycisk_usun_rekord, 7, 1)
        grid_box.addWidget(self.baza_danych_tab, 0, 6)
        self.setLayout(grid_box)

    def aktualizuj_excel(self):
        config = {}
        parser = ConfigParser()
        parser.read('database.ini')
        if parser.has_section('postgresql'):
            for param in parser.items('postgresql'):
                config[param[0]] = param[1]
        try:
            self.conn = psycopg2.connect(**config)
            self.polaczenie_aktywne = True
            self.cur = self.conn.cursor()

            # Wybor tablicy
            self.cur.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'")
            tablice_bazy_danych_nowe = [tablica[0] for tablica in self.cur.fetchall()]
            if self.tablice_bazy_danych != tablice_bazy_danych_nowe:
                self.tablice_bazy_danych = tablice_bazy_danych_nowe
                for tablica in self.tablice_bazy_danych:
                    self.baza_danych_tab.addItem(tablica)
            self.wybrana_tablica_db = self.baza_danych_tab.currentText()

            # Podliczenie rekordow z bazy danych
            self.cur.execute(f'SELECT count(wiek) FROM {self.wybrana_tablica_db}')
            ilosc_rekordow = self.cur.fetchone()[0]

            # Uzupelnianie tablicy(QTableWidget) danymi z bazy danych
            self.cur.execute(f"SELECT * FROM {self.wybrana_tablica_db}")
            self.nazwy_kolumn = [desc[0] for desc in self.cur.description]
            self.ilosc_kolumn = len(self.nazwy_kolumn)
            self.excel.setColumnCount(self.ilosc_kolumn)
            self.excel.setRowCount(ilosc_rekordow)
            self.excel.setColumnCount(len(self.nazwy_kolumn))
            for idx, nazwa_kolumny in enumerate(self.nazwy_kolumn):
                self.excel.setHorizontalHeaderItem(idx, QTableWidgetItem(nazwa_kolumny))
            rekord = True
            idx = 0
            while rekord:
                rekord = self.cur.fetchone()
                if rekord:
                    idx_danych = 0
                    idx_kolumny = 0
                    for pracownik_dane in rekord:
                        if isinstance(pracownik_dane, int):
                            self.excel.setItem(idx, idx_kolumny, QTableWidgetItem(str(pracownik_dane)))
                        else:
                            self.excel.setItem(idx, idx_kolumny, QTableWidgetItem(pracownik_dane))
                        idx_danych += 1
                        idx_kolumny += 1
                idx += 1

        except (psycopg2.DatabaseError, Exception) as error:
            QMessageBox.warning(self,
                                'Blad',
                                f'{error}')

    def usun_rekord(self):
        if self.polaczenie_aktywne:
            # Identyfikowanie rekordu wzgledem bazy danych // Roznica numerowania
            rekord_wybrany = self.excel.selectedItems()
            usun_rekord = self.excel.currentRow()
            pozycja_rekordu_rzad = rekord_wybrany[0].row()
            txt_komunikat = ''
            dane_z_rekordu = []
            dane_do_query = ''
            if rekord_wybrany:
                # Komunikat dla uzytkownika o rekordach do usuniecia
                for i in range(self.ilosc_kolumn):
                    dane_z_rekordu.append(self.excel.item(pozycja_rekordu_rzad, i).text())
                for idx, nazwa_kolumny in enumerate(self.nazwy_kolumn):
                    txt_komunikat += f'{nazwa_kolumny}: {dane_z_rekordu[idx]}\n'
                    try:
                        if idx == len(self.nazwy_kolumn) - 1:
                            dane_do_query += f"{nazwa_kolumny}={int(dane_z_rekordu[idx])}"
                        else:
                            dane_do_query += f"{nazwa_kolumny}={int(dane_z_rekordu[idx])} AND "
                    except ValueError:
                        if idx == len(self.nazwy_kolumn) - 1:
                            dane_do_query += f"{nazwa_kolumny}='{dane_z_rekordu[idx]}'"
                        else:
                            dane_do_query += f"{nazwa_kolumny}='{dane_z_rekordu[idx]}' AND "
                odpowiedz = QMessageBox.question(self, f'Baza danych', txt_komunikat,
                                                 QMessageBox.Ok | QMessageBox.Cancel)
                if odpowiedz == QMessageBox.Ok:
                    self.excel.removeRow(usun_rekord)
                    self.cur.execute(f'DELETE FROM {self.wybrana_tablica_db} WHERE {dane_do_query}')
                    self.conn.commit()

            else:
                QMessageBox.warning(self, 'Blad', 'Wybierz rekord aby usunac.')

        else:
            QMessageBox.warning(self,
                                'Blad uwierzytelnienia',
                                'Polacz sie z baza danych')

    def dodaj_pracownika(self):
        if self.polaczenie_aktywne:
            try:
                txt_pracownik = self.str_imie_nazwisko.text()
                txt_wiek = int(self.str_wiek.text())
                txt_stanowisko = self.str_stanowisko.text()
                self.cur.execute(
                    f"INSERT INTO {self.wybrana_tablica_db}(imie_nazwisko, wiek, stanowisko) VALUES('{txt_pracownik}', {txt_wiek}, '{txt_stanowisko}')")
                self.conn.commit()
                komunikat = QMessageBox.information(self, 'Baza danych', 'Pomyslnie dodany rekord.', QMessageBox.Ok)
                if komunikat == QMessageBox.Ok:
                    self.str_imie_nazwisko.setText('')
                    self.str_wiek.setText('')
                    self.str_stanowisko.setText('')

            except (psycopg2.DatabaseError, Exception) as error:
                QMessageBox.warning(self, 'Blad', f'{error}')
        else:
            QMessageBox.warning(self,
                                'Blad uwierzytelnienia',
                                'Polacz sie z baza danych')

    def szukaj(self):
        tekst_szukaj = self.txt_wyszukaj.text()
        wyszukane_rekordy = self.excel.findItems(tekst_szukaj, Qt.MatchContains)
        self.pozycje_znalezione = wyszukane_rekordy
        if wyszukane_rekordy:
            rekord = self.pozycje_znalezione[0]
            self.excel.setCurrentItem(rekord)
            if len(self.pozycje_znalezione) > 1:
                self.przycisk_szukaj_dalej.setHidden(False)

    def szukaj_dalej(self):
        #Kontynuacja szukania poprzez indexowanie listy
        ilosc_pozycji = len(self.pozycje_znalezione)
        self.idx_szukaj_dalej += 1
        if self.idx_szukaj_dalej != ilosc_pozycji:
            self.excel.setCurrentItem(self.pozycje_znalezione[self.idx_szukaj_dalej])
        else:
            self.pozycje_znalezione = []
            self.idx_szukaj_dalej = 0
            self.przycisk_szukaj_dalej.setHidden(True)


    def zamknij_polaczenie(self):
        self.conn.close()
        print('Zamknieto polaczenie')
