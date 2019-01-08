from flask import render_template
import sqlalchemy
from demitaja.database import db_session
from demitaja.models import Posting, City, Technology
from demitaja import app
from demitaja.utils import queries


@app.route('/')
def home():
    return 'Hello world!'


@app.route('/summary')
def summary():
    req_city = 'Warsaw'
    req_tech = 'Django'
    techs = db_session.execute(queries.techs).fetchall()
    cities = db_session.execute(queries.cities).fetchall()
    city = db_session.execute(queries.city, {'city': req_city}).fetchone()
    if not city:
        city = (req_city, 0)
    tech = db_session.execute(queries.tech, {'tech': req_tech}).fetchone()
    if not tech:
        tech = (req_tech, 0)
    cities_tech = db_session.execute(queries.cities_tech, {'tech': req_tech}).fetchall()
    techs_city = db_session.execute(queries.techs_city, {'city': req_city}).fetchall()
    tech_city = db_session.execute(queries.tech_city, {'city': req_city, 'tech': req_tech}).fetchone()
    if not tech_city:
        tech_city = (req_tech, req_city, 0)
    techs_tech = db_session.execute(queries.techs_tech, {'tech': req_tech}).fetchall()
    techs_tech_city = db_session.execute(queries.techs_tech_city, {'city': req_city, 'tech': req_tech}).fetchall()
    return render_template('market-summary.html',
                           req_city=req_city,
                           req_tech=req_tech,
                           techs=techs,
                           cities=cities,
                           city=city,
                           tech=tech,
                           cities_tech=cities_tech,
                           techs_city=techs_city,
                           tech_city=tech_city,
                           techs_tech=techs_tech,
                           techs_tech_city=techs_tech_city)
