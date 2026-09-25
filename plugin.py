"""
<plugin key="SmartGatewaysCustom" name="SmartGateways REST API" author="Harry Berg" version="1.0.0" wikilink="https://github.com/HB787/Domoticz-domoticz-smartgateways-plugin" externallink="">
    <params>
        <param field="Address" label="IP Address or Hostname" width="200px" required="true" default="http://connectix_smartmeter.local"/>
        <param field="Port" label="Port" width="100px" required="true" default="82"/>
        <param field="Mode1" label="Poll Interval" width="120px">
            <options>
                <option label="20 seconds" value="20"/>
                <option label="30 seconds" value="30" default="true"/>
                <option label="1 minute" value="60"/>
                <option label="2 minutes" value="120"/>
                <option label="3 minutes" value="180"/>
                <option label="5 minutes" value="300"/>
            </options>
        </param>
        <param field="Mode2" label="Read Gas Meter" width="75px">
            <options>
                <option label="Yes" value="True" default="true"/>
                <option label="No" value="False"/>
            </options>
        </param>
        <param field="Mode3" label="Read Solar Panels (kWh)" width="75px">
            <options>
                <option label="Yes" value="True"/>
                <option label="No" value="False" default="true"/>
            </options>
        </param>
        <param field="Mode4" label="Read Phase Details (L1-L3)" width="75px">
            <options>
                <option label="Yes" value="True"/>
                <option label="No" value="False" default="true"/>
            </options>
        </param>
        <param field="Mode5" label="Read Power Failures" width="75px">
            <options>
                <option label="Yes" value="True"/>
                <option label="No" value="False" default="true"/>
            </options>
        </param>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import urllib.request
import json

class BasePlugin:
    def __init__(self):
        return

    def onStart(self):
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
            
        Domoticz.Log("-----------------------------------------------------------------")
        Domoticz.Log(" SmartGateways REST API Plugin v1.0.0 by Harry Berg started.")
        Domoticz.Log("-----------------------------------------------------------------")
        
        # 1. P1 Power Total (Main smart meter) - Always created
        if 200 not in Devices:
            Domoticz.Device(Name="P1 Power Total", Unit=200, Type=250, Subtype=1, Used=1).Create()
            
        # 2. Electricity Usage (kWh Counter) - Always created
        if 202 not in Devices:
            Domoticz.Device(Name="Electricity Usage", Unit=202, TypeName="kWh", Used=1).Create()
            
        # 3. Gas Meter (Optional via Mode2)
        if Parameters["Mode2"] == "True":
            if 201 not in Devices:
                Domoticz.Device(Name="Gas Meter", Unit=201, Type=251, Subtype=2, Used=1).Create()
            
        # 4. Solar Panels / Return (Optional via Mode3)
        if Parameters["Mode3"] == "True":
            if 205 not in Devices:
                Domoticz.Device(Name="Solar Panels", Unit=205, TypeName="kWh", Used=1).Create()

        # 5. Phase Details & Voltages (Optional via Mode4)
        if Parameters["Mode4"] == "True":
            if 210 not in Devices: Domoticz.Device(Name="Voltage L1", Unit=210, TypeName="Voltage", Used=1).Create()
            if 211 not in Devices: Domoticz.Device(Name="Voltage L2", Unit=211, TypeName="Voltage", Used=1).Create()
            if 212 not in Devices: Domoticz.Device(Name="Voltage L3", Unit=212, TypeName="Voltage", Used=1).Create()
            if 213 not in Devices: Domoticz.Device(Name="Power L1", Unit=213, TypeName="Usage", Used=1).Create()
            if 214 not in Devices: Domoticz.Device(Name="Power L2", Unit=214, TypeName="Usage", Used=1).Create()
            if 215 not in Devices: Domoticz.Device(Name="Power L3", Unit=215, TypeName="Usage", Used=1).Create()

        # 6. Power Failures (Optional via Mode5)
        if Parameters["Mode5"] == "True":
            if 220 not in Devices: Domoticz.Device(Name="Power Failures", Unit=220, TypeName="Text", Used=1).Create()
            if 221 not in Devices: Domoticz.Device(Name="Long Power Failures", Unit=221, TypeName="Text", Used=1).Create()

        Domoticz.Heartbeat(int(Parameters["Mode1"]))

    def onStop(self):
        Domoticz.Log("SmartGateways plugin stopped.")

    def onHeartbeat(self):
        try:
            base_address = Parameters["Address"].strip() if Parameters["Address"].strip() != "" else "http://connectix_smartmeter.local"
            
            if base_address.startswith("http://") or base_address.startswith("https://"):
                url = f"{base_address}:{Parameters['Port']}/smartmeter/api/read"
            else:
                url = f"http://{base_address}:{Parameters['Port']}/smartmeter/api/read"
            
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    # Main P1 energy update
                    t1 = int(float(data.get("EnergyDeliveredTariff1", 0)) * 1000)
                    t2 = int(float(data.get("EnergyDeliveredTariff2", 0)) * 1000)
                    r1 = int(float(data.get("EnergyReturnedTariff1", 0)) * 1000)
                    r2 = int(float(data.get("EnergyReturnedTariff2", 0)) * 1000)
                    act_use = int(float(data.get("PowerDelivered_total", 0)) * 1000)
                    act_ret = int(float(data.get("PowerReturned_total", 0)) * 1000)
                    
                    p1_svalue = f"{t1};{t2};{r1};{r2};{act_use};{act_ret}"
                    if 200 in Devices:
                        Devices[200].Update(nValue=0, sValue=p1_svalue)
                        Domoticz.Log(f"Updated device 'P1 Power Total' (sValue: {p1_svalue})")
                        
                    # Electricity Usage update
                    if 202 in Devices:
                        total_consumed_wh = int((float(data.get("EnergyDeliveredTariff1", 0)) + float(data.get("EnergyDeliveredTariff2", 0))) * 1000)
                        elec_svalue = f"{act_use};{total_consumed_wh}"
                        Devices[202].Update(nValue=0, sValue=elec_svalue)
                        Domoticz.Log(f"Updated device 'Electricity Usage' (sValue: {elec_svalue})")
                        
                    # Gas Meter update
                    if Parameters["Mode2"] == "True" and 201 in Devices:
                        gas_val = int(float(data.get("GasDelivered", 0)) * 1000)
                        Devices[201].Update(nValue=0, sValue=str(gas_val))
                        Domoticz.Log(f"Updated device 'Gas Meter' (sValue: {gas_val})")
                        
                    # Solar Panels update
                    if Parameters["Mode3"] == "True" and 205 in Devices:
                        total_returned_wh = int((float(data.get("EnergyReturnedTariff1", 0)) + float(data.get("EnergyReturnedTariff2", 0))) * 1000)
                        solar_svalue = f"{act_ret};{total_returned_wh}"
                        Devices[205].Update(nValue=0, sValue=solar_svalue)
                        Domoticz.Log(f"Updated device 'Solar Panels' (sValue: {solar_svalue})")
                        
                    # Phase details update
                    if Parameters["Mode4"] == "True":
                        if 210 in Devices: Devices[210].Update(nValue=0, sValue=str(data.get("Voltage_l1", 0)))
                        if 211 in Devices: Devices[211].Update(nValue=0, sValue=str(data.get("Voltage_l2", 0)))
                        if 212 in Devices: Devices[212].Update(nValue=0, sValue=str(data.get("Voltage_l3", 0)))
                        if 213 in Devices: Devices[213].Update(nValue=0, sValue=str(data.get("PowerDelivered_l1", 0)))
                        if 214 in Devices: Devices[214].Update(nValue=0, sValue=str(data.get("PowerDelivered_l2", 0)))
                        if 215 in Devices: Devices[215].Update(nValue=0, sValue=str(data.get("PowerDelivered_l3", 0)))
                        Domoticz.Log("Updated phase details (L1-L3)")

                    # Power failure statistics update
                    if Parameters["Mode5"] == "True":
                        if 220 in Devices and "PowerFailures" in data: 
                            Devices[220].Update(nValue=0, sValue=str(data.get("PowerFailures")))
                        if 221 in Devices and "LongPowerFailures" in data: 
                            Devices[221].Update(nValue=0, sValue=str(data.get("LongPowerFailures")))

                else:
                    Domoticz.Error(f"HTTP error fetching SmartGateways API: {response.status}")
        except Exception as e:
            Domoticz.Error(f"Connection error with SmartGateways API: {str(e)}")

global _plugin
_plugin = BasePlugin()

def onStart():
    _plugin.onStart()

def onStop():
    _plugin.onStop()

def onHeartbeat():
    _plugin.onHeartbeat()