# How to monitor Velocloud SD-WAN DHCPv6 IPv6 interface prefix
Your DHCPv6 prefix delegation (DP) assigned prefix from your ISP can change from time to time. In more complex network designs it can be problematic to keep track of the changes.

Your can use attached python script to monitor these changes and run it from cron or other tools like HomeAssistant. The python script uses API v1 and username/password authentication. The API documentation can be found here: https://developer.broadcom.com/xapis/velocloud-orchestrator-api/5.4.0/

In order to make python script work, you need to configure:

1. VCO URL
2. username/password
3. IPv6 prefix from your ISP
4. Your edge ID
5. Interface name you want to monitor (for example 'GE3')

In order to make python script work in HomeAssistant, you need to:

1. Save the python script to `/config` directory and make it executable (`chmod +x`)
2. Create following section in `configuration.yaml` file (change the name and scan onterval as you see fit):
```
command_line:
  sensor:
    name: SDWAN_IPv6_prefix
    unique_id: sdwan_ipv6_prefix
    command: "python3 /config/interfacePrefix.py"
    scan_interval: 3600
    value_template: "{{ value_json.state }}"
    json_attributes_path: "$.attributes"
    json_attributes:
      - current_ipv6_address
      - expected_prefix
      - interface
      - last_check_time
      - message
```
3. Restart the HomeAssistant for changes to make effect
4. Create an automation to monitor the prefix changes, and in addition moniro any of the attributes, for example:
```
alias: SD-WAN IPv6 prefix check
description: ""
trigger:
  - platform: state
    entity_id:
      - sensor.sdwan_ipv6_prefix
condition:
  - condition: not
    conditions:
      - condition: template
        value_template: "{{ 'Prefix matches' in states.sensor.sdwan_ipv6_prefix.state }}"
action:
  - service: notify.<your_email>
    metadata: {}
    data:
      message: SD-WAN IPv6 prefix doesn't match
      title: SD-WAN IPv6 prefix doesn't match
      target: <your_email>
mode: single
```

Should you need to debug the python script in HomeAssistant, follow a guide such as this https://community.home-assistant.io/t/execute-in-home-assistant-container-context/415031/4 or https://community.home-assistant.io/t/sshing-from-a-command-line-sensor-or-shell-command/258731. The idea here is to launch it in homeassistant container scope...

Don't forget to set the orchestrator WAN interface in question to ``DHCP Stateless`` mode, assuming it is DHCPv6 PD changes you want to track, otherwise the ``IPv6Address`` field might not get populated.
