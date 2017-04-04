This directory contains utility tools from 3rd parties.

Using pygettext to collect marked text to a .pot file
=====================================================
Steps:
1) cd /home/ak/py/cm/html

2) pygettext -o /home/ak/i18n/messages.pot *.py *.ptl case/*.p*
incident/*.p* report/*.p* \
user/*.p* attachment/*.p* feedback/*.p* role/*.p* store/*.p*
mypreference/*.p* ../htmllib/*

Using msgfmt.py to compile .po file to .mo file
===============================================
python2.2 msgfmt.py
