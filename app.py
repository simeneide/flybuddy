import streamlit as st
import plotly.graph_objects as go
from streamlit_javascript import st_javascript

st.set_page_config(layout="wide", page_title="XCTrack Live Position")
st.title("XCTrack Live GPS Map")


def get_xctrack_or_browser_location_js():
    # Improved readability, matches your HTML debug logic and string formatting
    return """
    (async function() {
        // Helper for browser time
        const timestamp = new Date().toLocaleTimeString();
        // Try XCTrack if present
        if (typeof XCTrack !== 'undefined' && typeof XCTrack.getLocation === 'function') {
            try {
                const location = JSON.parse(XCTrack.getLocation());
                if (location && typeof location.latitude === 'number' && typeof location.longitude === 'number') {
                    return [location.latitude, location.longitude, location.accuracy || null, "XCTrack", timestamp];
                }
                return [null, null, null, "XCTrack returned bad data", timestamp];
            } catch (error) {
                return [null, null, null, `XCTrack exception: ${error}`, timestamp];
            }
        } else if (navigator.geolocation) {
            try {
                const pos = await new Promise((resolve) =>
                    navigator.geolocation.getCurrentPosition(
                        p => resolve(p),
                        err => resolve({ coords: { latitude: null, longitude: null, accuracy: null }, error: err.message })
                    )
                );
                let lat = pos.coords.latitude;
                let lon = pos.coords.longitude;
                let acc = pos.coords.accuracy;
                if (lat && lon) {
                    return [lat, lon, acc, "Browser", timestamp];
                } else {
                    return [null, null, null, pos.error || "Unknown error", timestamp];
                }
            } catch (error) {
                return [null, null, null, `Browser geolocation exception: ${error}`, timestamp];
            }
        } else {
            return [null, null, null, "Geolocation not supported", timestamp];
        }
    })()
    """


# Get coordinates
coords = st_javascript(
    get_xctrack_or_browser_location_js(),
)

if coords is None or not isinstance(coords, list) or len(coords) < 5:
    st.info(
        "Waiting for browser/XCTrack GPS location (allow location permissions or enable in XCTrack)."
    )
else:
    lat, lon, acc, src, timestamp = coords
    if lat is not None and lon is not None:
        st.success(f"({timestamp}) Location from {src}: {lat:.6f}, {lon:.6f} (Accuracy: {acc}m)")
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
        st.error(f"({timestamp}) GPS error: {src}")
