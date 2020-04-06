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
from custom_components.hacs.globals import get_hacs
from homeassistant.helpers.entity import Entity

import xml.etree.ElementTree as ET

REQUIREMENTS = []

_LOGGER = logging.getLogger(__name__)

CONF_ATTRIBUTION = "Data provided by TISSEO Open API"
CONF_STOPID = 'stop_id'
CONF_ROUTENUMBER = 'route_number'
CONF_APIKEY = 'api_key'

DEFAULT_NAME = 'Tisseo Next Bus'
DEFAULT_ICON = 'mdi:bus'

SCAN_INTERVAL = timedelta(seconds=120)

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

    def __init__(self, lineName, shortName, direction, color):
        super().__init__()
        self._name = lineName
        self._shortName = shortName
        self._direction = direction
        self._color = color
        self._timeList = []

    def addTime(self, time):
        self._timeList.append(time)


class BusLineManager:
    __instance = None

    _lineList = []

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

    def reset(self):
        self._lineList.clear()

    def printLinelist(self):
        print("Recorded Lines")
        for line in self._lineList:
            print(line.name)
            for time in line._timeList:
                print(time)

    def addAttributes(self, fullName, shortName, direction, color, time):
        tempLine = None

        for currentLine in self._lineList:
            if currentLine._name == fullName:
                tempLine = currentLine
                if len(currentLine._timeList) < 2:
                    currentLine.addTime(time)

        if tempLine == None:
            print("new line: " + fullName)
            tempLine = TisseoLine(fullName, shortName, direction, color)
            tempLine.addTime(time)
            self._lineList.append(tempLine)
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

        #hacs = get_hacs()
        # hacs.logger.critical(str(tisseodata))

        departures = tisseodata['departures']
        departurelist = departures['departure']

        BusLineManager.getInstance().reset()

        for dep in departurelist:
            direction = dep['destination'][0]['name']
            shortName = dep['line']['shortName']
            fullName = shortName + " | " + direction
            lineColor = dep['line']['color']
            BusLineManager.getInstance().addAttributes(
                fullName, shortName, direction, lineColor, dep['dateTime'])

        busCount = 0
        dataString = ""
        for line in BusLineManager.getInstance().lineList:
            attr["bus_" + str(busCount)] = line.name
            if len(line.timeList) >= 1:
                attr["bus_" + str(busCount) + "next1"] = line._timeList[0]
            else:
                attr["bus_" + str(busCount) + "next1"] = "none"
            if len(line.timeList) >= 2:
                attr["bus_" + str(busCount) + "next2"] = line._timeList[1]
            else:
                attr["bus_" + str(busCount) + "next2"] = "none"
            attr["bus_" + str(busCount) + "color"] = line._lineColor
            busCount += 1

            dataString = dataString + "#" + line._shortName + \
                "|" + line._direction+"|"+line._color+"|" + line._timeList[0]+"|" + line._timeList[1]


        attr['dataString'] = dataString
        attr['expirationDate'] = tisseodata['expirationDate']
        return attr

    @asyncio.coroutine
    def async_update(self):

        TISSEOURL = "https://api.tisseo.fr/v1/stops_schedules.json?stopPointId=" + \
            self._stopid+"&key="+self._apikey
        tisseoFile = "/tmp/tisseo_" + self._stopid + ".json"
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(TISSEOURL, tisseoFile)
        tisseodata = json.load(open(tisseoFile))

        #hacs = get_hacs()
        # hacs.logger.critical(tisseodata['expirationDate'])

        self._state = tisseodata['expirationDate']
        return self._state

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state
