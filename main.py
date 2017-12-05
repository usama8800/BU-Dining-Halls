from bs4 import BeautifulSoup
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import smtplib

now = datetime.datetime.now()
main_url = 'http://www.bu.edu/dining/where-to-eat/residence-dining/marciano-commons/menu/?dsd=%d&dsm=%d&dsy=%d' % (
    now.day, now.month, now.year)
filename = 'wants.txt'


def log(arg=''):
    print(arg)
    file = open('log.txt', 'a')
    file.write(arg + '\n')
    file.close()


def read_file():
    file = open(filename, 'r')
    ret = []
    for line in file:
        ret.append(line[:-1])
    file.close()
    return ret


def main():
    soup = BeautifulSoup(str(requests.get(main_url).text), "html.parser")
    meals = soup.select('.mealgroup')

    wants = read_file()
    available = {}

    for i, meal in enumerate(meals):
        mealsoup = BeautifulSoup(str(meal), "html.parser")
        mealstring = str(mealsoup)
        mealgroup = mealstring.find('class="title">')
        mealgroup = mealstring[mealgroup + 14:]
        mealgroup = mealgroup[:mealgroup.find('<')]
        available[mealgroup] = {}
        for station in mealsoup.select('.items'):
            stationsoup = BeautifulSoup(str(station), "html.parser")
            station = BeautifulSoup(str(station.parent), "html.parser")
            station = station.select('.item-title-name')[0].text
            available[mealgroup][station] = []
            for item in stationsoup.select('.item-menu-name'):
                # if item.text in wants:
                available[mealgroup][station].append(item.text)

    fromaddr = "usama8800@gmail.com"
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(fromaddr, "nqfkaexanhjlbwcw")
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = fromaddr
    msg['Subject'] = 'Daily Dining Hall'
    body = ''
    for meal in available:
        found_meal = False
        for station in available[meal]:
            found_station = False
            for item in available[meal][station]:
                if not found_meal:
                    body += '<h1 style="margin:0;padding:0">' + meal + '</h1>'
                    found_meal = True
                if not found_station:
                    body += '<h3 style="padding-left:2%;margin-bottom:.2%">' + station + '</h3>'
                    found_station = True
                body += '<span style="padding-left:4%">' + item + '</span><br><br>'
        if found_meal:
            body += '<br>'
    msg.attach(MIMEText(body, 'html'))
    server.sendmail(fromaddr, fromaddr, msg.as_string())


main()
