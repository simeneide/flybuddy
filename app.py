import streamlit as st
import json
import time
import datetime
import plotly.graph_objects as go
import streamlit_js_eval


def get_best_location():
    # Try XCTrack first
    key = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
    try:
        xctrack_data_raw = streamlit_js_eval.streamlit_js_eval(
            js_expressions="window.XCTrack && window.XCTrack.getLocation ? window.XCTrack.getLocation() : null",
            # key=key + "xctrack",
        )
        st.write(xctrack_data_raw)
        if xctrack_data_raw:
            # If it's a string, try to parse it as JSON
            if isinstance(xctrack_data_raw, str):
                xctrack_data = json.loads(xctrack_data_raw)
            else:
                xctrack_data = xctrack_data_raw
            if isinstance(xctrack_data, dict) and "lat" in xctrack_data and "lon" in xctrack_data:
                xctrack_data["source"] = "xctrack"
                return xctrack_data
    except Exception as e:
        print(f"Error getting XCTrack location: {e}")
        pass  # failed, will try geolocation next

    try:
        geoloc_data = streamlit_js_eval.get_geolocation()

        if geoloc_data.get("coords"):
            loc = geoloc_data.get("coords")
            loc["source"] = "geolocation"
            loc["timestamp"] = geoloc_data.get("timestamp")
        return loc
    except Exception as e:
        print(f"Error getting geolocation: {e}")
        pass

    return {"error": "Both XCTrack and geolocation failed"}


st.write("location:")
st.write(get_best_location())


# if st.session_state.get("locdata"):
#     fig = go.Figure(
#         go.Scattermapbox(
#             lat=[st.session_state.get("locdata").get("lat")],
#             lon=[st.session_state.get("locdata").get("lon")],
#             mode="markers",
#             marker=go.scattermapbox.Marker(size=15, color="red"),
#             text=["You are here!"],
#         )
#     )

#     fig.update_layout(
#         mapbox=dict(
#             style="open-street-map",
#             center=dict(
#                 lat=st.session_state.get("locdata").get("lat"),
#                 lon=st.session_state.get("locdata").get("lon"),
#             ),
#             zoom=14,
#         ),
#         margin={"r": 0, "t": 0, "l": 0, "b": 0},
#     )

#     st.plotly_chart(fig, use_container_width=True)

# else:
#     st.info("Waiting for GPS location from XCTrack...")
