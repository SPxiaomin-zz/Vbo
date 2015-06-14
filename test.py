from flask import Flask
from flask.ext.mail import Mail, Message

# configuration
DEBUG = True

MAIL_SERVER='smtp.qq.com'
MAIL_PORT=587
MAIL_USE_TLS = True 
MAIL_USE_SSL= False
MAIL_USERNAME = '3013366498@qq.com'
MAIL_PASSWORD = '123456789.a'

app = Flask(__name__)
app.config.from_object(__name__)
mail = Mail(app)

@app.route('/minfo')
def send_mail():
    msg = Message(
      'Hello',
       sender='3013366498@qq.com',
       recipients=
       ['3013366498@qq.com'])
    msg.body = "This is the email body"
    mail.send(msg)
    return "Sent"

if __name__ == '__main__':
    app.run()
