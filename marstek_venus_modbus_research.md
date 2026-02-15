# Marstek Venus A - Modbus TCP Research Findings

Generated: 2026-02-14

---

## 1. Modbus TCP Support

YES - The Marstek Venus series (including Venus A, C, D, E) supports Modbus TCP communication.

### Connection Methods

| Method | Description |
|--------|-------------|
| **Direct Ethernet (V3 models)** | Venus E/D V3 models have a native RJ45 Ethernet port enabling direct Modbus TCP on port 502 |
| **RS485-to-WiFi/Ethernet bridge** | Earlier models (V1/V2) require an RS485 adapter (Elfin EW11, PUSR DR134, Waveshare RS485-to-ETH) bridging the battery RS485 port to TCP |

### Firmware Note
Firmware version V139+ or V144 is required to enable Modbus functionality. Native Modbus TCP (without adapter) is available on V3 firmware (firmware 139+).

### Important Constraint
Only **one simultaneous Modbus TCP connection** is allowed on port 502. Multiple clients will be rejected.

---

## 2. Default Connection Settings

| Parameter | Value |
|-----------|-------|
| Protocol | Modbus TCP (or Modbus RTU-over-TCP via adapter) |
| Port | **502** |
| Slave ID / Unit ID | **1** (default, configurable) |
| Timeout | 5 seconds (recommended) |
| Message wait | 35-80 ms between messages |
| Byte order | Big-endian |

### RS485 Physical Settings (for adapter-based connections)
| Parameter | Value |
|-----------|-------|
| Baud rate | 115200 |
| Data bits | 8 |
| Stop bits | 1 |
| Parity | None |

### RS485 Pin Wiring (Marstek connector to adapter)
| Marstek Pin | Signal | Wire Color |
|-------------|--------|------------|
| 1 | A (differential +) | Yellow |
| 2 | B (differential -) | Red |
| 3 | GND | Black |
| 5 | VCC | Black |

---

## 3. Complete Modbus Register Map

All registers are **holding registers** (function code 03 for read, 06/16 for write).

### Register Map Key
- **RO** = Read Only
- **RW** = Read/Write (requires RS485 control mode enabled first for 42xxx range)
- **WO** = Write Only

---

### 3.1 Device Information Registers (Read Only)

| Address | Count | Data Type | Scale | Unit | Key | Description |
|---------|-------|-----------|-------|------|-----|-------------|
| 30200 | 1 | uint16 | - | - | ems_version | EMS firmware version (V3) |
| 30202 | 1 | uint16 | - | - | vms_version | VMS firmware version (V3) |
| 30204 | 1 | uint16 | - | - | bms_version | BMS firmware version (V3) |
| 30304 | 6 | char | - | - | mac_address | MAC address (V3) |
| 30350 | 6 | char | - | - | comm_module_firmware | Comm module firmware (V3) |
| 30402 | 6 | char | - | - | mac_address | MAC address (V1/V2) |
| 30800 | 6 | char | - | - | comm_module_firmware | Comm module firmware (V1/V2) |
| 31000 | 10 | char | - | - | device_name | Device name string |
| 31100 | 1 | uint16 | 0.01 | - | software_version | Software version (V1/V2) |
| 31101 | 1 | uint16 | - | - | ems_version | EMS version (V1/V2) |
| 31102 | 1 | uint16 | - | - | bms_version | BMS version (V1/V2) |
| 31200 | 10 | char | - | - | sn_code | Serial number |

---

### 3.2 Connectivity / Status Registers (Read Only)

| Address | Count | Data Type | Scale | Unit | Key | Description |
|---------|-------|-----------|-------|------|-----|-------------|
| 30300 | 1 | uint16 | - | boolean | wifi_status | WiFi connected (0=No, 1=Yes) |
| 30302 | 1 | uint16 | - | boolean | cloud_status | Cloud connected (0=No, 1=Yes) |
| 30303 | 1 | uint16 | -1 | dBm | wifi_signal_strength | WiFi signal strength (negated) |

---

### 3.3 Battery Measurement Registers (Read Only)

