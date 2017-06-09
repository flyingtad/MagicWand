#!/usr/bin/python

from Wand import Wand

def main():
    wand = Wand()
    wand.detectSpells(20)

if __name__ == '__main__':
    main()

