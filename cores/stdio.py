#!/usr/bin/python
from sys import stdout
from time import sleep
import os


class Clear:
    os.system("cls" if os.name == "nt" else "clear")


class StrObject:
    def Typewriter(text):
        for c in text:
            stdout.write(c)
            stdout.flush()
            sleep(0.0002)
        print()