| Address | Count | Data Type | Scale | Unit | Key | Description |
|---------|-------|-----------|-------|------|-----|-------------|
| 30001 | 1 | int16 | 1 | W | battery_power | Battery DC power (V3) |
| 30100 | 1 | uint16 | 0.01 | V | battery_voltage | Battery voltage (V3) |
| 30101 | 1 | int16 | 0.1 | A | battery_current | Battery current (V3) |
| 32100 | 1 | uint16 | 0.01 | V | battery_voltage | Battery voltage (V1/V2) |
| 32101 | 1 | int16 | 0.01 | A | battery_current | Battery current, +charge/-discharge (V1/V2) |
| 32102 | 2 | int32 | 1 | W | battery_power | Battery DC power (V1/V2) |
| 32104 | 1 | uint16 | 1 | % | battery_soc | State of charge (V1/V2) |
| 32105 | 1 | uint16 | 0.001 | kWh | battery_total_energy | Battery nameplate capacity |
| 37005 | 1 | uint16 | 1 | % | battery_soc | State of charge (V3) |

---

### 3.4 AC Grid Measurement Registers (Read Only)

| Address | Count | Data Type | Scale | Unit | Key | Description |
|---------|-------|-----------|-------|------|-----|-------------|
| 30006 | 1 | int16 | 1 | W | ac_power | AC grid power (V3), +export/-import |
| 32200 | 1 | uint16 | 0.1 | V | ac_voltage | AC grid voltage |
| 32201 | 1 | int16 | 0.01 | A | ac_current | AC grid current (V1/V2) |
| 32202 | 2 | int32 | 1 | W | ac_power | AC power (V1/V2), +discharge/-charge |
| 32204 | 1 | int16 | 0.01 | Hz | ac_frequency | AC grid frequency |
| 37004 | 1 | int16 | 0.004 | A | ac_current | AC grid current (V3) |

---

### 3.5 AC Off-Grid Measurement Registers (Read Only)

| Address | Count | Data Type | Scale | Unit | Key | Description |
|---------|-------|-----------|-------|------|-----|-------------|
| 32300 | 1 | uint16 | 0.1 | V | ac_offgrid_voltage | Off-grid output voltage |
| 32301 | 1 | uint16 | 0.01 | A | ac_offgrid_current | Off-grid output current |
| 32302 | 2 | int32 | 1 | W | ac_offgrid_power | Off-grid output power (V1/V2 only) |

---

### 3.6 Energy Counter Registers (Read Only)

| Address | Count | Data Type | Scale | Unit | Key | Description |
|---------|-------|-----------|-------|------|-----|-------------|
| 33000 | 2 | uint32 | 0.01 | kWh | total_charging_energy | Total lifetime charging energy |
| 33002 | 2 | int32 | 0.01 | kWh | total_discharging_energy | Total lifetime discharging energy |
| 33004 | 2 | uint32 | 0.01 | kWh | total_daily_charging_energy | Daily charging energy |
| 33006 | 2 | int32 | 0.01 | kWh | total_daily_discharging_energy | Daily discharging energy |
| 33008 | 2 | uint32 | 0.01 | kWh | total_monthly_charging_energy | Monthly charging energy |
| 33010 | 2 | int32 | 0.01 | kWh | total_monthly_discharging_energy | Monthly discharging energy |

---

### 3.7 Temperature Registers (Read Only)

| Address | Count | Data Type | Scale | Unit | Key | Description |
|---------|-------|-----------|-------|------|-----|-------------|
| 35000 | 1 | int16 | 0.1 | degC | internal_temperature | Internal battery temperature |
| 35001 | 1 | int16 | 0.1 | degC | internal_mos1_temperature | MOS1 transistor temperature |
| 35002 | 1 | int16 | 0.1 | degC | internal_mos2_temperature | MOS2 transistor temperature |
| 35010 | 1 | int16 | 1 (V1/V2) / 0.1 (V3) | degC | max_cell_temperature | Maximum cell temperature |
| 35011 | 1 | int16 | 1 (V1/V2) / 0.1 (V3) | degC | min_cell_temperature | Minimum cell temperature |
| 35111 | 1 | uint16 | 0.1 | A | bms_charge_current_limit | BMS max charge current |
| 35112 | 1 | uint16 | 0.1 | A | bms_discharge_current_limit | BMS max discharge current |

---

### 3.8 Cell Voltage Registers (Read Only)

