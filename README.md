# Tisseo Sensor

This is home assistant custom component to pull bus times from Tisseo Open API.  This is pretty limited right now, simply pulling in the next two times for a given stop.

There is a lovelace ui custom card available here: https://github.com/math0ne/translink-card


### Manual Installation

Copy this folder to `<config_dir>/custom_components/tisseo_sensor/`.

### HACS Custom Install

1. Go to the community tab of your home assistant installation
2. Click settings
3. Add "https://github.com/maxPeuck/tisseo-sensor" with the type **Integration**
4. Click Save
5. Restart home assistant

### Usage

Add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: tisseo_sensor
    api_key: XXX
    stop_id: 58652
```
### Credits
