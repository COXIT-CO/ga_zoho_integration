"""Send email to user accounts"""
import smtplib
import json


def sign_in_email_value():
    """"read parameters from json file"""
    try:
        with open("emailnoti.json", "r") as read_file:
            data = json.load(read_file)
            return data
    except IOError:
        print "E-mail data not found. Please check if u have 'emailnoti.json' in this directory.\
         In this file u have to write your email date"
    return None


def send_e_mail(to_email):
    """"send email with following parameters"""
    date_noti_mail = sign_in_email_value()
    if date_noti_mail is None:
        return False

    gmail_user = date_noti_mail["login"]
    to_email_send = to_email
    gmail_pwd = date_noti_mail["password"]

    smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(gmail_user, gmail_pwd)
    header = 'To:' + to_email_send + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:ALERT \n'
    print header
    msg = header + '\n SCRIPT STOPED! PLEASE PAY ATTENTION TO START SCRIPT AGAIN \n\n'
    smtpserver.sendmail(gmail_user, to_email_send, msg)
    smtpserver.close()
    return True
