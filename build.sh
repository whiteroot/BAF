#!/bin/bash

# build an executable

rm -rf dist build
pyinstaller run.py -n baf --onefile

