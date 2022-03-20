from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import matplotlib.pyplot as plt
import matplotlib
import csv

from urllib3.filepost import writer

app = Flask(__name__)


def update_cars():
    if not os.path.exists('cars.csv') or (time.time() - os.path.getmtime('cars.csv')) > 600:

        browser = webdriver.Chrome()
        car_list = []
        time.sleep(2)
        next_page = True
        link = 'https://www.sahibinden.com/arazi-suv-pickup-citroen-c3-aircross-1.5-bluehdi-feel'
        while next_page:
            browser.get(link)
            time.sleep(2)
            cars = browser.find_elements(by=By.CSS_SELECTOR, value='.searchResultsItem')
            for c in cars:
                if c.get_attribute('data-id') is None:
                    continue
                else:
                    infos = c.find_elements(by=By.CSS_SELECTOR, value='.searchResultsAttributeValue')
                    price = c.find_elements(by=By.CSS_SELECTOR, value='.searchResultsPriceValue')
                    location = c.find_elements(by=By.CSS_SELECTOR, value='.searchResultsLocationValue')
                    # color = c.find_elements(by=By.CSS_SELECTOR, value='.searchResultColorValue')
                    car_list.append({'year': infos[0].text,
                                     'km': infos[1].text,
                                     'color': infos[2].text,
                                     'price': price[0].text,
                                     'location': location[0].text})

                time.sleep(3)

                next_link = browser.find_elements(by=By.CSS_SELECTOR, value='.prevNextBut')
                next_page = False if len(next_link) == 0 else True
                for n in next_link:
                    if n.get_attribute('title') == 'Sonraki':
                        link = n.get_attribute('href')
                        next_page = True
                    else:
                        next_page = False

        browser.close()

        with open('open.csv', 'w', newline='') as f:
            writer.csvwriter(f)
            writer.writerow(['year', 'km', 'color', 'price', 'location'])
            for car in cars:
                writer.writerow([car['year']], [car['km']], [car['color']], [car['price']], [car['location']])
    else:
        car_list = []
        with open('cars.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    car_list.append({'year': int(row[0]),
                                     'km': int(row[1]),
                                     'color': row[2],
                                     'price': int(row[3]),
                                     'location': row[4]})
                except:
                    continue
        return car_list


# sahibinden üzerinde çalışan bir extension yapılacak
# araba içeren bir sayfaya girildiğinde dersteki grafik oluştursun

@app.route('/image.jpg')
def image():
    car_list = update_cars()
    plt.figure(figsize=(10, 8))
    plt.xlabel('KM')
    plt.ylabel('Price')
    plt.title('Car Data From Sahibinden')
    plt.scatter(list(map(lambda x: x['km'], car_list)), list(map(lambda x: x['price'], car_list)))
    plt.savefig('image.jpg')
    return open('image.jpg', 'rb').read()



@app.route('/')  # function decorator
def index():
    car_list = update_cars()
    return render_template('index.html', title='Data From Sahibinden')  # if you change sth you have to restart the server


if __name__ == '__main__':
    app.run()