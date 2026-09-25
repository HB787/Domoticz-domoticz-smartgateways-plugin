# SmartGateways P1 Smart Meter Plugin for Domoticz

A robust, clean, and user-friendly Domoticz Python plugin designed to retrieve P1 smart meter data from the **Smartgateways WiFi P1 adapter** via its local REST API.

---

## Features
* **Plug & Play:** Clean device creation out-of-the-box with standard utility types and correct naming conventions.
* **Flexible Polling:** Adjustable polling interval via a convenient dropdown menu (ranging from 20 seconds to 5 minutes).
* **Comprehensive Data:** Supports main P1 energy totals, electricity consumption, gas meter, and solar return (kWh).
* **Optional Metrics:** Easily toggle phase details (L1-L3 voltages and power) and power failure statistics via Domoticz hardware settings.
* **Clear Logging:** Structured startup messages and regular update logs to easily monitor device synchronisation.

---

## Installation

1. Navigate to your Domoticz plugins directory using your terminal:
   ```bash
   cd ~/domoticz/plugins/

   Clone this repository into a dedicated folder (e.g., SmartGatewaysCustom):
   git clone [https://github.com/HB787/Domoticz-domoticz-smartgateways-plugin.git](https://github.com/HB787/Domoticz-domoticz-smartgateways-plugin.git) SmartGatewaysCustom

   Restart domoticz:
   sudo systemctl restart domoticz.sh

   Configuration

   In Domoticz, go to Setup > Hardware.

   Add a new hardware entry and select SmartGateways REST API from the type dropdown.

   Configure the parameters to your liking:

        IP Address or Hostname: Enter the URL or hostname of your adapter (default: http://connectix_smartmeter.local).

        Port: Port number of the adapter (default: 82).

        Poll Interval: Choose your preferred update frequency (e.g., 30 seconds or 1 minute).

        Toggles: Enable or disable Gas, Solar panels, Phase details, and Power failures based on your setup.

    Click Add.

Author & Version

    Author: Harry Berg

    Version: 1.0.0

License

This project is open-source and available under the MIT License.
