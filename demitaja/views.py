from flask import render_template, request
from sqlalchemy import func
from time import gmtime, strftime
from demitaja.database import db_session
from demitaja.models import Posting, City, Technology
from demitaja import app
from demitaja.utils.utils import normalize_string
from demitaja.utils import queries


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
    return 'Hello world!'


@app.route('/summary')
def summary():
    # TODO serve db query results asynchronously via api:
    # 1.Create several API endpoints (one per db query/graph) accepting city and/or tech name as args.
    #   * each API endpoint returns either relevant graph code or data in json
    #   * each API endpoint checks if provided city/tech is in the db and if not
    #     returns an appropriate message instead of the regular response
    # 2. Search button in html makes several ajax requests (one per required graph) to the API
    # 3. If response to any of the ajax requests contains 'city/tech not found' message, abort all other requests
    #    and inform the user
    # 4. knockout.js manages content of the web page on the client side
    # 5. Each ajax.success with graph data triggers flag for knockout to display the graph
    # 6. html has filter checkboxes allowing the user to specify which graphs are to be displayed
    data = {}

    # User input tech and city names
    req_city = normalize_string(request.args.get('req_city'))
    req_tech = normalize_string(request.args.get('req_tech'))

    # Database tech and city names
    city_name = db_session.query(City.name).filter(City.name_ascii == req_city).scalar() if req_city else ''
    tech_name = db_session.query(Technology.name).filter(Technology.name_ascii == req_tech).scalar() if req_tech else ''

    # Most in-demand technologies
    data['techs'] = db_session.execute(queries.techs).fetchall()
    # Cities with most job postings
    data['cities'] = db_session.execute(queries.cities).fetchall()
    # Number of postings in database
    data['total_postings'] = db_session.query(func.count(Posting.id)).scalar()
    # Posted date for the oldest and newest postings
    dates = db_session.query(func.max(Posting.posted).label('newest'),
                             func.min(Posting.posted).label('oldest')
                             ).one()
    data['newest'] = strftime("%d %b %Y", gmtime(dates.newest))
    data['oldest'] = strftime("%d %b %Y", gmtime(dates.oldest))

    if req_city:
        # Number of job postings in req_city
        data['city'] = db_session.execute(queries.city, {'city': req_city}).fetchone()
        if not data['city']:
            data['city'] = (req_city, 0)
        # Technologies most in-demand in req_city
        data['techs_city'] = db_session.execute(queries.techs_city, {'city': req_city}).fetchall()

    if req_tech:
        # Demand for req_tech
        data['tech'] = db_session.execute(queries.tech, {'tech': req_tech}).fetchone()
        if not data['tech']:
            data['tech'] = (req_tech, 0)
        # Cities with most job postings requiring req_tech
        data['cities_tech'] = db_session.execute(queries.cities_tech, {'tech': req_tech}).fetchall()
        # Technologies most often required in postings requiring req_tech
        data['techs_tech'] = db_session.execute(queries.techs_tech, {'tech': req_tech}).fetchall()

    if req_tech and req_city:
        # Demand for req_tech in req_city
        data['tech_city'] = db_session.execute(queries.tech_city, {'city': req_city, 'tech': req_tech}).fetchone()
        if not data['tech_city']:
            data['tech_city'] = (req_tech, req_city, 0)
        # Technologies most often required in postings requiring req_tech in req_city
        data['techs_tech_city'] = db_session.execute(queries.techs_tech_city, {'city': req_city, 'tech': req_tech}).fetchall()

    return render_template('market-summary.html',
                           req_city=city_name,
                           req_tech=tech_name,
                           **data)
