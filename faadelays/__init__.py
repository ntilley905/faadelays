"""Fetch latest data from the FAA ASWS API."""
from aiohttp import ClientSession, ClientResponseError

BASE_URL = "https://nasstatus.faa.gov/api/airport-events"


class ArriveDepartDelay:
    # Class for Arrival/Departure delays
    def __init__(self, airport, status=False, minimum=None, maximum=None, average_delay=None, trend=None, reason=None, update_time=None):
        self.airport = airport
        self.status = status
        self.minimum = minimum
        self.maximum = maximum
        self.average_delay = average_delay
        self.trend = trend
        self.reason = reason
        self.update_time = update_time

class GroundDelay:
    # Class for Ground Delays
    def __init__(self, airport, status=False, average=None, max_delay=None, start_time=None, end_time=None, reason=None, update_time=None, advisory_url=None, departure_scope=None, included_facilities=None, included_flights=None):
        self.airport = airport
        self.status = status
        self.average = average
        self.max_delay = max_delay
        self.start_time = start_time
        self.end_time = end_time
        self.reason = reason
        self.update_time = update_time
        self.advisory_url = advisory_url
        self.departure_scope = departure_scope
        self.included_facilities = included_facilities
        self.included_flights = included_flights


class GroundStop:
    # Class for Ground Stops
    def __init__(self, airport, status=False, endtime=None, reason=None, update_time=None, advisory_url=None, included_facilities=None, included_flights=None, probability_of_extension=None):
        self.airport = airport
        self.status = status
        self.endtime = endtime
        self.reason = reason
        self.update_time = update_time
        self.advisory_url = advisory_url
        self.included_facilities = included_facilities
        self.included_flights = included_flights
        self.probability_of_extension = probability_of_extension

class Closure:
    # Class for closures
    def __init__(self, airport, status=False, start=None, end=None, reason=None, update_time=None, notam=None):
        self.airport = airport
        self.status = status
        self.start = start
        self.end = end
        self.update_time = update_time
        self.notam = notam

class AirportConfig:
    # Class for storing airport config data
    def __init__(self, airport, created_time=None, arrival_runway_config=None, departure_runway_config=None, arrival_rate=None, source_time_stamp=None):
        self.airport = airport
        self.created_time = created_time
        self.arrival_runway_config = arrival_runway_config
        self.departure_runway_config = departure_runway_config
        self.arrival_rate = arrival_rate
        self.source_time_stamp = source_time_stamp


class Airport:
    # Class for storing data for an individual airport
    def __init__(self, code, session: ClientSession):
        self.code = code
        self.name = None
        self.latitude = None
        self.longitude = None
        self.is_deicing = False
        self.supported_airport = None
        self.delay = False
        self.delay_count = 0
        self.ground_delay = GroundDelay(self.code)
        self.ground_stop = GroundStop(self.code)
        self.depart_delay = ArriveDepartDelay(self.code)
        self.arrive_delay = ArriveDepartDelay(self.code)
        self.closure = Closure(self.code)
        self.config = None
        self.session = session

    async def update(self):
        resp = await self.session.get(BASE_URL)
        if resp.status == 200:
            data = await resp.json()
        else:
            raise ClientResponseError(
                resp.request_info,
                resp.history,
                )

        # iterate through returned data for correct airport
        for airport in data:
            if airport['airportId'] == self.code:

                self.name = airport['airportLongName']
                self.latitude = airport['latitude']
                self.longitude = airport['longitude']

                if airport['deicing']:
                    self.is_deicing = True
                
                # check for each type of delay
                if airport['groundStop']:
                    self.ground_stop = GroundStop(
                        airport=self.code,
                        status=True,
                        endtime=airport['groundStop']['endTime'],
                        reason=airport['groundStop']['impactingCondition'],
                        update_time=airport['groundStop']['updatedAt'],
                        advisory_url=airport['groundStop']['advisoryUrl'],
                        included_facilities=airport['groundStop']['includedFacilities'],
                        included_flights=airport['groundStop']['includedFlights'],
                        probability_of_extension=airport['groundStop']['probabilityOfExtension'],
                    )
                    self.delay_count += 1
                else:
                    self.GroundStop = GroundStop(self.code)
                
                if airport['arrivalDelay']:
                    self.arrive_delay = ArriveDepartDelay(
                        airport=self.code,
                        status=True,
                        minimum=airport['arrivalDelay']['arrivalDeparture']['min'],
                        maximum=airport['arrivalDelay']['arrivalDeparture']['max'],
                        average_delay=airport['arrivalDelay']['averageDelay'],
                        trend=airport['arrivalDelay']['arrivalDeparture']['trend'],
                        reason=airport['arrivalDelay']['reason'],
                        update_time=airport['arrivalDelay']['updateTime'],
                    )
                    self.delay_count += 1
                
                else:
                    self.arrive_delay = ArriveDepartDelay(self.code)
                
                if airport['departureDelay']:
                    self.depart_delay = ArriveDepartDelay(
                        airport=self.code,
                        status=True,
                        minimum=airport['departureDelay']['arrivalDeparture']['min'],
                        maximum=airport['departureDelay']['arrivalDeparture']['max'],
                        average_delay=airport['departureDelay']['averageDelay'],
                        trend=airport['departureDelay']['arrivalDeparture']['trend'],
                        reason=airport['departureDelay']['reason'],
                        update_time=airport['departureDelay']['updateTime'],
                    )
                    self.delay_count += 1
                
                else:
                    self.depart_delay = ArriveDepartDelay(self.code)

                if airport['groundDelay']:
                    self.ground_delay = GroundDelay(
                        airport=self.code,
                        status=True,
                        average=airport['groundDelay']['avgDelay'],
                        max_delay=airport['groundDelay']['maxDelay'],
                        start_time=airport['groundDelay']['startTime'],
                        end_time=airport['groundDelay']['endTime'],
                        reason=airport['groundDelay']['impactingCondition'],
                        update_time=airport['groundDelay']['updatedAt'],
                        advisory_url=airport['groundDelay']['advisoryUrl'],
                        departure_scope=airport['groundDelay']['departureScope'],
                        included_facilities=airport['groundDelay']['includedFacilities'],
                        included_flights=airport['groundDelay']['includedFlights'],
                    )
                    self.delay_count += 1
                
                else:
                    self.ground_delay = GroundDelay(self.code)

                if airport['airportClosure']:
                    self.closure = Closure(
                        airport=self.code,
                        status=True,
                        start=airport['airportClosure']['startTime'],
                        end=airport['airportClosure']['endTime'],
                        update_time=airport['airportClosure']['updatedAt'],
                        notam=airport['airportClosure']['simpleText'],
                    )

                elif airport['freeForm']:
                    # API doesn't always put closures in the actual closure field so check freeform
                    if "CLSD" in airport['freeForm']['simpleText']:
                        self.closure = Closure(
                            airport=self.code,
                            status=True,
                            start=airport['freeForm']['startTime'],
                            end=airport['freeForm']['endTime'],
                            update_time=airport['freeForm']['updatedAt'],
                            notam=airport['freeForm']['simpleText'],
                        )

                else:
                    self.closure = Closure(self.code)

                if self.delay_count > 0:
                    self.delay = True                

                return self

            
        # if airport is not in data then no programs are active
        self.arrive_delay = ArriveDepartDelay(self.code)
        self.depart_delay = ArriveDepartDelay(self.code)
        self.ground_stop = GroundStop(self.code)
        self.ground_delay = GroundDelay(self.code)
        self.closure = Closure(self.code)

                

async def get_airport_delays(code, session: ClientSession):
    results = Airport(code, session)
    await results.update()

    return results