| Address | Count | Data Type | Scale | Unit | Key | Description |
|---------|-------|-----------|-------|------|-----|-------------|
| 34018 | 1 | int16 | 0.001 | V | cell_1_voltage | Cell 1 voltage |
| 34019 | 1 | int16 | 0.001 | V | cell_2_voltage | Cell 2 voltage |
| 34020 | 1 | int16 | 0.001 | V | cell_3_voltage | Cell 3 voltage |
| 34021 | 1 | int16 | 0.001 | V | cell_4_voltage | Cell 4 voltage |
| 34022 | 1 | int16 | 0.001 | V | cell_5_voltage | Cell 5 voltage |
| 34023 | 1 | int16 | 0.001 | V | cell_6_voltage | Cell 6 voltage |
| 34024 | 1 | int16 | 0.001 | V | cell_7_voltage | Cell 7 voltage |
| 34025 | 1 | int16 | 0.001 | V | cell_8_voltage | Cell 8 voltage |
| 34026 | 1 | int16 | 0.001 | V | cell_9_voltage | Cell 9 voltage |
| 34027 | 1 | int16 | 0.001 | V | cell_10_voltage | Cell 10 voltage |
| 34028 | 1 | int16 | 0.001 | V | cell_11_voltage | Cell 11 voltage |
| 34029 | 1 | int16 | 0.001 | V | cell_12_voltage | Cell 12 voltage |
| 34030 | 1 | int16 | 0.001 | V | cell_13_voltage | Cell 13 voltage |
| 34031 | 1 | int16 | 0.001 | V | cell_14_voltage | Cell 14 voltage |
| 34032 | 1 | int16 | 0.001 | V | cell_15_voltage | Cell 15 voltage |
| 34033 | 1 | int16 | 0.001 | V | cell_16_voltage | Cell 16 voltage |
| 37007 | 1 | int16 | 0.001 | V | max_cell_voltage | Maximum cell voltage |
| 37008 | 1 | int16 | 0.001 | V | min_cell_voltage | Minimum cell voltage |

---

### 3.9 Status and Alarm Registers (Read Only)

| Address | Count | Data Type | Unit | Key | Description |
|---------|-------|-----------|------|-----|-------------|
| 35100 | 1 | uint16 | - | inverter_state | Inverter state: 0=Sleep, 1=Standby, 2=Charge, 3=Discharge, 4=Backup Mode, 5=OTA Upgrade, 6=Bypass |
| 36000 | 2 | uint16 | bit-field | alarm_status | Alarm flags (see bits below) |
| 36100 | 4 | uint16 | bit-field | fault_status | Fault flags (see bits below) |

#### Alarm Status Bit Definitions (register 36000)
| Bit | Description |
|-----|-------------|
| 0 | PLL Abnormal Restart |
| 1 | Overtemperature Limit |
| 2 | Low Temperature Limit |
| 3 | Fan Abnormal Warning |
| 4 | Low Battery SOC Warning |
| 5 | Output Overcurrent Warning |
| 6 | Abnormal Line Sequence Detection |
| 16 | WiFi Abnormal |
| 17 | BLE Abnormal |
| 18 | Network Abnormal |
| 19 | CT Connection Abnormal |

#### Fault Status Bit Definitions (register 36100)
| Bit | Description |
|-----|-------------|
| 0 | Grid Overvoltage |
| 1 | Grid Undervoltage |
| 2 | Grid Overfrequency |
| 3 | Grid Underfrequency |
| 4 | Grid Peak Voltage |
| 5 | Current Dcover |
| 6 | Voltage Dcover |
| 16 | BAT Overvoltage |
| 17 | BAT Undervoltage |
| 18 | BAT Overcurrent |
| 19 | BAT Low SOC |
| 20 | BAT Communication Failure |
| 21 | BMS Protect |
| 32 | Inverter Soft Start Timeout |
| 33 | Self-checking Failure |
| 34 | EEPROM Failure |
| 35 | Other System Failure |
| 48 | Hardware Bus Overvoltage |
| 49 | Hardware Output Overcurrent |
| 50 | Hardware Trans Overcurrent |
| 51 | Hardware Battery Overcurrent |
| 52 | Hardware Protection |
| 53 | Output Overcurrent |
| 54 | High Voltage Bus Overvoltage |
| 55 | High Voltage Bus Undervoltage |
| 56 | Overpower Protection |
| 57 | FSM Abnormal |
| 58 | Overtemperature Protection |

