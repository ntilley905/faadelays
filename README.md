# FAA Airport Status

This is a simple Python package used to retrieve data from the FAA's ASWS API. See https://app.swaggerhub.com/apis/FAA/ASWS/1.1.0 for API documentation.

## Classes

The following classes are available and in some cases dynamically generated when retrieving data:

Class | Information Provided | Methods
--- | --- | ---
ArriveDepartDelay | Airport, Status, Minimum delay, Maximum delay, Trend, Reason
GroundDelay | Airport, Status, Average delay, Reason
GroundStop | Airport, Status, End Time, Reason
Closure | Airport, Status, Begin Time, End Time, Reason
Nationwide | Total count of delays, Array of Ground delays, Count of Ground Delays, Array of Ground Stops, Count of Ground Stops, Array of ArriveDepart Delays, Count of ArriveDepart Delays, Array of Closures, Count of Closures | Update
Airport | Code (provide when creating, IATA format), Name, City, State, ICAO identifier, IATA identifier, Bool of Supported Airport, Bool of any delays, Count of delays, GroundDelay object, GroundStop object, Depart Delay object (ArriveDepartDelay), Arrive Delay object (ArriveDepartDelay), Closure object | Update

## Methods Available

`get_nationwide_delays(session)` requires an asyncio HTTP session (such as aiohttp.ClientSession) and returns a Nationwide object

`get_airport_delays(airport_code, session)` requires the code for the airport to get delays for in IATA format (i.e. ATL for Atlanta) and an asyncio HTTP session (such as aiohttp.ClientSession) and returns an Airport object

## Support
[![Buy me a coffee][buymeacoffee-shield]][buymeacoffee]



[buymeacoffee-shield]: https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-2.svg
[buymeacoffee]: https://www.buymeacoffee.com/ntilley905
