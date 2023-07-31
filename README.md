# FAA Airport Status

This is a simple Python package used to retrieve data from the FAA's NAS Status API.

## Classes

The following classes are available and in some cases dynamically generated when retrieving data:

Class | Information Provided | Methods
--- | --- | ---
ArriveDepartDelay | Airport, Status, Minimum delay, Maximum delay, Trend, Reason, Update time
GroundDelay | Airport, Status, Average delay, Maximum delay, Start time, End time, Reason, Update time, URL to the advisory, Departure scope (if applicable), Included Facilities (if applicable), Included flights (if applicable)
GroundStop | Airport, Status, End Time, Reason, Update time, URL to advisory, Included facilities (if applicable), Included flights (if applicable), Probabibility of extension
Closure | Airport, Status, Begin Time, End Time, Update time, NOTAM text
AirportConfig | Airport, Time the data was created, Arrival runway config, Departure runway config, Arrival rate, Source time stamp
Airport | Code (provide when creating, IATA format), *Name*, *Longitude*, *Latitude*, Bool of if airport is deicing (see note), Bool of any delays, Count of delays, GroundDelay object, GroundStop object, Depart Delay object (ArriveDepartDelay), Arrive Delay object (ArriveDepartDelay), Closure object, Airport config | Update

Items in *italics* are not updated until delay data is present

Note: Information about airport deicing is untested

## Methods Available

`get_airport_delays(airport_code, session)` requires the code for the airport to get delays for in IATA format (i.e. ATL for Atlanta) and an asyncio HTTP session (such as aiohttp.ClientSession) and returns an Airport object

## Support
[![Buy me a coffee][buymeacoffee-shield]][buymeacoffee]



[buymeacoffee-shield]: https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-2.svg
[buymeacoffee]: https://www.buymeacoffee.com/ntilley905
