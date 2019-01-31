# -*- coding: utf-8 -*- python
import unicodedata
from demitaja.models import Posting, City, Technology, Salary
from demitaja.database import db_session
from demitaja.utils import queries


def check_item(request, item_type):
    """"Check if item was requested; if so, check if item is in database

    Args:
        request (Request object)
        item_type (str): type of item to be checked;
            must be either tech or city

    Returns:
         normalized name of the tech (str)
         database name of the tech (str)
         number of postings with the tech as must (int)
    """
    name_ascii = normalize_string(request.args.get('req_' + item_type, ''))
    if not name_ascii:
        return None, None, 0
    query = getattr(queries, item_type)
    item = db_session.execute(query, {item_type: name_ascii}).fetchone()
    if not item:
        return name_ascii, None, 0
    return name_ascii, item[0], item[1]


def normalize_string(s):
    """Normalize string
    Return lowercase ascii version of the input string
    """
    s = s.lower().replace('ł', 'l')
    # unicodedata.normalize('NFD', s) decomposes each special character
    # in the input string into letter and diacritic.
    # Diacritics belong to the Mn (Mark, nonspacing) category.
    # Normalization does no work for ł.
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))


def create_posting(posting_d):
    """Add posting with all its relationships to the database"""
    # check if this is a new posting
    posting = get_posting(posting_d['web_id'])
    if posting:
        print('Posting already in the db')
        return
    # extract cities, technologies and salaries
    p_cities = posting_d.pop('cities')
    p_techs_must = posting_d.pop('techs_must')
    p_techs_nice = posting_d.pop('techs_nice')
    p_salaries = posting_d.pop('salaries')
    p_salary_currency = posting_d.pop('salary_currency')
    p_salary_period = posting_d.pop('salary_period')
    # insert posting into the postings table
    posting = Posting(**posting_d)
    db_session.add(posting)
    db_session.commit()
    # append cities and technologies to the posting
    for name in p_cities:
        city = get_city(name)
        posting.cities.append(city)
    for tech in p_techs_must:
        must = get_tech(tech)
        posting.techs_must.append(must)
    for tech in p_techs_nice:
        nice = get_tech(tech)
        posting.techs_nice.append(nice)
    # create salaries
    for key, val in p_salaries.items():
        create_salary(posting.id, key, val, p_salary_currency, p_salary_period)
    # update posting
    db_session.add(posting)
    db_session.commit()
    print('Added posting to the db!')


def create_salary(posting_id, employment_type, sal, sal_currency, sal_period):
    """Insert salary into the salaries table"""
    sal_from = sal['range'][0]
    sal_to = sal['range'][1] if len(sal['range']) == 2 else sal_from
    salary_dict = {
        'posting_id': posting_id,
        'employment_type_ascii': normalize_string(employment_type),
        'salary_from': sal_from,
        'salary_to': sal_to,
        'salary_currency': sal_currency,
        'salary_period': sal_period
    }
    salary = Salary(**salary_dict)
    db_session.add(salary)
    db_session.commit()
    print('Added salary to the db!')


def get_posting(web_id):
    """Check if the posting is in the database.
    Return the posting or None if the posting does not exist.
    """
    return Posting.query.filter_by(web_id=web_id).scalar()


def get_city(name):
    """Check if the city is already in the database;
    if not, make a new entry. Return the city.
    """
    # TODO cater for alias names:
    # 1. New table cities_aliases:
    #   id (integer, primary key)
    #   city_id (integer, foreign key)
    #   alias_ascii (string, unique)
    # 2. Modify get_city():
    #   if cities query returns None, query cities_aliases:
    #   .filter_by(alias_ascii=name_ascii)
    # 3. New command_line tool for adding aliases:
    #   * adds alias for an existing city
    #   * if alias in cities, delete alias from cities and update postings_cities
    name_ascii = normalize_string(name)
    city = City.query.filter_by(name_ascii=name_ascii).scalar()
    if not city:
        city = City(name=name, name_ascii=name_ascii)
        db_session.add(city)
        db_session.commit()
        print('Added city to the db!')
    return city


def get_tech(name):
    """Check if the tech is already in the database;
    if not, make a new entry. Return the tech.
    """
    name_ascii = normalize_string(name)
    tech = Technology.query.filter_by(name_ascii=name_ascii).scalar()
    if not tech:
        tech = Technology(name=name, name_ascii=name_ascii)
        db_session.add(tech)
        db_session.commit()
        print('Added tech to the db!')
    return tech
