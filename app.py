import streamlit as st
from streamlit_javascript import st_javascript
import json
import time
import datetime
import plotly.graph_objects as go

if st.session_state.get("locdata"):
    fig = go.Figure(
        go.Scattermapbox(
            lat=[st.session_state.get("locdata").get("lat")],
            lon=[st.session_state.get("locdata").get("lon")],
            mode="markers",
            marker=go.scattermapbox.Marker(size=15, color="red"),
            text=["You are here!"],
        )
    )

    fig.update_layout(
        mapbox=dict(
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

else:
    st.info("Waiting for GPS location from XCTrack...")
st.write(st.session_state.get("locdata", "no location data found"))
time.sleep(5)
try:
    key = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    geoloc_str = st_javascript("(function(){ return window.XCTrack.getLocation(); })()", key=key)
    st.session_state["locdata"] = json.loads(geoloc_str)


except Exception as e:
    pass  # st.write(f"Error parsing JSON: {e}")

st.rerun()
