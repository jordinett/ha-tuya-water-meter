# Tuya Water Meter (ZNSB Category) for Home Assistant

Custom integration for Home Assistant to fetch water meter data directly from the **Tuya Developer Cloud API**. 

⚠️ **IMPORTANT: This integration is strictly specific to Tuya Water Meters under the `znsb` category** (e.g., Zigbee valve-controlled ultrasonic water meters with Product ID `vuwtqx0t`). It will completely ignore any other Tuya devices (lights, switches, etc.) to avoid conflicts with the official Tuya integration or Local Tuya.

## Features
- **Dynamic Entity Creation:** Automatically exposes all supported data points from the Tuya Developer Portal.
- **Total Consumption:** Converts `water_use_data` correctly to cubic meters ($m^3$) for the Home Assistant Energy/Water dashboard.
- **Battery Status:** Exposes the battery voltage formatted in Volts ($V$).
- **Advanced Diagnostics:** Splits the Tuya `fault` bitmap into **14 independent binary sensors** (Low battery alarm, leakage, low temperature, overflow, tamper, etc.).
- **Optimized Polling:** Requests data once every hour to match the device's typical 12-hour sleeping cycle, preventing Tuya API rate-limiting issues.

## Setup Requirements
You will need your Tuya IoT Platform credentials:
1. **Client ID** (Access ID)
2. **Client Secret** (Access Secret)
3. **Account UID** (Found under *Cloud > Development > Your Project > Link Tuya App*)
4. **API Region** (e.g., `eu` for Europe)

## Changelog

Version 1.0.0: it is only a read only integration, it reads total water consumption and all the rest of the sensors and alarms

Version: 1.1.0: Valve state becomes a switch, in version 1.0.0 you could only read the valve state (true or false - valve opened or closed) in this version you can open and close the valve directly from the integration.
