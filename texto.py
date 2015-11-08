# -*- coding: UTF-8 -*-
#!/usr/bin/env python

'''
Texto! - small Python script that sends SMS via https://bramka.play.pl

Copyright (C) 2015  Marcin Możejko

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
from argparse import ArgumentParser

# PL PLAY
from operators.pl.Play import *

class Texto:
    def __init__(self):
        pass

    def Main(self):

        # Parsing command-line arguments
        parser = ArgumentParser(prog='texto')
        parser.add_argument('login', help='Phone number or email to login')
        parser.add_argument('passwd', help='Password')
        parser.add_argument('recipient', help='Message recipient')
        parser.add_argument('message', help='Message content')
        args = parser.parse_args()


        sms = Play(args.login, args.passwd)
        sms.SendMessage(args.recipient, args.message)

if __name__ == "__main__":
    texto = Texto()
    texto.Main()