---

### 3.10 Configuration Registers (Read Only)

| Address | Count | Data Type | Scale | Unit | Key | Description |
|---------|-------|-----------|-------|------|-----|-------------|
| 41010 | 1 | uint16 | - | boolean | discharge_limit_mode | Discharge limit mode enabled |
| 41100 | 1 | uint16 | - | - | modbus_address | Configured Modbus slave address |

---

### 3.11 Control Registers (Read/Write)

**IMPORTANT: To access registers 42000-42999, the battery must first be set to RS485 control mode (write 21930 to register 42000).**

| Address | Count | Data Type | Scale | Unit | Access | Values / Range | Description |
|---------|-------|-----------|-------|------|--------|----------------|-------------|
| 41000 | 1 | uint16 | - | - | WO | 21930 | Reset device (button) |
| 41001 | 1 | uint16 | - | - | WO | 21930 | Factory reset (button) |
| 41200 | 1 | uint16 | - | - | RW | 0=Enable, 1=Disable | Backup function toggle |
| 42000 | 1 | uint16 | - | - | RW | 21930=Enable, 21947=Disable (0x55AA / 0x55BB) | RS485 remote control mode |
| 42010 | 1 | uint16 | - | - | RW | 0=Stop, 1=Charge, 2=Discharge | Force charge/discharge mode |
| 42011 | 1 | uint16 | 1 | % | RW | 10-100 | Charge-to-SOC target |
| 42020 | 1 | uint16 | 1 | W | RW | 0-2500 | Set charge power setpoint |
| 42021 | 1 | uint16 | 1 | W | RW | 0-2500 | Set discharge power setpoint |
| 43000 | 1 | uint16 | - | - | RW | 0=Manual, 1=Anti-Feed, 2=Trade Mode | User work mode |
| 44000 | 1 | uint16 | 0.1 | % | RW | 80-100 | Charging cutoff capacity (SOC) |
| 44001 | 1 | uint16 | 0.1 | % | RW | 12-30 | Discharging cutoff capacity (SOC) |
| 44002 | 1 | uint16 | 1 | W | RW | 0-2500 | Maximum charge power limit |
| 44003 | 1 | uint16 | 1 | W | RW | 0-2500 | Maximum discharge power limit |
| 44100 | 1 | uint16 | - | - | RW | See grid standard values | Grid standard selection |
| 44100 | 1 | uint16 | - | - | RW | 0=Auto, 1=EN50549, 2=Netherlands, 3=Germany, 4=Austria, 5=UK, 6=Spain, 7=Poland, 8=Italy, 9=China | Grid standard |

---

### 3.12 Schedule Registers (Venus V3 only - registers 43100-43129)

6 time schedules, each using 5 consecutive 16-bit registers.

| Schedule | Start Address | Registers |
|----------|--------------|-----------|
| Schedule 1 | 43100 | 43100-43104 |
| Schedule 2 | 43105 | 43105-43109 |
| Schedule 3 | 43110 | 43110-43114 |
| Schedule 4 | 43115 | 43115-43119 |
| Schedule 5 | 43120 | 43120-43124 |
| Schedule 6 | 43125 | 43125-43129 |

**Per schedule register layout** (structure: big-endian `>HHHhH`):
| Offset | Data Type | Description |
|--------|-----------|-------------|
| +0 | uint16 | Weekday bitmask (bits 0-6 = Mon-Sun) |
| +1 | uint16 | Start time (hour*100 + minute, e.g. 0730 = 07:30) |
| +2 | uint16 | End time (hour*100 + minute) |
| +3 | int16 | Mode: >=100 = discharge (watts), <=-100 = charge (watts), -1 = Auto (anti-feed), 0 = disabled |
| +4 | uint16 | Enable flag (1=active, 0=inactive) |

---

## 4. V1/V2 vs V3 Register Differences

