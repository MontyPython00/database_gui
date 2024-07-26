from PySide6.QtWidgets import QWidget, QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout, QLabel, \
    QLineEdit
from configparser import ConfigParser
import psycopg2


class Lacznik(QWidget):
    def __init__(self):
        super().__init__()
        #GUI polacz z baza danych
        l_host = QLabel('Host:')
        self.str_host = QLineEdit()
        self.str_host.setFixedSize(170, 26)

        l_port = QLabel('Port:')
        self.str_port = QLineEdit()
        self.str_port.setFixedSize(170, 26)

        l_nazwa_bazy = QLabel('Nazwa bazy danych: ')
        self.str_nazwa_bazy = QLineEdit()
        self.str_nazwa_bazy.setFixedSize(170, 26)

        l_uzytkownik = QLabel('Uzytkownik: ')
        self.str_uzytkownik = QLineEdit()
        self.str_uzytkownik.setFixedSize(170, 26)

        l_haslo = QLabel('Haslo:')
        self.str_haslo = QLineEdit()
        self.str_haslo.setFixedSize(170, 26)

        przycisk_polacz = QPushButton('Polacz')
        przycisk_polacz.clicked.connect(self.sprawdzian_polaczenia)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(l_host)
        hbox1.addWidget(self.str_host)
        hbox1.addStretch()

        hbox2 = QHBoxLayout()
        hbox2.addWidget(l_port)
        hbox2.addWidget(self.str_port)
        hbox2.addStretch()

        hbox3 = QHBoxLayout()
        hbox3.addWidget(l_nazwa_bazy)
        hbox3.addWidget(self.str_nazwa_bazy)
        hbox3.addStretch()

        hbox4 = QHBoxLayout()
        hbox4.addWidget(l_uzytkownik)
        hbox4.addWidget(self.str_uzytkownik)
        hbox4.addStretch()

        hbox5 = QHBoxLayout()
        hbox5.addWidget(l_haslo)
        hbox5.addWidget(self.str_haslo)
        hbox5.addStretch()

        v_box = QVBoxLayout()
        v_box.addLayout(hbox1)
        v_box.addLayout(hbox2)
        v_box.addLayout(hbox3)
        v_box.addLayout(hbox4)
        v_box.addLayout(hbox5)
        v_box.addWidget(przycisk_polacz)

        self.setLayout(v_box)

    def sprawdzian_polaczenia(self):
        host = self.str_host.text()
        nazwa_bazy = self.str_nazwa_bazy.text()
        uzytkownik = self.str_uzytkownik.text()
        haslo = self.str_haslo.text()
        port = self.str_port.text()
        with open('database.ini', 'w') as file:
            file.write(
                f'''[postgresql]\ndbname={nazwa_bazy}\nuser={uzytkownik}\npassword={haslo}\nhost={host}\nport={port}''')

        parser = ConfigParser()
        parser.read('database.ini')
        config = {}
        if parser.has_section('postgresql'):
            for param in parser.items('postgresql'):
                config[param[0]] = param[1]
        try:
            conn = psycopg2.connect(**config)
            QMessageBox.about(self,
                              'Polaczenie z baza danych',
                              'Wprowadziles poprawne dane')
            conn.close()
        except (psycopg2.DatabaseError, Exception) as error:
            QMessageBox.warning(self,
                                'Wystapil blad',
                                f'{error}')


