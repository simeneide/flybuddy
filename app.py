"""
## TEMPLATE APP FROM XCTrack to get location data
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XCTrack.getLocation() Debug</title>
    <style>
        body {
            background-color: white;
            color: black;
            font-family: Arial, sans-serif;
        }
    </style>
    <script>
        function getLocation() {
            const timestamp = new Date().toLocaleTimeString();
            if (typeof XCTrack !== 'undefined' && typeof XCTrack.getLocation === 'function') {
                try {
                    const location = JSON.parse(XCTrack.getLocation());
                    document.body.innerHTML = `<pre>Time: ${timestamp}\nXCTrack.getLocation()=\n${JSON.stringify(location, null, 2)}</pre>`;
                } catch (error) {
                    document.body.innerHTML = `<pre>Time: ${timestamp}\nError: ${error}</pre>`;
                }
            } else {
                document.body.innerHTML = `<pre>Time: ${timestamp}\nXCTrack.getLocation() is not available!\nDoes it run in XCTrack?\nIs the option "Allow web page to access XCTrack data" enabled?</pre>`;
            }
        }

        window.onload = function() {
            getLocation();
            setInterval(getLocation, 1000);
        };
    </script>
</head>
<body>
</body>
</html>
"""

import streamlit as st
from streamlit_javascript import st_javascript
import json

st.title("XCTrack Geolocation Demo")

return_value = st_javascript("(function(){ return {'width':window.XCTrack.getLocation()}; })()")
st.write(f"Width: {return_value}")


st.write(json.loads(return_value))

js_code = """
(() => {
    const timestamp = new Date().toLocaleTimeString();
    let response = {};
    // Try XCTrack first
    if (typeof window.XCTrack !== "undefined" && typeof window.XCTrack.getLocation === "function") {
        try {
            response = JSON.parse(window.XCTrack.getLocation());
            response["source"] = "XCTrack";
        } catch(e) {
            response = {"error": String(e), "source": "XCTrack"};
        }
        response["time"] = timestamp;
        return [1,2 ] //response;
    }
    // Fallback: Try browser geolocation API
    else if (navigator.geolocation) {
        return new Promise(resolve => {
            navigator.geolocation.getCurrentPosition(
                pos => resolve({
                    "latitude": pos.coords.latitude,
                    "longitude": pos.coords.longitude,
                    "accuracy": pos.coords.accuracy,
                    "source": "Browser",
                    "time": timestamp
                }),
                err => resolve({"error": err.message, "source": "Browser", "time": timestamp})
            );
        });
    }
    // No geolocation available
    else {
        return {"error": "No geolocation API available", "time": timestamp};
    }
})()
"""

# Button for manual refresh
loc = st_javascript(js_code)
st.write(loc)
# if loc is None:
#     st.info("Click 'Get Location' to fetch location data...")
# elif "error" in loc:
#     st.error(f"Error: {loc['error']} (source: {loc.get('source', '?')})")
# else:
#     st.write(f"Location data (source: {loc.get('source', '?')}) at {loc.get('time', '?')}:")
#     st.json(loc)
