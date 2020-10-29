from asset import KEYWORDS
from scanner import Scanner
from utils import *
import sys





if __name__ == "__main__":

    symbol_table = {}
    for sym in KEYWORDS:
        symbol_table[sym] = []

    scanner = Scanner('input.txt', symbol_table)
    scanner.show_results()