import smtplib
from email.mime.text import MIMEText
from slackclient import SlackClient


def send_slack_message(args, results):
    slack_token = args.slack_token
    slack_channel = args.slack_channel
    if not slack_channel.startswith('#') and not slack_channel.startswith('@'):
        slack_channel = '#' + slack_channel
    text = "Ratata results for {0}: {1}".format(results['name'], results['summary'])
    sc = SlackClient(slack_token)
    sc.api_call("chat.postMessage", channel=slack_channel, text=text)



def send_email_message(args, results):
    text = """
Greetings human!

Somebody ran the ratata command on %s and specified you as the result recipient.
Here are the results: %s

-- the ratata client
-- https://github.com/City-of-Helsinki/ratata

""" % (results['time'].strftime('%Y-%m-%d %H:%M'), results['summary'])

    msg = MIMEText(text)
    msg['Subject'] = "Results from the ratata test run"
    msg['From'] = 'do-not-reply@ratata.local'
    msg['To'] = args.email_to

    print("Sending [><] report via", args.email_smtp)
    print()
    s = smtplib.SMTP(args.email_smtp)
    s.ehlo()
    s.starttls()
    if args.email_smtp_login:
        user, passw = args.email_smtp_login.split(':')
        s.login(user, passw)
    s.send_message(msg)
    s.quit()

