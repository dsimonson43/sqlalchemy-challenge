# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data in Hawaii."""

    # Find the most recent date in the database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    print(f"Most recent date: {most_recent_date}") #debugging

    most_recent_date = np.datetime64(most_recent_date)
    one_year_ago = most_recent_date - np.timedelta64(365, 'D')
    print(f"One year ago: {one_year_ago}") #debugging
    # Query for precipitation data for the last 12 months
    prcp_data = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= str(one_year_ago))
        .all()
    )

    # Convert results to a dictionary
    prcp_dict = {date: prcp for date, prcp in prcp_data}
    print(f"Dictionary results: {prcp_dict}") #debugging

    return jsonify(prcp_dict)


# Stations Route
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations."""
    # Query all stations
    stations_data = session.query(Station.station).all()
    stations_list = list(np.ravel(stations_data))

    return jsonify(stations_list)


# Temperature Observations Route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations for the previous year."""
    # Find the most active station (most number of results)
    most_active_station = (
        session.query(Measurement.station)
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station).desc())
        .first()[0]
    )
    print(f"Most Active station: {most_active_station}") #debugging
    # Find the most recent date and calculate one year prior
    
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    print(f"Most Recent Date: {most_recent_date}") #debugging

#calculate precisely one year ago
    import datetime as dt
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query temperatures
    tobs_data = (
        session.query(Measurement.date, Measurement.tobs)
        .filter(Measurement.date >= one_year_ago)
        .filter(Measurement.station == most_active_station)
        .all()
    )
    #covert results into a list of dictionaries

    tobs_list = [{"date": date, "temperature": tobs} for date, tobs in tobs_data]
    return jsonify(tobs_list)


# Start Date Routes

@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    """Return min, max, and average temperatures from start to end of dataset."""
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

#query temperatures for all dates greater than or equal to the start date
    results = session.query(*sel).filter(Measurement.date >= start).all()

    # Convert the results into a list
    temp_stats = list(np.ravel(results))

    return jsonify(temp_stats)

#start/end date route
@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end(start, end):
    """Returns min, avg, and max temperature values between start and ends dates."""
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
#query for temperatures of dates between start and end
    results = (
        session.query(*sel)
        .filter(Measurement.date >= start)
        .filter(Measurement.date <= end)
        .all()
    )
#conversion of results into list
    temp_stats = list(np.ravel(results))

    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)

    