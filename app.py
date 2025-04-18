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
import time
import datetime

st.session_state["locdata"] = {}
st.title("XCTrack Geolocation Demo1")

st.write(st.session_state["locdata"])
try:
    key = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return_value = st_javascript("(function(){ return window.XCTrack.getLocation(); })()", key=key)
    st.session_state["locdata"] = json.loads(return_value)
except Exception as e:
    st.write(f"Error parsing JSON: {e}")

time.sleep(5)
st.rerun()
