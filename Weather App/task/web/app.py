from random import random, randint

from flask import request, redirect

from flask import Flask, render_template, flash, jsonify
import sys
import requests
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'So-Seckrekt'


class City(db.Model):
    __tablename__ = 'weather'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique = True, nullable=False)


@app.route('/')
def index():
    db.create_all()
    wlist = []
    for city in City.query.all():
        name = city.name
        id = city.id
        r = requests.get('https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(name,
                                                                                               '6827a833a0e047cb26830a2868b85b30'))
        data = r.json()

        degree = data["main"]["temp"]
        state = data["weather"][0]["main"]
        city = data["name"]
        w = {'city': city, 'degree': degree, 'state': state, 'id': id}
        wlist.append(w)
    return render_template('index.html', weather=wlist)

@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')

@app.route('/add', methods=['GET', 'POST'])
def add_city():
    name = request.form['city_name']
    existing_city = City.query.filter_by(name=name).first()
    r = requests.get('https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(name,
                                                                                            '6827a833a0e047cb26830a2868b85b30'))
    data = r.json()
    if "main" not in data:
        flash("The city doesn't exist!")
    elif not existing_city:
        weather = City(id=randint(1, 10000), name=name)
        db.session.add(weather)
        db.session.commit()
    else:
        flash("The city has already been added to the list!")
    return redirect('/')


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
