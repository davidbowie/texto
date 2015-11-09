#Texto!

Small script logs into sms gate https://bramka.play.pl and sends message.
It handles captcha.

Usage: 

>`$ texto.py [-h] [-c CAPTCHA] login passwd recipient message`



|:-------:|------------------------------|
|login    |phone number or email to login|
|passwd   |password                      |
|recipient|message recipient             |
|message  |message content               |

options:

|-----------------------------|-------------------------------|
|-h, --help                   |show help message and exit     |
|-c CAPTCHA, --captcha CAPTCHA|command viewing captcha        |


for example:

>`$ texto.py -c /usr/bin/ristretto 505123456 mypassword1 +48123456789 "This is a short text message!"`