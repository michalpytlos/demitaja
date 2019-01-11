"""SQL queries."""

import sqlalchemy


# Get 10 most in-demand technologies
techs = sqlalchemy.sql.text(
    "SELECT technologies.name, COUNT(*) AS count "
    "FROM postings_techs_must "
    "JOIN technologies "
    "ON postings_techs_must.must_id=technologies.id "
    "GROUP BY technologies.name "
    "ORDER BY count DESC "
    "LIMIT 10"
)


# Get 10 cities with most postings
cities = sqlalchemy.sql.text(
    "SELECT cities.name, COUNT(*) AS count "
    "FROM postings_cities "
    "JOIN cities "
    "ON postings_cities.city_id=cities.id "
    "GROUP BY cities.name "
    "ORDER BY count DESC "
    "LIMIT 10"
)

# Get number of job postings in a given city
city = sqlalchemy.sql.text(
    "SELECT cities.name, COUNT(*) "
    "FROM postings_cities "
    "JOIN cities "
    "ON postings_cities.city_id=cities.id "
    "WHERE cities.name_ascii=:city "
    "GROUP BY cities.name"
)

# Get demand for a given technology
tech = sqlalchemy.sql.text(
    "SELECT technologies.name, COUNT(*) "
    "FROM postings_techs_must "
    "JOIN technologies "
    "ON postings_techs_must.must_id=technologies.id "
    "WHERE technologies.name_ascii=:tech "
    "GROUP BY technologies.name"
)

# Get 5 cities with most postings requiring a given technology
cities_tech = sqlalchemy.sql.text(
    "SELECT cities.name, technologies.name, COUNT(*) AS count "
    "FROM postings_cities "
    "JOIN cities "
        "ON postings_cities.city_id=cities.id "
    "JOIN postings_techs_must "
        "ON postings_techs_must.posting_id=postings_cities.posting_id "
    "JOIN technologies "
        "ON postings_techs_must.must_id=technologies.id "
    "WHERE technologies.name_ascii=:tech "
    "GROUP BY cities.name "
    "ORDER BY count DESC "
    "LIMIT 5"
)

# Get 5 most in-demand technologies in a given city
techs_city = sqlalchemy.sql.text(
    "SELECT technologies.name, cities.name, COUNT(*) AS count "
    "FROM postings_cities "
    "JOIN cities "
        "ON postings_cities.city_id=cities.id "
    "JOIN postings_techs_must "
        "ON postings_techs_must.posting_id=postings_cities.posting_id "
    "JOIN technologies "
        "ON postings_techs_must.must_id=technologies.id "
    "WHERE cities.name_ascii=:city "
    "GROUP BY technologies.name "
    "ORDER BY count DESC "
    "LIMIT 5"
)

# Get demand for a given technology in a given city
tech_city = sqlalchemy.sql.text(
    "SELECT technologies.name, cities.name, COUNT(*) AS count "
    "FROM postings_cities "
    "JOIN cities "
        "ON postings_cities.city_id=cities.id "
    "JOIN postings_techs_must "
        "ON postings_techs_must.posting_id=postings_cities.posting_id "
    "JOIN technologies "
        "ON postings_techs_must.must_id=technologies.id "
    "WHERE cities.name_ascii=:city "
        "AND technologies.name_ascii=:tech "
    "GROUP BY technologies.name "
    "ORDER BY count DESC "
    "LIMIT 5"
)

# Get 5 technologies most often accompanying a given technology in postings
techs_tech = sqlalchemy.sql.text(
    "SELECT t1.name, t2.name, COUNT(*) AS count "
    "FROM technologies t1 "
    "JOIN postings_techs_must pt1 "
        "ON pt1.must_id=t1.id "
    "JOIN postings_techs_must pt2 "
        "ON pt1.posting_id=pt2.posting_id "
    "JOIN technologies t2 "
        "ON pt2.must_id=t2.id "
    "WHERE t2.name_ascii=:tech "
        "AND t1.name_ascii<>:tech "
    "GROUP BY t1.name "
    "ORDER BY count DESC "
    "LIMIT 5"
)

# Get 5 technologies most often accompanying a given technology in a given city in postings
techs_tech_city = sqlalchemy.sql.text(
    "SELECT t1.name, t2.name, cities.name, COUNT(*) AS count "
    "FROM technologies t1 "
    "JOIN postings_techs_must AS pt1 "
        "ON pt1.must_id=t1.id "
    "JOIN postings_techs_must AS pt2 "
        "ON pt1.posting_id=pt2.posting_id "
    "JOIN technologies t2 "
        "ON pt2.must_id=t2.id "
    "JOIN postings_cities "
        "ON pt1.posting_id=postings_cities.posting_id "
    "JOIN cities "
        "ON postings_cities.city_id=cities.id "
    "WHERE t2.name_ascii=:tech "
        "AND t1.name_ascii<>:tech "
        "AND cities.name_ascii=:city "
    "GROUP BY t1.name "
    "ORDER BY count DESC "
    "LIMIT 5"
)
