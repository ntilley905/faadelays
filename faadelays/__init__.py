"""Fetch latest data from the FAA ASWS API."""
from aiohttp import ClientSession, ClientResponseError

BASE_URL = "https://soa.smext.faa.gov/asws/api/airport/{}"

# define custom errors
class InvalidAirport(Exception):
    """Raised when the airport returns no data from the API."""
    pass

class ArriveDepartDelay:
    # Class for Arrival/Departure delays
    def __init__(self, airport, status=False, minimum=None, maximum=None, trend=None, reason=None):
        self.airport = airport
        self.status = status
        self.minimum = minimum
        self.maximum = maximum
        self.trend = trend
        self.reason = reason

class GroundDelay:
    # Class for Ground Delays
    def __init__(self, airport, status=False, average=None, reason=None):
        self.airport = airport
        self.status = status
        self.average = average
        self.reason = reason

class GroundStop:
    # Class for Ground Stops
    def __init__(self, airport, status=False, endtime=None, reason=None):
        self.airport = airport
        self.status = status
        self.endtime = endtime
        self.reason = reason

class Closure:
    # Class for closures
    def __init__(self, airport, status=False, begin=None, end=None, reason=None):
        self.airport = airport
        self.status = status
        self.begin = begin
        self.end = end
        self.reason = reason


class Nationwide:
    # Class for storing data from a nationwide API call
    def __init__(self, session: ClientSession):
        self.url = BASE_URL.format("delays")
        self.count = 0
        self.ground_delays = []
        self.ground_delay_count = 0
        self.ground_stops = []
        self.ground_stop_count = 0
        self.arrive_depart_delays = []
        self.arrive_depart_count = 0
        self.closures = []
        self.closure_count = 0
        self.session = session

    async def update(self):
        resp = await self.session.get(self.url)
        if resp.status == 200:
            data = await resp.json()
        else:
            raise ClientResponseError(
                    resp.request_info,
                    resp.history
                    )
        self.count = data['status']['count']

        for gd in data['GroundDelays']['groundDelay']:
            # Define a ground delay object and append that to the list of nationwide ground delays
            gdelay = GroundDelay(gd['airport'],
            True,
            gd['avgTime'],
            gd['reason'])

            self.ground_delays.append(gdelay)

        self.ground_delay_count = data['GroundDelays']['count']
        for gs in data['GroundStops']['groundStop']:
            # Define a ground stop object and append that to the list of nationwide ground stops
            stop = GroundStop(
                gs['airport'],
                True,
                gs['endTime'],
                gs['reason']
            )

            self.ground_stops.append(stop)

        self.ground_stop_count = data['GroundStops']['count']
        for ad in data['ArriveDepartDelays']['arriveDepart']:
            # Define an Arrival/Departure object and append that to the list of nationwide arrival/departure delays
            ardp = ArriveDepartDelay(
                ad['airport'],
                True,
                ad['minTime'],
                ad['maxTime'],
                None, # The API does not provide a trend for Arrival/Departure delays from the nationwide call so none will be passed through.
                ad['reason']
            )

            self.arrive_depart_delays.append(ardp)

        self.arrive_depart_count = data['ArriveDepartDelays']['count']
        for cl in data['Closures']['closure']:
            # Define a closure object and append that to the list of nationwide closures
            close = Closure(
                cl['airport'],
                True,
                None, # The API does not provide a beginning time for a closure from the nationwide call so none will be passed through.
                cl['reopen'],
                cl['reason']
            )

            self.closures.append(close)

        self.closure_count = data['Closures']['count']

class Airport:
    # Class for storing data for an individual airport
    def __init__(self, code, session: ClientSession):
        self.code = code
        self.name = None
        self.city = None
        self.state = None
        self.icao = None
        self.iata = None
        self.supported_airport = None
        self.delay = None
        self.delay_count = None
        self.ground_delay = GroundDelay(self.code)
        self.ground_stop = GroundStop(self.code)
        self.depart_delay = ArriveDepartDelay(self.code)
        self.arrive_delay = ArriveDepartDelay(self.code)
        self.closure = Closure(self.code)
        self.url = BASE_URL.format("status/" + self.code)
        self.session = session

    async def update(self):
        resp = await self.session.get(self.url)
        if resp.status == 200:
            data = await resp.json()
        else:
            raise ClientResponseError(
                resp.request_info,
                resp.history,
                )
        try:
            self.name = data['Name']
        # check for key error here because if a name is not returned no other data will be either as the API does not recognize the airport
        except KeyError:
            raise InvalidAirport(self.code + " is not a valid airport")
        self.city = data['City']
        self.state = data['State']
        self.icao = data['ICAO']
        self.iata = data['IATA']
        self.supported_airport = data['SupportedAirport']
        self.delay = data['Delay']
        self.delay_count = data['DelayCount']
        self.weather = data['Weather']['Weather'][0]['Temp'][0]
        self.visibility = data['Weather']['Visibility'][0]
        self.temp = data['Weather']['Temp'][0]
        self.wind = data['Weather']['Wind'][0]

        # Look for each type of delay in the API response
        # The API does not order the delays and does not return each in a consistent type so each has to use a different method
        ar = next((i for i, d in enumerate(data['Status']) if d.get('Type') == "Arrival"), False)
        de = next((i for i, d in enumerate(data['Status']) if d.get('Type') == "Departure"), False)
        gd = next((i for i, d in enumerate(data['Status']) if d.get('Type') == "Ground Delay"), False)
        gs = next((i for i, d in enumerate(data['Status']) if "EndTime" in d), False)
        cl = next((i for i, d in enumerate(data['Status']) if "ClosureEnd" in d), False)

        if ar is False:
            self.arrive_delay = ArriveDepartDelay(self.code)
        else:
            self.arrive_delay = ArriveDepartDelay(
                self.code,
                True,
                data['Status'][ar]["MinDelay"],
                data['Status'][ar]["MaxDelay"],
                data['Status'][ar]["Trend"],
                data['Status'][ar]["Reason"]
            )

        if de is False:
            self.depart_delay = ArriveDepartDelay(self.code)
        else:
            self.depart_delay = ArriveDepartDelay(
                self.code,
                True,
                data['Status'][de]["MinDelay"],
                data['Status'][de]["MaxDelay"],
                data['Status'][de]["Trend"],
                data['Status'][de]["Reason"]
            )

        if gd is False:
            self.ground_delay = GroundDelay(self.code)
        else:
            self.ground_delay = GroundDelay(
                self.code,
                True,
                data['Status'][gd]['AvgDelay'],
                data['Status'][gd]['Reason']
            )

        if gs is False:
            self.ground_stop = GroundStop(self.code)
        else:
            self.ground_stop = GroundStop(
                self.code,
                True,
                data['Status'][gs]['EndTime'],
                data['Status'][gs]['Reason']
            )

        if cl is False:
            self.closure = Closure(self.code)
        else:
            self.closure = Closure(
                self.code,
                True,
                data['Status'][cl]['ClosureBegin'],
                data['Status'][cl]['ClosureEnd'],
                data['Status'][cl]['Reason']
            )

async def get_nationwide_delays(session: ClientSession):
    results = Nationwide()
    await results.update(session)

    return results

async def get_airport_delays(code, session: ClientSession):
    results = Airport(code)
    await results.update(session)

    return results
