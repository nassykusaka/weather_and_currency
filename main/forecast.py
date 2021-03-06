# -*- coding: utf-8 -*-
from urllib import request
import json
import datetime
import smtplib


TIMESTAMP = datetime.datetime.today().strftime("%d.%m.%Y %H:%M:%S")
CITIES = {'NYC': 'https://www.theweathernetwork.com/us/api/data/usny0996/ci?ts=1752',
          'SAN FRANCISCO': 'https://www.theweathernetwork.com/us/api/data/usca0987/ci?ts=2152',
          'CHICAGO': 'https://www.theweathernetwork.com/us/api/data/usil0225/ci?ts=2152',
          'MIAMI': 'https://www.theweathernetwork.com/us/api/data/usfl0316/ci?ts=2152'}


def get_html(url):
    response = request.urlopen(url)
    return response.read()


def parse(url):
    json_ = get_html(url)
    result = json.loads(json_)['obs']
    global params
    params = {}

    params['sky'] = result['wxc'] + ' ' + result['wxca']
    params['sunset'] = result['sunrise_time']
    params['sunrise'] = result['sunset_time']
    params['uv'] = result['uv_level_icon']
    params['wind direction'] = result['windDirection_icon']
    params['wind'] = int(result['w'] * 1.6 * 1000 / 3600)  # mph to mps
    params['humidity'] = result['h']
    params['temperature'] = result['t']
    params['feels like'] = result['f']
    params['pressure'] = result['pressure_icon']
    params['changes'] = result['wxsp']

    return params


def advice(params):
    print('Some pieces of advice:')
    temper = int(params['feels like'])
    if temper > 15 and temper < 22:
        print('It is quite warm.')
    elif temper > 22:
        print("It's better to summer wear and take water with you.")
    if int(params['humidity']) > 80:
        print('It may be rainy. Take umbrella.')
    if params['sky'] == 'Clear sunny':
        print('Take sunglasses')
    if params['uv'] == 'high':
        print('Use sun protector cream')
    if params['pressure'] == 'medium-high' or params['pressure'] == 'high':
        print('Be careful, it is high pressure, you may feel headache')
    if params['changes'] == 'PRECIP':
        print('Take umbrella. It is going to be rainy')


def print_weather_forecast(url):
    params = parse(url)
    report = '{:<17}{}C\n{:<17}{}C\n{:<17}{}\n{:<17}{}\n{:<17}{}\n{:<17}{} ' \
             'm/s\n{:<17}{}%\n{:<17}{}\n{:<17}{}\n{:<17}{}\n{:<17}{}' \
             '\n'.format('Temperature:', params['temperature'], 'Feels like:', params['feels like'],
                         'Sky is:', params['sky'], 'UV level:', params['uv'], 'Wind direction:',
                         params['wind direction'], 'Wind:', params['wind'], 'Humidity:', params['humidity'],
                         'Pressure:', params['pressure'], 'Next 3 hours: ', params['changes'],
                         'Sunrise:', params['sunrise'], 'Sunset:', params['sunset'])
    print(report)
    return report


def write_statistic(city):
    with open('weather_stats.txt', 'a+', encoding='utf-8') as f:
        f.write(TIMESTAMP + ' ' + city + ' ' + str(params)+'\n')
        f.close()


def choose_city():
    city_index = input("Please enter number for city\n1 - NYC, NY\n2 - "
                       "San Francisco, CA\n3 - Chicago, IL\n4 - Miami, FL\n")
    if city_index in '1234':
        city_index = int(city_index) - 1
        city = list(CITIES.keys())[city_index]
        return city
    else:
        print('Invalid input data')
        choose_city()


def request_api(city):
    print("{} weather forecast".format(city))
    # print weather forecast and send it to email
    data_to_send = print_weather_forecast(CITIES[city])
    send_email(city, data_to_send)
    advice(parse(CITIES[city]))
    write_statistic(city)


def send_email(city, data):
    conn = smtplib.SMTP('smtp.mail.yahoo.com', 587)
    conn.ehlo()
    conn.starttls()
    try:
        message = 'Subject: weather in %s today\n\n' % city + data
        conn.login('username@yahoo.com', 'password')
        res = conn.sendmail('username@yahoo.com', 'username@yahoo.com', message)
        if len(res) != 0:
            print("Email wasn't send")
    except Exception as e:
        print(e)
        print("Can't connect to email-box")
    finally:
        conn.quit()


def main():
    request_api(choose_city())


if __name__ == '__main__':
    main()


# FIXME: Traceback if you put wrong data to answer - choose a city
# TODO: parse statistic file - build lists of possible values for some parameters
