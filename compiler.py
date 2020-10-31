from assets import KEYWORDS
from scanner import Scanner
from parser import *
from utils import *
import sys

""""
Arghavan Rezvani - 96101657
Mohammad Amin Ghasemzade - 97110296
"""



if __name__ == "__main__":

    symbol_table = {}
    for sym in KEYWORDS:
        symbol_table[sym] = []

    scanner = Scanner('input.txt', symbol_table)
    parser = Parser(scanner)
    parser.parse()
    parser.write_parse_tree_to_file()
    parser.write_syntax_errors_to_file()