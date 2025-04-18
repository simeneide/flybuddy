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

st.title("XCTrack Geolocation Demo")
i = 0
while True:
    return_value = st_javascript(
        "(function(){ return {'width':window.XCTrack.getLocation()}; })()", key=f"{i}"
    )
    st.write(return_value)
    i = i + 1
    time.sleep(1)