| Parameter | V1/V2 Address | V3 Address | Notes |
|-----------|--------------|-----------|-------|
| Battery voltage | 32100 | 30100 | Scale differs: 0.01 both |
| Battery current | 32101 | 30101 | Scale: 0.01 (V1/V2) vs 0.1 (V3) |
| Battery power | 32102 (int32, 2 regs) | 30001 (int16, 1 reg) | |
| Battery SOC | 32104 | 37005 | |
| AC current | 32201 | 37004 | Scale: 0.01 (V1/V2) vs 0.004 (V3) |
| AC power | 32202 (int32) | 30006 (int16) | |
| EMS version | 31101 | 30200 | |
| VMS version | N/A | 30202 | V3 only |
| BMS version | 31102 | 30204 | |
| MAC address | 30402 | 30304 | |
| Comm firmware | 30800 | 30350 | |
| Cell temp scale | 35010/35011 x1 | 35010/35011 x0.1 | |

---

## 5. Home Assistant Integrations

### 5.1 HACS Custom Integration (Recommended - No YAML required)
**Repository:** https://github.com/ViperRNMC/marstek_venus_modbus

- HACS-compatible custom component
- Supports Marstek Venus E v1/v2, v3, and D models
- No YAML configuration needed - configured via UI
- Requires Home Assistant Core 2025.9+
- Provides: sensors, binary sensors, select, switch, number, button entities
- Supports multiple batteries
- Tested adapters: Elfin EW11, PUSR DR134, Waveshare RS485-to-ETH, M5Stack

### 5.2 YAML-based Modbus Integration (ElfinEW11/adapter)
**Repository:** https://github.com/Superduper1969/MarstekVenus-ElfinEW11

Supports up to 3 batteries via YAML packages.

### 5.3 YAML-based Integration (Venus V3 direct Ethernet)
**Repository:** https://github.com/fonske/MarstekVenusV3-modbus-TCP-IP

Direct TCP for V3 models with native Ethernet port.

### 5.4 Venus E YAML Integration with Automations
**Repository:** https://github.com/reschcloud/marstek_venus_e_modbus_home_assistant

Includes automations and dashboard YAML.

### 5.5 WargamingPlayer Multi-Battery Integration
**Repository:** https://github.com/WargamingPlayer/HA-Marstek-Venus-E-Modbus

Supports 1-3 batteries, includes manual schedule control.

---

## 6. Home Assistant YAML Configuration Examples

### 6.1 Basic Modbus Connection Block

```yaml
# In configuration.yaml or packages/marstek.yaml
modbus:
  - name: marstek
    type: tcp
    host: 192.168.1.100     # IP of your battery / RS485 adapter
    port: 502
    timeout: 5
    delay: 1                # seconds between connection attempts
    message_wait_milliseconds: 35
```

### 6.2 Key Sensor Definitions

```yaml
    sensors:
      # Battery State of Charge
      - name: "Marstek Battery SOC"
        slave: 1
        address: 32104        # V1/V2; use 37005 for V3
        data_type: uint16
        unit_of_measurement: "%"
        device_class: battery
        state_class: measurement
        scan_interval: 30

      # Battery Voltage
      - name: "Marstek Battery Voltage"
        slave: 1
        address: 32100        # V1/V2; use 30100 for V3
        data_type: uint16
        scale: 0.01
        precision: 1
        unit_of_measurement: "V"
        device_class: voltage
        state_class: measurement
        scan_interval: 30

      # Battery Current (positive = charging, negative = discharging)
      - name: "Marstek Battery Current"
        slave: 1
        address: 32101        # V1/V2; use 30101 for V3
        data_type: int16
        scale: 0.01
        precision: 1
        unit_of_measurement: "A"
        device_class: current
        state_class: measurement
        scan_interval: 10

      # Battery Power (int32 = 2 registers)
      - name: "Marstek Battery Power"
        slave: 1
        address: 32102        # V1/V2; use 30001 (int16) for V3
        data_type: int32
        count: 2
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        scan_interval: 10

      # AC Grid Power
      - name: "Marstek AC Power"
        slave: 1
        address: 32202        # V1/V2; use 30006 (int16) for V3
        data_type: int32
        count: 2
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        scan_interval: 10

      # AC Grid Voltage
      - name: "Marstek AC Voltage"
        slave: 1
        address: 32200
        data_type: uint16
        scale: 0.1
        precision: 1
        unit_of_measurement: "V"
        device_class: voltage
        state_class: measurement
        scan_interval: 30

      # AC Frequency
      - name: "Marstek AC Frequency"
        slave: 1
        address: 32204
        data_type: int16
        scale: 0.01
        precision: 2
        unit_of_measurement: "Hz"
        device_class: frequency
        state_class: measurement
        scan_interval: 30

      # Internal Temperature
      - name: "Marstek Internal Temperature"
        slave: 1
        address: 35000
        data_type: int16
        scale: 0.1
        precision: 1
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement
        scan_interval: 30

      # Inverter State
      - name: "Marstek Inverter State"
        slave: 1
        address: 35100
        data_type: uint16
        scan_interval: 5

      # Total Charging Energy
      - name: "Marstek Total Charge Energy"
        slave: 1
        address: 33000
        data_type: uint32
        count: 2
        scale: 0.01
        precision: 2
        unit_of_measurement: "kWh"
        device_class: energy
        state_class: total_increasing
        scan_interval: 60

      # Total Discharging Energy
      - name: "Marstek Total Discharge Energy"
        slave: 1
        address: 33002
        data_type: int32
        count: 2
        scale: 0.01
        precision: 2
        unit_of_measurement: "kWh"
        device_class: energy
        state_class: total_increasing
        scan_interval: 60

      # Max Cell Voltage
      - name: "Marstek Max Cell Voltage"
        slave: 1
        address: 37007
        data_type: int16
        scale: 0.001
        precision: 3
        unit_of_measurement: "V"
        device_class: voltage
        state_class: measurement
        scan_interval: 30

      # Min Cell Voltage
      - name: "Marstek Min Cell Voltage"
        slave: 1
        address: 37008
        data_type: int16
        scale: 0.001
        precision: 3
        unit_of_measurement: "V"
        device_class: voltage
        state_class: measurement
        scan_interval: 30
```

