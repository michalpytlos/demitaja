from flask import render_template, request, jsonify
from sqlalchemy import func
from sqlalchemy.orm import aliased
from time import gmtime, strftime
from demitaja.database import db_session
from demitaja.models import (Posting, City, Technology, postings_must_assoc,
                             postings_cities_assoc)
from demitaja import app
from demitaja.utils import queries, charts
from demitaja.utils.utils import normalize_string, check_item


###############################
# Database session management #
###############################

@app.teardown_appcontext
def remove_session(exception=None):
    """Remove database session at the end of each request."""
    db_session.remove()


##################
# View functions #
##################

@app.route('/')
def home():
    # TODO serve db query results asynchronously via api:
    # 1.Create several API endpoints (one per db query/graph) accepting city and/or tech name as args.
    #   * each API endpoint returns data in json
    #   * each API endpoint checks if provided city/tech is in the db and if not
    #     returns an appropriate message instead of the regular response
    # 2. Search button in html makes several ajax requests (one per required graph) to the API
    # 3. If response to any of the ajax requests contains 'city/tech not found' message, abort all other requests
    #    and inform the user
    # 4. knockout.js manages content of the web page on the client side
    # 5. Each ajax.success with graph data triggers flag for knockout to display the graph
    # 6. html has filter checkboxes allowing the user to specify which graphs are to be displayed

    # Get posted date for the oldest and newest postings
    dates = db_session.query(func.max(Posting.posted).label('newest'),
                             func.min(Posting.posted).label('oldest')
                             ).one()
    # Template variables
    data = {
        # Get total number of postings in database
        'total_postings': db_session.query(func.count(Posting.id)).scalar(),
        # Get posted date for the oldest and newest postings
        'newest':  strftime("%d %b %Y", gmtime(dates.newest)),
        'oldest': strftime("%d %b %Y", gmtime(dates.oldest)),
        # Get number of job postings for each of top 10 technologies
        'techs': db_session.execute(queries.techs).fetchall(),
        # Get number of job postings for each of top 10 cities
        'cities': db_session.execute(queries.cities).fetchall()
    }
    return render_template('index.html', **data)


@app.route('/api/cities')
def api_cities():
    """Cities chart"""
    # Get total number of postings in database
    total_postings = db_session.query(func.count(Posting.id)).scalar()
    # req_tech
    tech_name_ascii, tech_name, tech_count = check_item(request, 'tech')
    # req_city
    city_name_ascii, city_name, city_count = check_item(request, 'city')

    if tech_name:
        # Get 5 cities with most postings with req_tech as must
        cities_tech = db_session.execute(queries.cities_tech, {'tech': tech_name_ascii}).fetchall()
        # Get total number of job postings for each city in cities_tech
        req_cities = [normalize_string(city[0]) for city in cities_tech]
        if city_name and city_name_ascii not in req_cities:
                # Get number of postings in req_city with req_tech as must
                tech_city = db_session.execute(queries.tech_city,
                                               {'city': city_name_ascii, 'tech': tech_name_ascii}).fetchone()
                if tech_city:
                    # Append tech_city to req_cities and cities_tech
                    req_cities.append(city_name_ascii)
                    cities_tech.append((tech_city[1], tech_city[0], tech_city[2]))
        cities_all = db_session.query(City.name, func.count('*')). \
            join(postings_cities_assoc). \
            filter(City.name_ascii.in_(req_cities)). \
            group_by(City.name).all()
        # Build tuple (no_of_postings_all, no_of_postings_req_tech)
        total = (total_postings, tech_count)
        # Build list of tuples (city_name, no_of_postings_all_techs, no_of_postings_req_tech)
        cities_dict = dict(cities_all)
        items = [[city[0], cities_dict[city[0]], city[2]] for city in cities_tech]
        # Build chart
        chart = charts.bar_double(items,
                                  total,
                                  title='Cities with most {} job postings'.format(tech_name),
                                  legend=('All technologies', tech_name))
    elif city_name:
        # Build city tuple
        city = (city_name, city_count)
        # Get number of job postings for each of top 10 cities
        cities = db_session.execute(queries.cities).fetchall()
        # Get index of req_city in cities
        # If req_city is not in cities, append it
        try:
            city_index = cities.index(city)
        except ValueError:
            cities.append(city)
            cities.sort(key=lambda x: x[1], reverse=True)
            city_index = cities.index(city)
        # Build chart
        chart = charts.bar_single(cities,
                                  total_postings,
                                  title='Cities with most job postings',
                                  highlight=city_index)

    else:
        # Get number of job postings for each of top 10 cities
        cities = db_session.execute(queries.cities).fetchall()
        # Build chart
        chart = charts.bar_single(cities,
                                  total_postings,
                                  title='Cities with most job postings')
    return jsonify(name='cities', base64=chart)


