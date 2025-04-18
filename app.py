import streamlit as st
import plotly.graph_objects as go
from streamlit_javascript import st_javascript

st.set_page_config(layout="wide", page_title="XCTrack Live Position")
st.title("XCTrack Live GPS Map")

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
st.write("Raw coords:", coords)

if coords is None:
    st.info("Waiting for browser GPS location (allow location permissions, and reload if needed).")
elif isinstance(coords, list):
    lat, lon, acc = coords
    if lat is not None and lon is not None:
        st.success(f"Got location: {lat:.6f}, {lon:.6f} (Accuracy: {acc}m)")
        fig = go.Figure(
            go.Scattermapbox(
                lat=[lat],
                lon=[lon],
                mode="markers+text",
                marker=dict(size=14, color="red"),
                text=["You"],
                textposition="top center",
            )
        )
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_center_lat=lat,
            mapbox_center_lon=lon,
            mapbox_zoom=13,
            margin=dict(l=0, r=0, t=0, b=0),
            width=800,
            height=600,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"GPS error: {acc}")
else:
    st.error("Unexpected error getting GPS coordinates.")