### 6.3 Control Switches

```yaml
    switches:
      # Enable/Disable RS485 Remote Control Mode
      - name: "Marstek RS485 Control Mode"
        slave: 1
        address: 42000
        command_on: 21930   # 0x55AA
        command_off: 21947  # 0x55BB
        write_type: holding
        scan_interval: 10

      # Backup Function
      - name: "Marstek Backup Function"
        slave: 1
        address: 41200
        command_on: 0
        command_off: 1
        write_type: holding
        scan_interval: 10
```

### 6.4 Writing Control Commands via Service Calls

```yaml
# Enable RS485 control mode (MUST be done first before 42xxx registers)
action: modbus.write_register
data:
  hub: marstek
  slave: 1
  address: 42000
  value: 21930         # 0x55AA - enable

# Set work mode to Manual
action: modbus.write_register
data:
  hub: marstek
  slave: 1
  address: 43000
  value: 0             # 0=Manual, 1=Anti-Feed, 2=Trade Mode

# Force charge at 1000W
action: modbus.write_register
data:
  hub: marstek
  slave: 1
  address: 42010
  value: 1             # 1=Charge

action: modbus.write_register
data:
  hub: marstek
  slave: 1
  address: 42020
  value: 1000          # Watts (0-2500)

# Force discharge at 800W
action: modbus.write_register
data:
  hub: marstek
  slave: 1
  address: 42010
  value: 2             # 2=Discharge

action: modbus.write_register
data:
  hub: marstek
  slave: 1
  address: 42021
  value: 800           # Watts (0-2500)

# Stop forced mode
action: modbus.write_register
data:
  hub: marstek
  slave: 1
  address: 42010
  value: 0             # 0=Stop

# Charge to 90% SOC target
action: modbus.write_register
data:
  hub: marstek
  slave: 1
  address: 42011
  value: 90            # 10-100%

# Disable RS485 control mode when done
action: modbus.write_register
data:
  hub: marstek
  slave: 1
  address: 42000
  value: 21947         # 0x55BB - disable
```

### 6.5 Number Entities (Charge/Discharge Power)

```yaml
    numbers:
      - name: "Marstek Set Charge Power"
        slave: 1
        address: 42020
        data_type: uint16
        min_value: 0
        max_value: 2500
        step: 50
        unit_of_measurement: "W"
        scan_interval: 10

      - name: "Marstek Set Discharge Power"
        slave: 1
        address: 42021
        data_type: uint16
        min_value: 0
        max_value: 2500
        step: 50
        unit_of_measurement: "W"
        scan_interval: 10

      - name: "Marstek Charge to SOC"
        slave: 1
        address: 42011
        data_type: uint16
        min_value: 10
        max_value: 100
        step: 1
        unit_of_measurement: "%"
        scan_interval: 10

      - name: "Marstek Max Charge Power"
        slave: 1
        address: 44002
        data_type: uint16
        min_value: 0
        max_value: 2500
        step: 50
        unit_of_measurement: "W"
        scan_interval: 60

      - name: "Marstek Max Discharge Power"
        slave: 1
        address: 44003
        data_type: uint16
        min_value: 0
        max_value: 2500
        step: 50
        unit_of_measurement: "W"
        scan_interval: 60
```

