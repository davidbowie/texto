# -*- coding: UTF-8 -*-

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

# Play.py - class handling logging to play.pl

import pycurl, os
from StringIO import StringIO
from bs4 import BeautifulSoup
from urllib import urlencode
from sys import stdin

class Play:
    def __init__(self, login, passwd):
        self.debug = 0

        self.START_URL = 'https://bramka.play.pl'
        self.login = login
        self.passwd = passwd
        # Indicates login status
        self.logged = 0
        # Current request URL
        self.url = self.START_URL
        self.logoutURL = ''

        # HTML Content of main message compose page
        self.composeContent = None

        # SMS sending form
        self.messageForm = {'recipients':'', 'content_in':'', 'czas':'',
                            'inputCaptcha':'', 'content_out':'', 'templateId':'',
                            'sendform':'', 'composedMsg':'', 'randForm':'',
                            'old_signature':'', 'old_content':'',
                            'MessageJustSent':''}

    @staticmethod
    def PreparePostRequest(curlobj, url, postFields, buffer, follow):
        """Setting options for application/x-www-form-urlencoded"""
        curlobj.setopt(curlobj.URL, url)
        curlobj.setopt(curlobj.POSTFIELDS, postFields)
        curlobj.setopt(curlobj.WRITEDATA, buffer)
        curlobj.setopt(pycurl.FOLLOWLOCATION, follow)

    @staticmethod
    def PrepareMultipartRequest(curlobj, url, parts, buffer, follow):
        """Setting options for multipart/form-data"""
        curlobj.setopt(curlobj.URL, url)
        curlobj.setopt(curlobj.HTTPPOST, parts)
        curlobj.setopt(pycurl.FOLLOWLOCATION, follow)

    @staticmethod
    def PerformRequest(curlobj, url):
        """Performing request"""

        try:
            curlobj.perform()
        except:
            print "Error sending request to %s" % (url)
            return 0

        return 1

    def Login(self):
        """Login"""

        # If already logged, quitting
        if self.logged:
            return

        # Setting up cURL request, will save response to buffer

        buffer = StringIO()
        self.c = pycurl.Curl()
        self.c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0')
        self.c.setopt(self.c.URL, self.url)
        self.c.setopt(pycurl.FOLLOWLOCATION, 1)
        self.c.setopt(pycurl.SSL_VERIFYPEER, 1)
        self.c.setopt(pycurl.SSL_VERIFYHOST, 2)
        self.c.setopt(pycurl.COOKIEFILE, 'cookie.txt')
        self.c.setopt(pycurl.COOKIEJAR, 'cookies.txt')
        self.c.setopt(self.c.WRITEDATA, buffer)

        print "Logging in..."

        # Sending request and check for errors
        if not self.PerformRequest(self.c, self.url):
            return

        # Retrieving buffer content
        htmlResponse = buffer.getvalue()
        # Clearing buffer
        buffer.truncate(0)

        # Parsing response using BeautifulSoup
        soup = BeautifulSoup(htmlResponse, 'html5lib')

        try:
            temp_url = self.url
            self.url = soup.form['action']
            samlRequestField = soup.find("input", attrs={'name': 'SAMLRequest', 'type': 'hidden'})['value']
            targetField = soup.find("input", attrs={'name': 'target', 'type': 'hidden'})['value']
        except:
            print "Error parsing response from %s" % (temp_url)
            return
        # Preparing POST data
        postData = {'SAMLRequest': samlRequestField, 'target': targetField}
        postFields = urlencode(postData)

        # Preparing POST request
        self.PreparePostRequest(self.c, self.url, postFields, buffer, 0)

        # Sending request and check for errors
        if not self.PerformRequest(self.c, self.url):
            return

        # Getting response
        htmlResponse = buffer.getvalue()
        buffer.truncate(0)

        # Parsing
        soup = BeautifulSoup(htmlResponse, 'html5lib')

        try:
            gotoField = soup.find("input", attrs={'name': 'goto'})['value']
            gotoOnFailField = soup.find("input", attrs={'name': 'gotoOnFail'})['value']
            sunQueryField = soup.find("input", attrs={'name': 'SunQueryParamsString'})['value']
            encodedField = soup.find("input", attrs={'name': 'encoded'})['value']
            charsetField = soup.find("input", attrs={'name': 'gx_charset'})['value']
        except:
            print "Error parsing response from %s" % (self.url)
            return

        # Preparing POST data
        postData = {'IDToken1': self.login, 'IDToken2': self.passwd,
                    'IDButton': 'Zaloguj', 'goto': gotoField,
                    'gotoOnFail': gotoOnFailField,
                    'SunQueryParamsString': sunQueryField,
                    'encoded': encodedField, 'gx_charset': charsetField}
        postFields = urlencode(postData)

        self.url = 'https://logowanie.play.pl/opensso/logowanie'

        # Preparing POST request
        self.PreparePostRequest(self.c, self.url, postFields, buffer, 1)

        # Sending request and check for errors
        if not self.PerformRequest(self.c, self.url):
            return

        # Getting response
        htmlResponse = buffer.getvalue()
        buffer.truncate(0)

        # Parsing
        soup = BeautifulSoup(htmlResponse, 'html5lib')

        if soup.find("title", string="P4 SSO (Nieudane logowanie)"):
            print "Login or password incorrect!"
            return

        try:
            temp_url = self.url
            self.url = soup.form['action']
            samlResponseField = soup.find("input", attrs={'name': 'SAMLResponse', 'type': 'HIDDEN'})['value']
            targetField = soup.find("input", attrs={'name': 'target', 'type': 'HIDDEN'})['value']
        except:
            print "Error parsing response from %s" % (temp_url)
            return

        # Preparing POST data
        postData = {'SAMLResponse': samlResponseField, 'target': targetField}
        postFields = urlencode(postData)

        # Preparing POST request
        self.PreparePostRequest(self.c, self.url, postFields, buffer, 0)

        # Sending request and check for errors
        if not self.PerformRequest(self.c, self.url):
            return

        # Getting response
        htmlResponse = buffer.getvalue()
        buffer.truncate(0)

        # Parsing
        soup = BeautifulSoup(htmlResponse, 'html5lib')

        try:
            samlResponseField = soup.find("input", attrs={'name': 'SAMLResponse', 'type': 'hidden'})['value']
        except:
            print "Error parsing response from %s" % (self.url)
            return

        # Preparing POST data
        postData = {'SAMLResponse': samlResponseField}
        postFields = urlencode(postData)

        self.url = 'https://bramka.play.pl/composer/j_security_check'

        # Preparing POST request
        self.PreparePostRequest(self.c, self.url, postFields, buffer, 1)

        # Sending request and check for errors
        if not self.PerformRequest(self.c, self.url):
            return

        # Getting response
        htmlResponse = buffer.getvalue()
        buffer.truncate(0)

        # Parsing
        soup = BeautifulSoup(htmlResponse, 'html5lib')

        if self.debug:
            outfile = open("debug_glowna.html", "w")
            outfile.write(BeautifulSoup(htmlResponse, 'html5lib').prettify().encode('UTF-8'))
            outfile.close()

        try:
            self.logoutURL = soup.find("a", string="Wyloguj")['href']
        except:
            print "Error parsing response from %s" % (temp_url)
            return



        # Checking if logged properly
        if self.logoutURL:
            print "Login succesfull"
            self.logged = 1
            self.composeContent = htmlResponse
            self.url = 'https://bramka.play.pl/composer/public/editableSmsCompose.do'
        else:
            self.url = self.START_URL
            print "Login failed"

    def Logout(self):
        """Logging out"""

        # If not logged
        if not self.logged:
            print "Logout error: not logged in!"
            return

            # Performing logout

        buffer = StringIO()

        print "Logging out..."

        # cURL request
        self.c.setopt(self.c.URL, self.logoutURL)
        self.c.setopt(pycurl.FOLLOWLOCATION, 1)
        self.c.setopt(self.c.WRITEDATA, buffer)

        # Sending request and check for errors
        if not self.PerformRequest(self.c, self.logoutURL):
            return

        # Response
        htmlResponse = buffer.getvalue()
        buffer.truncate(0)

        # Parsing
        soup = BeautifulSoup(htmlResponse, 'html5lib')

        if self.debug:
            outfile = open("debug_logout.html", "w")
            outfile.write(BeautifulSoup(htmlResponse, 'html5lib').prettify().encode('UTF-8'))
            outfile.close()

        temp_url = soup.form['action']
        self.url = soup.find("img", attrs={'height': '0'})['src']

        # IMG Request
        self.c.setopt(self.c.URL, self.url)
        self.c.setopt(pycurl.FOLLOWLOCATION, 1)
        self.c.setopt(self.c.WRITEDATA, buffer)

        # Sending request and check for errors
        if not self.PerformRequest(self.c, self.url):
            return

        htmlResponse = buffer.getvalue()
        buffer.truncate(0)

        self.url = temp_url

        # POST Request
        self.PreparePostRequest(self.c, self.url, '', buffer, 0)

        # Sending request and check for errors
        if not self.PerformRequest(self.c, self.url):
            return

        htmlResponse = buffer.getvalue()
        buffer.truncate(0)

        if self.debug:
            outfile = open("debug_wylogowano.html", "w")
            outfile.write(htmlResponse)
            outfile.close()

        # Checking if logged out properly
        if htmlResponse.find('Strona G&#322;&oacute;wna - Play'):
            print("Logout succesfull")
            self.logged = 0
        else:
            print("Logout failed!")

        self.c.close()

        self.url = self.START_URL

    def SendMessage(self, phoneno, message, command, dirname):
        """Method logs in, sends SMS, logs out"""

        self.Login()

        if not self.logged:
            print "Error sending message!"
            return

        soup = BeautifulSoup(self.composeContent, 'html5lib')

        messageJustSent = soup.find('input', attrs={'name':'MessageJustSent'})['value']

        try:
            captchaURL = self.START_URL + soup.find('img', id='imgCaptcha')['src']
            self.existCaptcha = 1
            print "Captcha!"
        except:
            self.existCaptcha = 0

        if self.existCaptcha:
            self.c.setopt(self.c.URL, captchaURL)
            self.c.setopt(pycurl.HTTPGET, 1)
            with open(dirname + '/captcha.jpg', 'w') as fcaptcha:
                self.c.setopt(self.c.WRITEFUNCTION, fcaptcha.write)
                if not self.PerformRequest(self.c, captchaURL):
                    print "Error downloading captcha!"
                    fcaptcha.close()
                    self.Logout()
                    return
                else:
                    fcaptcha.close()
                    os.system(command + " " + dirname + "/captcha.jpg 2>/dev/null &")
                    print "Captcha stored in %s" % (dirname + '/captcha.jpg')
                    print "Enter captcha:"
                    captcha = stdin.readline().rstrip('\n')
                    self.messageForm['inputCaptcha'] = captcha




        print "Sending message..."

        msg = message

        self.messageForm['recipients'] = phoneno
        self.messageForm['randForm'] = soup.find('input', attrs={'name':'randForm'})['value']
        self.messageForm['content_in'] = msg
        self.messageForm['content_out'] = msg
        self.messageForm['old_content'] = ''
        self.messageForm['sendform'] = 'on'
        self.messageForm['czas'] = '0'
        self.messageForm['MessageJustSent'] = messageJustSent

        postFields = urlencode(self.messageForm)
        buffer = StringIO()
        self.PreparePostRequest(self.c, self.url, postFields, buffer, 0)

        if not self.PerformRequest(self.c, self.url):
            return

        htmlResponse = buffer.getvalue()
        buffer.truncate(0)

        soup = BeautifulSoup(htmlResponse, 'html5lib')

        # Checking message sent flag #MessageJustSent
        try:
            if soup.find("input", attrs={'name': 'MessageJustSent'})['value'] == "false":
                print "Error sending message!"
                self.Logout()
                return
        except:
            pass

        if self.debug:
            outfile = open("debug_confirm.html", "w")
            outfile.write(soup.prettify().encode('UTF-8'))
            outfile.close()


        parts = [('SMS_SEND_CONFIRMED.x', '0'), ('SMS_SEND_CONFIRMED.y', '0')]
        self.PrepareMultipartRequest(self.c, self.url, parts, buffer, 0)

        if not self.PerformRequest(self.c, self.url):
            return

        htmlResponse = buffer.getvalue()
        buffer.truncate(0)

        if self.debug:
            outfile = open("debug_glowna2.html", "w")
            outfile.write(BeautifulSoup(htmlResponse, 'html5lib').prettify().encode('UTF-8'))
            outfile.close()

        self.composeContent = htmlResponse

        print "Message sent successfully!"

        self.Logout()