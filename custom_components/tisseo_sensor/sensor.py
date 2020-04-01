import asyncio
from datetime import timedelta
import logging
import urllib.request
import json

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

import xml.etree.ElementTree as ET

REQUIREMENTS = []

_LOGGER = logging.getLogger(__name__)

CONF_ATTRIBUTION = "Data provided by TISSEO Open API"
CONF_STOPID = 'stop_id'
CONF_ROUTENUMBER = 'route_number'
CONF_APIKEY = 'api_key'

DEFAULT_NAME = 'Translink Next Bus'
DEFAULT_ICON = 'mdi:bus'

SCAN_INTERVAL = timedelta(seconds=240)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_STOPID): cv.string,
    vol.Required(CONF_APIKEY): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    #_LOGGER.debug("start async setup platform")

    name = config.get(CONF_NAME)
    stopid = config.get(CONF_STOPID)
    apikey = config.get(CONF_APIKEY)

    session = async_get_clientsession(hass)

    async_add_devices(
        [TisseoSensor(name, stopid, apikey)], update_before_add=True)



class TisseoLine:

    def __init__(self, lineName):
        super().__init__()
        self.name = lineName
        self.timeList = []

    def addTime(self, time):
        self.timeList.append(time)


class BusLineManager:
    __instance = None

    lineList = []

    @staticmethod
    def getInstance():
        """ Static access method. """
        if BusLineManager.__instance == None:
            BusLineManager()
        return BusLineManager.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if BusLineManager.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            BusLineManager.__instance = self

    def printLinelist(self):
        print("Recorded Lines")
        for line in self.lineList:
            print(line.name)
            for time in line.timeList:
                print(time)

    def addLineAndTime(self, lineName, time):
        tempLine = None

        for currentLine in self.lineList:
            if currentLine.name == lineName:
                tempLine = currentLine
                if len(currentLine.timeList) < 2:
                    currentLine.addTime(time)
                

        if tempLine == None:
            print("new line: " + lineName)
            tempLine = TisseoLine(lineName)
            tempLine.addTime(time)
            self.lineList.append(tempLine)
        # self.printLinelist()


class TisseoSensor(Entity):

    def __init__(self, name, stopid, apikey):
        """Initialize the sensor."""
        self._name = name
        self._stopid = stopid
        self._apikey = apikey
        self._state = None
        self._icon = DEFAULT_ICON

    @property
    def device_state_attributes(self):
        attr = {}

        tisseoFile = "/tmp/tisseo_" + self._stopid + ".json"
        tisseodata = json.load(open(tisseoFile))

        attr["stop_id"] = self._stopid

        print(tisseodata)

        departures = tisseodata['departures']
        departurelist = departures['departure']

        for dep in departurelist:
            direction = dep['destination'][0]['name']
            fullName = dep['line']['shortName'] + " | " + direction

            BusLineManager.getInstance().addLineAndTime(
                fullName, dep['dateTime'])

        busCount = 0
        for line in BusLineManager.getInstance().lineList:
            attr["bus_" + str(busCount)] = line.name
            if len(line.timeList) >= 1:
                attr["bus_" + str(busCount) + "next1"] = line.timeList[0]
            else:
                attr["bus_" + str(busCount) + "next1"] = "none"
            if len(line.timeList) >= 2:
                attr["bus_" + str(busCount) + "next2"] = line.timeList[1]
            else:
                attr["bus_" + str(busCount) + "next2"] = "none"
            busCount +=1

        return attr

    @asyncio.coroutine
    def async_update(self):

        TISSEOURL="https://api.tisseo.fr/v1/stops_schedules.json?stopPointId=" + \
            self._stopid+"&key="+self._apikey
        tisseoFile = "/tmp/tisseo_" + self._stopid + ".json"

        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(TISSEOURL, tisseoFile)
        tisseodata = json.load(open(tisseoFile))


        self._state = 1
        return self._state

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state
