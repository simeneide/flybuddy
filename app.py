import streamlit as st
import plotly.graph_objects as go
from streamlit_javascript import st_javascript

st.set_page_config(layout="wide", page_title="XCTrack Live Position")
st.title("XCTrack Live GPS Map")

coords = st_javascript(
    """
    (async function(){
        // Try XCTrack first
        if (typeof XCTrack !== "undefined" && typeof XCTrack.getLocation === "function") {
            try {
                const location = JSON.parse(XCTrack.getLocation());
                // XCTrack location example structure: { latitude: ..., longitude: ..., accuracy: ... }
                if (location && typeof location.latitude === 'number' && typeof location.longitude === 'number') {
                    return [location.latitude, location.longitude, location.accuracy || null, "XCTrack"];
                }
            } catch (e) {
                // Could not parse, fall through to browser API
            }
        }
        // Otherwise, fallback to browser geolocation
        if (navigator.geolocation) {
            try {
                const pos = await new Promise((resolve, reject) => {
                    navigator.geolocation.getCurrentPosition(
                        p => resolve(p),
                        err => resolve({coords: {latitude: null, longitude: null, accuracy: null}, error: err.message})
                    );
                });
                let lat = pos.coords.latitude;
                let lon = pos.coords.longitude;
                let acc = pos.coords.accuracy;
                if (lat && lon) {
                    return [lat, lon, acc, "Browser"];
                } else {
                    return [null, null, null, pos.error || "Unknown error"];
                }
            } catch (e) {
                return [null, null, null, e.toString()];
            }
        } else {
            return [null, null, null, "Geolocation not supported"];
        }
    })()
    """,
    "Waiting for GPS location...",
)

st.write("Raw coords:", coords)

if coords is None:
    st.info(
        "Waiting for browser/XCTrack GPS location (allow location permissions or enable in XCTrack)."
    )
elif isinstance(coords, list):
    lat, lon, acc, src = coords
    if lat is not None and lon is not None:
        st.success(f"Got location from {src}: {lat:.6f}, {lon:.6f} (Accuracy: {acc}m)")
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
        st.error(f"GPS error: {src}")
else:
    st.error("Unexpected error getting GPS coordinates.")
