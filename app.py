import streamlit as st
import json
import time
import datetime
import plotly.graph_objects as go
import streamlit_js_eval


from pydantic import BaseModel
from typing import Optional


class LocationData(BaseModel):
    timestamp: int
    lat: float
    lon: float
    source: str
    altitude: float
    isValid: bool = False
    speed: Optional[float] = None


def get_best_location():
    # Try XCTrack first
    try:
        xctrack_data_raw = streamlit_js_eval.streamlit_js_eval(
            js_expressions="window.XCTrack && window.XCTrack.getLocation ? window.XCTrack.getLocation() : null",
        )
        # Returns a dict with lat, lon, time, altGps, isValid, stdBaroAlt ++
        if xctrack_data_raw:
            # If it's a string, try to parse it as JSON
            # if isinstance(xctrack_data_raw, str):
            xctrack_data = json.loads(xctrack_data_raw)
            location = LocationData(
                lat=xctrack_data.get("lat"),
                lon=xctrack_data.get("lon"),
                source="xctrack",
                timestamp=int(time.time()),
                altitude=xctrack_data.get("altGps"),
                isValid=xctrack_data.get("isValid"),
                speed=xctrack_data.get("speedComputed"),
            )
            return location
    except Exception as e:
        print(f"Error getting XCTrack location: {e}")
        pass  # failed, will try geolocation next

    try:
        geoloc = streamlit_js_eval.get_geolocation()
        if geoloc.get("coords"):
            loc = geoloc.get("coords")
            location = LocationData(
                lat=geoloc["coords"].get("latitude"),
                lon=geoloc["coords"].get("longitude"),
                source="geolocation",
                timestamp=geoloc.get("timestamp"),
                altitude=geoloc["coords"].get("altitude"),
                speed=geoloc["coords"].get("speed"),
                isValid=geoloc["coords"].get("accuracy") < 200,  # Assuming accuracy < 200m is valid
            )

            return location
    except Exception as e:
        print(f"Error getting geolocation: {e}")
        pass

    return {"error": "Both XCTrack and geolocation failed"}


def update_session_state():
    # Check if the session state already has locdata
    if "locdata" not in st.session_state:
        st.session_state["locdata"] = None

    # Get the best location
    location = get_best_location()

    # Update session state with the new location data
    if isinstance(location, LocationData):
        st.session_state["locdata"] = location.dict()
    else:
        st.session_state["locdata"] = {"error": location.get("error")}


DEBUG = False
update_session_state()
if DEBUG:
    st.write("Debug mode is ON")
    st.write("Session state:")
    st.write(st.session_state)


if st.session_state.get("locdata"):
    fig = go.Figure(
        go.Scattermap(
            lat=[st.session_state.get("locdata").get("lat")],
            lon=[st.session_state.get("locdata").get("lon")],
            mode="markers",
            marker=go.Marker(size=15, color="red"),
            text=["You are here!"],
        )
    )

    fig.update_layout(
        map=dict(
            style="open-street-map",
            center=dict(
                lat=st.session_state.get("locdata").get("lat"),
                lon=st.session_state.get("locdata").get("lon"),
            ),
            zoom=14,
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    st.plotly_chart(fig, use_container_width=True)
