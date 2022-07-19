import sys
import random
from datetime import datetime
from pathlib import Path
from string import ascii_uppercase

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *


LETTERS = set(ascii_uppercase.replace('Q', '').replace('C', ''))
SINGLE_VOWELS = set('AEIOU')
CONSONANTS = LETTERS.difference(SINGLE_VOWELS).union({'Ch', 'Sh', 'Th'})
DIPHTONGS = {'Ai', 'Oi', 'Ow'}
VOWELS = SINGLE_VOWELS.union(DIPHTONGS)


def word(vowels: list[str] = ['A', 'U', 'I', 'Ai', 'Ow'], consonants: list[str]
         = ['B', 'G', 'D'], n_syl: int | None = None) -> str:
    """Generate a word of one to three syllables, which are themselves composed
    of all possible consonant-vowel and single-vowel permutations.

    Args:
        vowels (list[str], optional): A list of vowels used to make syllables.
            Accepts single vowels, including y, and all non-repetitive
            diphthongs of single vowels, (not 'aa', 'ee'). Defaults to
            ['A', 'U', 'I', 'Ai', 'Au'].
        consonants (list[str], optional): A list of consonants used to make
            syllables. Accepts single consonants plus: 'ch', 'sh', 'th'.
            Defaults to  ['B', 'G', 'D'].
        n_syl (int | None, optional): The integer number of syllables in
            the word, from one to three. Negative numbers are interpreted as
            their absolute values. Numbers greater than 3 are interpreted
            modulo 3. The default, None, or 0, return a word with a random
            number of either one, two, or three syllables.

    Returns:
        str: A word of `n_syl` syllables, composed of `consonants` and `vowels`
        in CV or V permutations, with syllables separated by hyphens.
    """

    vowels = [v[:2] for v in vowels if len(v) > 2]
    vowels = [v.capitalize() for v in vowels]
    vowels = list(VOWELS.intersection(vowels))
    if not vowels:
        vowels = ['A', 'U', 'I', 'Ai', 'Au']

    for c in consonants:
        if c.lower() not in CONSONANTS:
            consonants.remove(c)
        c = c.capitalize()
    if not consonants:
        consonants = ['B', 'G', 'D']

    cv_syl = [c + v.lower() for c in consonants for v in vowels]
    all_syl = cv_syl + vowels

    if n_syl is None:
        n_syl = random.randint(1, 3)

    if n_syl == 0:
        n_syl = random.randint(1, 3)

    if n_syl < 0:
        n_syl = abs(n_syl)

    if n_syl > 3:
        n_syl = n_syl % 3

    text = ''
    i = 0
    while i < n_syl:
        if text == '' or text[-1].upper() not in VOWELS:
            text += random.choice(all_syl)
        else:
            text += random.choice(cv_syl)
        i += 1

    return text


def line() -> str:
    """Generate a line of 3-5 words, of up to 20 characters.

    Returns:
        str: A line of words up to 20 characters long, contructed from
        available CV and/or V syllables.
    """
    n_words = random.randint(3, 5)

    text = ''
    i = 0
    while i < n_words:
        text += word()
        if len(text) < 20:
            text += ' '
        i += 1

    if len(text) > 20:
        text = text[:text.rfind(' ')]

    return text


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "Abugida 3: Abugida Babalu (Einstürzende Zikkuraten)")
        self.setGeometry(50, 100, 1200, 700)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        log_path = Path('./abugida_logs')
        if not log_path.exists():
            log_path.mkdir()
        now = datetime.now().strftime('%Y-%m-%d-%H:%M')
        log_name = 'babalu_' + now
        self.log_file = log_path/log_name

        self.vow_active = []
        self.con_active = []

        select = QGridLayout()
        layout.addLayout(select)

        select_lab = QLabel(' ')
        select_font = select_lab.font()
        select_font.setBold(True)
        select_font.setPixelSize(48)

        select_ncol = 11

        # Vowels in one row
        select_vlab = QLabel('Vowels/Diphthongs')
        select_vlab.setFont(select_font)
        select.addWidget(select_vlab, 0, 0, 1, select_ncol)
        self.vow_cb = []
        for n, v in enumerate(sorted(VOWELS)):
            exec("cb_{} = QCheckBox('{}')".format(v, v))
            exec("cb_{}.stateChanged.connect(self.update_vowels)".format(v))
            exec("select.addWidget(cb_{}, 1, {})".format(v, n))
            exec("self.vow_cb.append(cb_{})".format(v))

        # Consonants in two rows
        select_clab = QLabel('Consonants')
        select_clab.setFont(select_font)
        select.addWidget(select_clab, 2, 0, 1, select_ncol)
        self.con_cb = []
        for n, c1 in enumerate(sorted(CONSONANTS)[:select_ncol]):
            exec("cb_{} = QCheckBox('{}')".format(c1, c1))
            exec("cb_{}.stateChanged.connect(self.update_cons)".format(c1))
            exec("select.addWidget(cb_{}, 3, {})".format(c1, n))
            exec("self.con_cb.append(cb_{})".format(c1))
        for n, c2 in enumerate(sorted(CONSONANTS)[select_ncol:]):
            exec("cb_{} = QCheckBox('{}')".format(c2, c2))
            exec("cb_{}.stateChanged.connect(self.update_cons)".format(c2))
            exec("select.addWidget(cb_{}, 4, {})".format(c2, n))
            exec("self.con_cb.append(cb_{})".format(c2))

        titles = ['Abugida Babalu', 'Einstüzende Zikkuraten']
        self.label = QLabel(random.choice(titles))
        lab_font = self.label.font()
        lab_font.setPixelSize(150)
        lab_font.setBold(True)
        lab_font.setFamily('Helvetica Ultra Compressed')
        self.label.setFont(lab_font)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedWidth(1150)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.btn = QPushButton(u'\u21BB')
        self.btn.clicked.connect(self.generate)
        btn_font = self.btn.font()
        btn_font.setPixelSize(120)
        btn_font.setBold(True)
        self.btn.setFont(btn_font)
        self.btn.setFixedWidth(150)
        layout.addWidget(self.btn, alignment=Qt.AlignCenter)

    def generate(self):
        this_line = line()
        self.label.setText(this_line)
        # with open(self.log_file, 'a') as f:
        #     f.write(this_line + '\n')

    def update_vowels(self):
        self.vow_active.clear()
        for cb in self.vow_cb:
            if cb.isChecked():
                self.vow_active.append(cb.text())
        print(self.vow_active)

    def update_cons(self):
        self.con_active.clear()
        for cb in self.con_cb:
            if cb.isChecked():
                self.con_active.append(cb.text())
        print(self.con_active)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
