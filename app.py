import streamlit as st
import json
import time
import datetime
import plotly.graph_objects as go
import streamlit_js_eval


from pydantic import BaseModel
from typing import Optional

hide_streamlit_style = """
            <style>
                /* Hide the Streamlit header and menu */
                header {visibility: hidden;}
                /* Optionally, hide the footer */
                .streamlit-footer {display: none;}
                /* Hide your specific div class, replace class name with the one you identified */
                .st-emotion-cache-uf99v8 {display: none;}
            </style>
            """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# st.markdown("<style>iframe{display: none}</style>", unsafe_allow_html=True)


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
    # Get window size
    reload = False
    window_width, window_height = get_window_size()
    # check if session state is different from the current window size
    if st.session_state.get("window_size") is None:
        st.session_state["window_size"] = {
            "width": window_width,
            "height": window_height,
        }
        reload = True
    elif (
        st.session_state["window_size"]["width"] != window_width
        or st.session_state["window_size"]["height"] != window_height
    ):
        st.session_state["window_size"] = {
            "width": window_width,
            "height": window_height,
        }
        reload = True

    # Check if the session state already has locdata
    if "locdata" not in st.session_state:
        st.session_state["locdata"] = None

    # Get the best location
    location = get_best_location()

    # Update session state with the new location data
    if isinstance(location, LocationData):
        location_dict = location.model_dump()
        # Check if location data has changed significantly
        if (
            st.session_state["locdata"] is None
            or abs(st.session_state["locdata"]["lat"] - location_dict["lat"]) > 0.0001
            or abs(st.session_state["locdata"]["lon"] - location_dict["lon"]) > 0.0001
        ):
            st.session_state["locdata"] = location_dict
            reload = True

    if reload:
        # Reload the page if window size changed
        st.rerun()


def get_window_size():
    # Use JS to get window size via streamlit_js_eval and cache it in session_state
    size = streamlit_js_eval.streamlit_js_eval(
        js_expressions="[window.innerWidth, window.parent.innerHeight]",
        key="get_win_size",
        want_response=True,
    )
    if isinstance(size, str):
        # Sometimes result may be serialized as string
        try:
            size = json.loads(size)
        except Exception:
            size = [800, 600]  # Default value
    if not isinstance(size, list) or len(size) != 2:
        size = [800, 600]  # Fallback
    return size


print(st.session_state.get("locdata"))

if (st.session_state.get("locdata") is not None) & (
    st.session_state.get("window_size") is not None
):
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
        width=st.session_state["window_size"]["width"],
        height=st.session_state["window_size"]["height"],
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    st.plotly_chart(fig, use_container_width=True)

update_session_state()
DEBUG = True

if DEBUG:
    st.write("Debug mode is ON")
    st.write("Session state:")
    st.write(st.session_state)
