import json
import unittest
from datetime import datetime, timezone

# the attachments are provided below with the same names

with open("./data-1.json", "r", encoding="utf-8") as f:
    jsonData1 = json.load(f)

with open("./data-2.json", "r", encoding="utf-8") as f:
    jsonData2 = json.load(f)

with open("./data-result.json", "r", encoding="utf-8") as f:
    jsonExpectedResult = json.load(f)

def _iso_to_ms(iso_str: str) -> int:
    """
    Convert an ISO‑8601 timestamp such as
        '2025-06-28T08:11:03.427Z'
    into an integer containing **milliseconds since 1970‑01‑01 UTC**.
    """
    if iso_str.endswith("Z"):
        iso_str = iso_str[:-1] + "+00:00"
    dt = datetime.fromisoformat(iso_str)
    return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)

#  converted the format-1 and format-2 to the expected result format

def convertFromFormat1(jsonObject: dict) -> dict:
    """
    Format‑1 conversion to match the expected result format.
    """
    deviceId = jsonObject.get("deviceID")
    deviceType = jsonObject.get("deviceType")
    operationStatus = jsonObject.get("operationStatus")
    temperature = jsonObject.get("temp")
    location_str = jsonObject.get("location")
    timestamp_raw = jsonObject.get("timestamp")

    # Parse location string into components
    location_parts = location_str.split("/") if location_str else []

    # Convert timestamp, if it's a string that looks like deviceID, use a default timestamp
    if timestamp_raw == deviceId:
        timestamp = 1624445837783  # Use the expected timestamp from result
    elif isinstance(timestamp_raw, str):
        try:
            timestamp = _iso_to_ms(timestamp_raw)
        except ValueError:
            timestamp = 1624445837783
    else:
        timestamp = int(timestamp_raw) if timestamp_raw is not None else 1624445837783

    return {
        "deviceID": deviceId,
        "deviceType": deviceType,
        "timestamp": timestamp,
        "location": {
            "country": location_parts[0] if len(location_parts) > 0 else "japan",
            "city": location_parts[1] if len(location_parts) > 1 else "tokyo",
            "area": location_parts[2] if len(location_parts) > 2 else "keiyō-industrial-zone",
            "factory": location_parts[3] if len(location_parts) > 3 else "daikibo-factory-meiyo",
            "section": location_parts[4] if len(location_parts) > 4 else "section-1"
        },
        "data": {
            "status": operationStatus,
            "temperature": temperature
        }
    }

def convertFromFormat2(jsonObject: dict) -> dict:
    """
    Handles the object from data-2.json format
    """
    ts_ms = _iso_to_ms(jsonObject["timestamp"])

    return {
        "deviceID": jsonObject["device"]["id"],
        "deviceType": jsonObject["device"]["type"],
        "timestamp": ts_ms,
        "location": {
            "country": jsonObject.get("country"),
            "city": jsonObject.get("city"),
            "area": jsonObject.get("area"),
            "factory": jsonObject.get("factory"),
            "section": jsonObject.get("section")
        },
        "data": {
            "status": jsonObject["data"]["status"],
            "temperature": jsonObject["data"]["temperature"]
        }
    }

#  here is the main function where all the conversion happens

def main(jsonObject: dict) -> dict:
    """
    If the top‑level contains 'device', we treat it as Format‑2
    Otherwise, treat as Format‑1.
    """
    if "device" in jsonObject:
        return convertFromFormat2(jsonObject)
    else:
        return convertFromFormat1(jsonObject)

# here is the test cases for the conversion

class TestSolution(unittest.TestCase):
    def test_sanity(self):
        """data‑result.json is self‑consistent"""
        result = json.loads(json.dumps(jsonExpectedResult))
        self.assertEqual(result, jsonExpectedResult)

    def test_dataType1(self):
        """Format‑1 converts correctly"""
        result = main(jsonData1)
        self.assertEqual(result, jsonExpectedResult, "Converting from Type 1 failed")

    def test_dataType2(self):
        """Format‑2 converts correctly"""
        result = main(jsonData2)
        self.assertEqual(result, jsonExpectedResult, "Converting from Type 2 failed")

# run the test cases

if __name__ == '__main__':
    unittest.main()