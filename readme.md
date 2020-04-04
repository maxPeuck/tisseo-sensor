[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

# Translink Sensor

This is home assistant custom component to pull bus times from Tisseo Open API.  This is pretty limited right now, simply pulling in the next two times for a given stop. 

There is a lovelace ui custom card available here: https://github.com/math0ne/translink-card


### Installation

Copy this folder to `<config_dir>/custom_components/tisseo_sensor/`.

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

This based on the work of:

* math0ne : https://github.com/math0ne/translink-sensor
* johnlarusic: https://github.com/johnlarusic/lebus
* amaximus: https://github.com/amaximus/bkk_stop