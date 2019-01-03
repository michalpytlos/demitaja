from demitaja.models import Posting, City, Technology
from demitaja.database import db_session


# dummy postings
p1 = {
    'web_id': 'GRR3455RET',
    'title': 'Dev1',
    'posted': 80482,
    'scraped': 90000,
    'text': 'text of posting 1',
    'employment_type': 'permanent',
    'salary_from': 4000,
    'salary_to': 5000,
    'salary_currency': 'PLN',
    'salary_period': 'month',
    'cities': ['Warsaw'],
    'techs_must': ['Python', 'Django', 'Git'],
    'techs_nice': ['unittest', 'PostgreSQL']
}

p2 = {
    'web_id': 'DSAER345',
    'title': 'Dev2',
    'posted': 80988,
    'scraped': 90500,
    'text': 'text of posting 2',
    'employment_type': 'B2B',
    'salary_from': 7500,
    'salary_to': 9000,
    'salary_currency': 'PLN',
    'salary_period': 'month',
    'cities': ['Krakow'],
    'techs_must': ['Python', 'C++', 'Pandas'],
    'techs_nice': ['unittest', 'MySQL']
}


def test_create():
    create_posting(p1)
    create_posting(p2)


def create_posting(posting_d):
    # check if this is a new posting
    posting = get_posting(posting_d['web_id'])
    if posting:
        print('Posting already in the db')
        return
    # extract city and technologies
    p_cities = posting_d.pop('cities')
    p_techs_must = posting_d.pop('techs_must')
    p_techs_nice = posting_d.pop('techs_nice')
    # create posting object
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
    # insert posting to the db
    db_session.add(posting)
    db_session.commit()
    print('Added posting to the db!')


def get_posting(web_id):
    """Check if the posting is in the database.
    Return the posting or None if the posting does not exist.
    """
    return Posting.query.filter_by(web_id=web_id).scalar()


def get_city(name):
    """Check if the city is already in the database;
    if not, make a new entry. Return the city.
    """
    city = City.query.filter_by(name=name).scalar()
    if not city:
        city = City(name=name)
        db_session.add(city)
        db_session.commit()
        print('Added city to the db!')
    return city


def get_tech(name):
    """Check if the tech is already in the database;
    if not, make a new entry. Return the tech.
    """
    tech = Technology.query.filter_by(name=name).scalar()
    if not tech:
        tech = Technology(name=name)
        db_session.add(tech)
        db_session.commit()
        print('Added tech to the db!')
    return tech
