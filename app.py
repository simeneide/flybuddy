import streamlit as st
import plotly.graph_objects as go
from streamlit_javascript import st_javascript

st.set_page_config(layout="wide", page_title="XCTrack Live Position")
st.title("XCTrack Live GPS Map")

# We'll try to get the user's coordinates as a tuple
coords = st_javascript(
    """
    (async function(){
        if (navigator.geolocation) {
            return await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(
                    pos => resolve([pos.coords.latitude, pos.coords.longitude, pos.coords.accuracy]),
                    err => resolve([null, null, err.message])
                );
            });
        } else {
            return [null, null, "Geolocation not supported"];
        }
    })()
    """,
    "Waiting for browser GPS location...",
)
st.write(st_javascript("1+1"))

if coords and isinstance(coords, list) and coords[0] is not None and coords[1] is not None:
    latitude, longitude = coords[0], coords[1]

    fig = go.Figure(
        go.Scattermapbox(
            lat=[latitude],
            lon=[longitude],
            mode="markers+text",
            marker=dict(size=14, color="red"),
            text=["You"],
            textposition="top center",
        )
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center_lat=latitude,
        mapbox_center_lon=longitude,
        mapbox_zoom=13,
        margin=dict(l=0, r=0, t=0, b=0),
        width=800,
        height=600,
    )
    st.plotly_chart(fig, use_container_width=True)

elif coords and isinstance(coords, list) and coords[2]:
    st.info(f"GPS error: {coords[2]}")
else:
    st.info("Waiting for browser GPS location (allow location permissions).")