---

## 7. Modbus TCP Adapter Configuration (for non-V3 models)

### RS485-to-TCP adapters that work with Marstek:
- Elfin EW11 / EW11B (commonly used, proven)
- PUSR DR134
- Waveshare RS485-to-WiFi/ETH (SKU:21968)
- M5Stack with RS485 base

### Adapter TCP Server Settings:
| Parameter | Value |
|-----------|-------|
| Protocol | TCP Server |
| Local Port | 502 |
| Buffer Size | 512 bytes |
| Keep Alive | 60 seconds |
| Timeout | 300 seconds |
| Max Connections | 3 |
| Mode | Modbus TCP to RTU (transparent bridge) |

---

## 8. Known Issues and Notes

1. **Single connection limit**: Only one Modbus TCP connection is allowed simultaneously on port 502. If another client (e.g., the Marstek app) is connected, your integration will fail.

2. **RS485 control mode prerequisite**: Registers 42010-42021 (force charge/discharge) only work after writing 21930 (0x55AA) to register 42000 to enable RS485 control mode.

3. **V3 register differences**: Venus E/D V3 models have significantly different register addresses for many parameters. Using V1/V2 addresses on V3 hardware (or vice versa) will produce incorrect or no data.

4. **Fault register 44001 on V3**: Register 44001 (discharging cutoff capacity) returns "Modbus exception 2: Illegal data address" on some V3 firmware.

5. **V3 native Ethernet**: The Venus V3 has a built-in RJ45 port. After connecting to Ethernet and enabling Modbus in the app, port 502 is directly accessible without any RS485 adapter.

6. **Firmware requirement**: Modbus functionality requires firmware V139 or higher. Older firmware may not expose the Modbus interface.

7. **Work Mode "Trade Mode" display**: The "User Work Mode (Trade Mode/AI Optimized)" setting may not accurately reflect in Home Assistant when changed via the Marstek app due to a known firmware quirk.

---

## 9. Sources

- GitHub: ViperRNMC/marstek_venus_modbus (HACS integration, source of register map) - https://github.com/ViperRNMC/marstek_venus_modbus
- GitHub: Superduper1969/MarstekVenus-ElfinEW11 - https://github.com/Superduper1969/MarstekVenus-ElfinEW11
- GitHub: fonske/MarstekVenusV3-modbus-TCP-IP - https://github.com/fonske/MarstekVenusV3-modbus-TCP-IP
- GitHub: reschcloud/marstek_venus_e_modbus_home_assistant - https://github.com/reschcloud/marstek_venus_e_modbus_home_assistant
- GitHub: WargamingPlayer/HA-Marstek-Venus-E-Modbus - https://github.com/WargamingPlayer/HA-Marstek-Venus-E-Modbus
- GitHub: gf78/marstek-venus-modbus-restapi-mqtt-nodered-homeassistant - https://github.com/gf78/marstek-venus-modbus-restapi-mqtt-nodered-homeassistant
- evcc discussion #21037 (Marstek Venus Battery) - https://github.com/evcc-io/evcc/discussions/21037
- evcc discussion #24648 (V3 register changes) - https://github.com/evcc-io/evcc/discussions/24648
- evcc issue #25373 (Enable Modbus TCP/IP) - https://github.com/evcc-io/evcc/issues/25373
- du.nkel.dev blog (Venus E HA integration) - https://du.nkel.dev/blog/2026-01-11_marstek-battery-homeassistant/
- forwardme.de (Venus modbus openHAB) - https://www.forwardme.de/2025/04/27/marstek-venus-speicher-modbus-tcp-openhab-anbindung/
- GitHub Gist (Schedule registers) - https://gist.github.com/schauveau/30a29ec0daa50e0f1cb6d5700c068d4b