@app.route('/api/techs')
def api_techs():
    """Technologies chart"""
    # Get total number of postings in database
    total_postings = db_session.query(func.count(Posting.id)).scalar()
    # req_tech
    tech_name_ascii, tech_name, tech_count = check_item(request, 'tech')
    # req_city
    city_name_ascii, city_name, city_count = check_item(request, 'city')

    if city_name:
        # Get number of postings of top 5 technologies in req_city
        techs_city = db_session.execute(queries.techs_city, {'city': city_name_ascii}).fetchall()
        # Get total number of job postings for each technology in techs_city
        req_techs = [normalize_string(tech[0]) for tech in techs_city]
        if tech_name and tech_name_ascii not in req_techs:
            # Get number of postings in req_city with req_tech as must
            tech_city = db_session.execute(queries.tech_city,
                                           {'city': city_name_ascii, 'tech': tech_name_ascii}).fetchone()
            if tech_city:
                # Append tech_city to req_cities and cities_tech
                req_techs.append(tech_name_ascii)
                techs_city.append(tech_city)
        techs_all = db_session.query(Technology.name, func.count('*')). \
            join(postings_must_assoc). \
            filter(Technology.name_ascii.in_(req_techs)). \
            group_by(Technology.name).all()
        # Build tuple (no_of_postings_all, no_of_postings_req_city)
        total = (total_postings, city_count)
        # Build list of tuples (tech_name, no_of_postings_all_cities, no_of_postings_req_city)
        techs_dict = dict(techs_all)
        items = [[tech[0], techs_dict[tech[0]], tech[2]] for tech in techs_city]
        # Build chart
        chart = charts.bar_double(items,
                                  total,
                                  title='Most in-demand technologies in {}'.format(city_name),
                                  legend=('All cities', city_name))
    elif tech_name:
        # Get number of job postings with req_tech as must
        tech = (tech_name, tech_count)
        # Get number of job postings for each of top 10 technologies
        techs = db_session.execute(queries.techs).fetchall()
        # Get index of req_tech in techs
        # If req_tech not in techs, append it
        try:
            tech_index = techs.index(tech)
        except ValueError:
            techs.append(tech)
            techs.sort(key=lambda x: x[1], reverse=True)
            tech_index = techs.index(tech)
        # Build chart
        chart = charts.bar_single(techs,
                                  total_postings,
                                  title='Most in-demand technologies',
                                  highlight=tech_index)
    else:
        # Get number of job postings for each of top 10 technologies
        techs = db_session.execute(queries.techs).fetchall()
        # Build chart
        chart = charts.bar_single(techs,
                                  total_postings,
                                  title='Most in-demand technologies')
    return jsonify(name='techs', base64=chart)


@app.route('/api/techs-tech')
def api_techs_tech():
    """Techs tech chart"""
    # req_tech
    tech_name_ascii, tech_name, tech_count = check_item(request, 'tech')
    # req_city
    city_name_ascii, city_name, city_count = check_item(request, 'city')

    if city_name and tech_name:
        # Get number of postings in req_city with req_tech as must
        tech_city = db_session.execute(queries.tech_city,
                                       {'city': city_name_ascii, 'tech': tech_name_ascii}).fetchone()
        # Technologies most often required in postings requiring req_tech in req_city
        techs_tech_city = db_session.execute(queries.techs_tech_city,
                                             {'city': city_name_ascii, 'tech': tech_name_ascii}).fetchall()
        # Get total number of job postings for techs in techs_tech_city
        req_techs_tech = [normalize_string(tech[0]) for tech in techs_tech_city]
        t_alias, pm_alias = aliased(Technology), aliased(postings_must_assoc)
        techs_tech_all = db_session.query(Technology.name, func.count('*')). \
            join(postings_must_assoc). \
            join(pm_alias, pm_alias.c.posting_id == postings_must_assoc.c.posting_id). \
            join(t_alias, t_alias.id == pm_alias.c.must_id). \
            filter(Technology.name_ascii.in_(req_techs_tech)). \
            filter(t_alias.name_ascii == tech_name_ascii). \
            group_by(Technology.name).all()
        # Build tuple (no_of_postings_req_tech, no_of_postings_req_tech_req_city)
        total = (tech_count, tech_city[2])
        # Build list of tuples (tech_name, no_of_postings_tech_req_tech, no_of_postings_tech_req_tech_req_city)
        techs_tech_dict = dict(techs_tech_all)
        items = [[tech[0], techs_tech_dict[tech[0]], tech[3]] for tech in techs_tech_city]
        # Build chart
        chart = charts.bar_double(items,
                                  total,
                                  title='Technologies most often required  in {} job postings'.format(tech_name),
                                  legend=('All cities', city_name))
    elif tech_name:
        # Top 5 technologies required in postings requiring req_tech
        techs_tech = db_session.execute(queries.techs_tech, {'tech': tech_name_ascii}).fetchall()
        items = [(tech[0], tech[2]) for tech in techs_tech]
        chart = charts.bar_single(items,
                                  tech_count,
                                  title='Technologies most often required in {} job postings'.format(tech_name))
    else:
        # no data for chart if no req_tech
        chart = None
    return jsonify(name='techs-tech', base64=chart)


@app.route('/api/charts-data')
def api_charts_data():
    """Charts data in textual format. This is just to confirm that the charts are correct."""
    data = {}  # container for template variables
    # req_tech
    tech_name_ascii, tech_name, data['tech_count'] = check_item(request, 'tech')
    # req_city
    city_name_ascii, city_name, data['city_count'] = check_item(request, 'city')
    data['tech_name'], data['city_name'] = tech_name, city_name
    if city_name:
        # Technologies most in-demand in req_city
        data['techs_city'] = db_session.execute(queries.techs_city, {'city': city_name_ascii}).fetchall()
    if tech_name:
        # Cities with most job postings requiring req_tech
        data['cities_tech'] = db_session.execute(queries.cities_tech, {'tech': tech_name_ascii}).fetchall()
        # Technologies most often required in postings requiring req_tech
        data['techs_tech'] = db_session.execute(queries.techs_tech, {'tech': tech_name_ascii}).fetchall()
    if city_name and tech_name:
        # Demand for req_tech in req_city
        data['tech_city'] = db_session.execute(queries.tech_city, {'city': city_name_ascii, 'tech': tech_name_ascii}).fetchone()
        if not data['tech_city']:
            data['tech_city'] = (tech_name, city_name, 0)
        # Technologies most often required in postings requiring req_tech in req_city
        data['techs_tech_city'] = db_session.execute(queries.techs_tech_city,
                                                     {'city': city_name_ascii, 'tech': tech_name_ascii}).fetchall()
    return render_template('charts-data.html', **data)
