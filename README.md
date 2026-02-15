# Marstek Venus A — Home Assistant Modbus TCP Integration

Full Home Assistant integration for the Marstek Venus A home battery via Modbus TCP.
Firmware >= 147 | Hardware: V1/V2 (RS485 adapter required) | Protocol: Modbus RTU-over-TCP

---

## Table of Contents

1. [File Overview](#file-overview)
2. [Hardware Requirements & Wiring](#hardware-requirements--wiring)
3. [Installation in Home Assistant](#installation-in-home-assistant)
4. [Register Reference — all registers explained](#register-reference--all-registers-explained)
5. [Control: how does it work?](#control-how-does-it-work)
6. [Automations explained](#automations-explained)
7. [FAQ & Troubleshooting](#faq--troubleshooting)

---

## File Overview

| File | Contents |
|------|----------|
| `marstek_venus_a.yaml` | Main package: modbus hub, sensors, switches, numbers, template sensors, input helpers, scripts |
| `marstek_automations.yaml` | Automations for charge/discharge by time, price, SOC, zero-grid |
| `README.md` | This file |

---

## Hardware Requirements & Wiring

### Venus A hardware

The Marstek Venus A is V1/V2 hardware with **no** built-in Ethernet port.
Communication uses **RS485** → you need an RS485-to-Ethernet adapter.

### Compatible adapters

| Adapter | Notes |
|---------|-------|
| Elfin EW11 | Popular, well documented for Marstek |
| PUSR DR134 | DIN-rail mount |
| Waveshare RS485-to-ETH | Budget option |
| USR-TCP232-304 | Alternative |

### RS485 Wiring

Marstek connector (4-pin or 5-pin variant):

```
Pin 1 → A (+)  yellow/green  → A-terminal on adapter
Pin 2 → B (-)  red           → B-terminal on adapter
Pin 3 → GND    black         → GND-terminal on adapter
Pin 5 → VCC    black         → (optional, to power adapter)
```

### Adapter serial settings

```
Baud rate: 115200
Data bits: 8
Parity:    None (N)
Stop bits: 1
Mode:      TCP Server or Modbus TCP Gateway
TCP Port:  502
```

### Limitation

> **Only one simultaneous Modbus TCP connection is allowed.**
> If Home Assistant is connected, other tools (Modbus Poll, evcc, etc.) cannot connect at the same time.

---

## Installation in Home Assistant

### If you already have `modbus: !include modbus.yaml`

If your `configuration.yaml` already contains `modbus: !include modbus.yaml`, you **cannot** add another `modbus:` key in a package — HA will reject the duplicate key.

**Solution: split the files.**

**Step 1** — Copy the entire `modbus:` block from `marstek_venus_a.yaml` (starting with `- name: marstek_venus`) and append it to your existing `modbus.yaml`:

```yaml
# modbus.yaml  (your existing file, append this at the bottom)

  - name: marstek_venus
    type: tcp
    host: !secret marstek_host
    port: 502
    timeout: 5
    message_wait_milliseconds: 50
    sensors:
      # ... (copy the full sensors/switches/numbers sections from marstek_venus_a.yaml)
```

**Step 2** — Remove the `modbus:` top-level key from `marstek_venus_a.yaml` (keep template, input_select, input_number, script).

**Step 3** — Load the remaining package from `configuration.yaml`:

```yaml
homeassistant:
  packages:
    marstek: !include packages/marstek_venus_a.yaml
```

Your `modbus.yaml` now contains all hubs (existing + Marstek) and the package contains everything else.

---

### Fresh install (no existing modbus config)

**Step 1: Add secret**

Add to `config/secrets.yaml`:
```yaml
marstek_host: "192.168.1.xxx"   # IP address of your RS485 adapter
```

**Step 2: Enable packages**

Add to `config/configuration.yaml`:
```yaml
homeassistant:
  packages:
    marstek: !include packages/marstek_venus_a.yaml
```

**Step 3: Place files**

```
config/
├── configuration.yaml
├── secrets.yaml
└── packages/
    ├── marstek_venus_a.yaml
    └── marstek_automations.yaml
```

Import `marstek_automations.yaml` as standalone automations or add to the package.
For package use, add to `marstek_venus_a.yaml`:
```yaml
automation: !include marstek_automations.yaml
```

**Step 4: Add input booleans** (required for automations 6 and 11)

Add to `marstek_venus_a.yaml` or a separate file:
```yaml
input_boolean:
  marstek_anti_feedin_enabled:
    name: "Marstek Anti Feed-In Enable"
    icon: mdi:transmission-tower-off

  marstek_zero_grid_enabled:
    name: "Marstek Zero-Grid Control"
    icon: mdi:home-lightning-bolt
```

**Step 5: Restart Home Assistant**

After restart all entities appear under the `marstek_venus` hub.

---

## Register Reference — all registers explained

### Convention

All registers are read via **Function Code 03** (Read Holding Registers).
Writing uses **FC06** (Write Single Register).

| Parameter | Value |
|-----------|-------|
| Slave ID / Unit ID | 1 |
| Byte order | Big-endian |
| Addressing | Absolute (use address exactly as shown in table) |

---

### Battery measurements (read-only)

| Register | Name | Type | Scale | Unit | Description |
|----------|------|------|-------|------|-------------|
| 32100 | Battery Voltage | uint16 | × 0.01 | V | DC voltage of the battery |
| 32101 | Battery Current | int16 | × 0.01 | A | + = charging, − = discharging |
| 32102–32103 | Battery Power | int32 | × 1 | W | DC power; + = charging, − = discharging |
| 32104 | State of Charge (SOC) | uint16 | × 1 | % | Battery charge level (0–100%) |
| 32105 | Nameplate Capacity | uint16 | × 0.001 | kWh | Nominal battery capacity |

---

### AC Grid measurements (read-only)

| Register | Name | Type | Scale | Unit | Description |
|----------|------|------|-------|------|-------------|
| 32200 | Grid Voltage | uint16 | × 0.1 | V | AC voltage on grid side |
| 32201 | Grid Current | int16 | × 0.01 | A | + = export to grid, − = import from grid |
| 32202–32203 | Grid Power | int32 | × 1 | W | + = export (discharging), − = import (charging) |
| 32204 | Grid Frequency | int16 | × 0.01 | Hz | Grid frequency (e.g. 50.00 Hz) |

---

### Off-grid output (read-only)

| Register | Name | Type | Scale | Unit | Description |
|----------|------|------|-------|------|-------------|
| 32300 | Off-Grid Voltage | uint16 | × 0.1 | V | Voltage on the off-grid output |
| 32301 | Off-Grid Current | uint16 | × 0.01 | A | Current to off-grid load |
| 32302–32303 | Off-Grid Power | int32 | × 1 | W | Power on off-grid output |

---

### Energy counters (cumulative, read-only)

| Register | Name | Type | Scale | Unit | Description |
|----------|------|------|-------|------|-------------|
| 33000–33001 | Total Energy Charged | uint32 | × 0.01 | kWh | Total energy ever charged |
| 33002–33003 | Total Energy Discharged | int32 | × 0.01 | kWh | Total energy ever discharged |
| 33004–33005 | Daily Energy Charged | uint32 | × 0.01 | kWh | Energy charged today |
| 33006–33007 | Daily Energy Discharged | int32 | × 0.01 | kWh | Energy discharged today |
| 33008–33009 | Monthly Energy Charged | uint32 | × 0.01 | kWh | Energy charged this month |
| 33010–33011 | Monthly Energy Discharged | int32 | × 0.01 | kWh | Energy discharged this month |

---

### Temperatures (read-only)

| Register | Name | Type | Scale | Unit | Description |
|----------|------|------|-------|------|-------------|
| 35000 | Battery Temperature | int16 | × 0.1 | °C | Internal battery temperature |
| 35001 | MOS1 Temperature | int16 | × 0.1 | °C | MOS transistor 1 temperature |
| 35002 | MOS2 Temperature | int16 | × 0.1 | °C | MOS transistor 2 temperature |
| 35010 | Max Cell Temperature | int16 | × 1 | °C | Highest cell temperature in battery pack |
| 35011 | Min Cell Temperature | int16 | × 1 | °C | Lowest cell temperature in battery pack |
| 35111 | BMS Max Charge Current | uint16 | × 0.1 | A | Maximum charge current allowed by BMS |
| 35112 | BMS Max Discharge Current | uint16 | × 0.1 | A | Maximum discharge current allowed by BMS |

---

### Cell voltages (read-only)

| Register | Name | Type | Scale | Unit | Description |
|----------|------|------|-------|------|-------------|
| 34018 | Cell 1 Voltage | int16 | × 0.001 | V | Voltage of cell 1 (e.g. 3.280 V) |
| 34019 | Cell 2 Voltage | int16 | × 0.001 | V | Voltage of cell 2 |
| 34020 | Cell 3 Voltage | int16 | × 0.001 | V | Voltage of cell 3 |
| 34021 | Cell 4 Voltage | int16 | × 0.001 | V | Voltage of cell 4 |
| 34022 | Cell 5 Voltage | int16 | × 0.001 | V | Voltage of cell 5 |
| 34023 | Cell 6 Voltage | int16 | × 0.001 | V | Voltage of cell 6 |
| 34024 | Cell 7 Voltage | int16 | × 0.001 | V | Voltage of cell 7 |
| 34025 | Cell 8 Voltage | int16 | × 0.001 | V | Voltage of cell 8 |
| 34026 | Cell 9 Voltage | int16 | × 0.001 | V | Voltage of cell 9 |
| 34027 | Cell 10 Voltage | int16 | × 0.001 | V | Voltage of cell 10 |
| 34028 | Cell 11 Voltage | int16 | × 0.001 | V | Voltage of cell 11 |
| 34029 | Cell 12 Voltage | int16 | × 0.001 | V | Voltage of cell 12 |
| 34030 | Cell 13 Voltage | int16 | × 0.001 | V | Voltage of cell 13 |
| 34031 | Cell 14 Voltage | int16 | × 0.001 | V | Voltage of cell 14 |
| 34032 | Cell 15 Voltage | int16 | × 0.001 | V | Voltage of cell 15 |
| 34033 | Cell 16 Voltage | int16 | × 0.001 | V | Voltage of cell 16 |

> Cell voltage difference > 50 mV may indicate cell imbalance. Typical LiFePO4 range: 3.1–3.6 V.

---

### Status & Alarm registers (read-only)

#### Inverter state (register 35100)

| Value | Status | Description |
|-------|--------|-------------|
| 0 | Sleep | Inverter inactive |
| 1 | Standby | Ready but not active |
| 2 | Charging | Battery is being charged |
| 3 | Discharging | Battery is supplying power |
| 4 | Backup Mode | Off-grid emergency power active |
| 5 | OTA Upgrade | Firmware update in progress |
| 6 | Bypass | Grid passthrough (no conversion) |

#### Alarm register (36000) — bitmask

| Bit | Value | Alarm |
|-----|-------|-------|
| 0 | 1 | PLL Restart |
| 1 | 2 | Overheating |
| 2 | 4 | Low Temperature |
| 3 | 8 | Fan Fault |
| 4 | 16 | Low SOC |
| 5 | 32 | Output Overcurrent |
| 6 | 64 | Line Sequence Fault |
| 7 | 128 | WiFi Abnormal |
| 8 | 256 | BLE Abnormal |
| 9 | 512 | Network Abnormal |
| 10 | 1024 | CT Connection Abnormal |

Example: value `20` = bit 2 (4) + bit 4 (16) = Low Temperature + Low SOC.

#### Fault registers (36100–36103) — bitmasks

**Register 36100:**

| Bit | Fault |
|-----|-------|
| 0 | Grid Overvoltage |
| 1 | Grid Undervoltage |
| 2 | Grid Overfrequency |
| 3 | Grid Underfrequency |
| 4 | Battery Overvoltage |
| 5 | Battery Undervoltage |
| 6 | Battery Overcurrent |
| 7 | Battery Low SOC |

**Register 36101:**

| Bit | Fault |
|-----|-------|
| 0 | Battery Communication Fault |
| 1 | BMS Fault |
| 2 | Inverter Hardware Fault |
| 3 | Hardware Protection Active |
| 4 | Overload |
| 5 | Overtemperature |
| 6–15 | Reserved |

---

### Firmware versions (read-only)

| Register | Name | Type | Scale | Description |
|----------|------|------|-------|-------------|
| 31100 | Software Version | uint16 | × 0.01 | EMS firmware version (e.g. 147 → 1.47) |
| 31101 | EMS Version | uint16 | × 1 | EMS module version |
| 31102 | BMS Version | uint16 | × 1 | BMS module version |
| 31200–31204 | Serial Number | char[10] | — | Device serial number |

---

### Control registers (read + write)

> **Order matters!** Enable RS485 control (42000) first, then write setpoints.

#### RS485 Control Mode (register 42000)

| Write value | Hex | Description |
|-------------|-----|-------------|
| 21930 | 0x55AA | RS485 control ENABLE (required for force charge/discharge) |
| 21947 | 0x55BB | RS485 control DISABLE (return to automatic) |

#### Force charge/discharge (registers 42010, 42020, 42021)

> RS485 control (42000 = 21930) **must be active** before these registers take effect.

| Register | Name | Type | Values | Description |
|----------|------|------|--------|-------------|
| 42010 | Force Mode | uint16 | 0=Stop, 1=Charge, 2=Discharge | Select the force mode |
| 42011 | Charge Target SOC | uint16 | 10–100 | Stop force charging when this SOC% is reached |
| 42020 | Charge Power | uint16 | 0–2500 | Forced charge power in Watts |
| 42021 | Discharge Power | uint16 | 0–2500 | Forced discharge power in Watts |

**Example sequence — force charge at 1500W to 80%:**
```
1. Write 21930 to register 42000   (enable RS485)
2. Write 80    to register 42011   (target SOC 80%)
3. Write 1500  to register 42020   (charge power 1500W)
4. Write 1     to register 42010   (start charging)
```

**To stop:**
```
1. Write 0     to register 42010   (stop)
2. Write 21947 to register 42000   (disable RS485, optional)
```

#### Work Mode (register 43000)

| Value | Mode | Description |
|-------|------|-------------|
| 0 | Manual | Full manual control via RS485 |
| 1 | Anti Feed-In | Prevents exporting to the grid |
| 2 | Trade Mode | Optimise based on energy tariffs (cloud/schedule) |

#### Backup function (register 41200)

| Value | Status | Description |
|-------|--------|-------------|
| 0 | ON | Backup/emergency power output active |
| 1 | OFF | Backup output disabled |

> Note: inverted logic — 0 = on, 1 = off!

#### Permanent power limits (registers 44002, 44003)

| Register | Name | Type | Range | Unit | Description |
|----------|------|------|-------|------|-------------|
| 44002 | Max Charge Power | uint16 | 0–2500 | W | Absolute maximum charge power |
| 44003 | Max Discharge Power | uint16 | 0–2500 | W | Absolute maximum discharge power |

#### SOC cutoff limits (registers 44000, 44001)

| Register | Name | Type | Range | Scale | Unit | Description |
|----------|------|------|-------|-------|------|-------------|
| 44000 | Charge Cutoff SOC | uint16 | 800–1000 | ÷ 10 | % | Stop charging at this SOC (800=80%, 1000=100%) |
| 44001 | Discharge Cutoff SOC | uint16 | 120–300 | ÷ 10 | % | Stop discharging at this SOC (120=12%, 300=30%) |

> **Note the scale factor:** register value 900 = 90%. Write `900` to register 44000 for 90% charge cutoff.

#### Grid standard (register 44100)

| Value | Standard |
|-------|----------|
| 0 | Auto detect |
| 1 | EN50549 (Europe) |
| 2 | NL (Netherlands) |
| 3 | DE (Germany) |
| 4 | AT (Austria) |
| 5 | UK (United Kingdom) |
| 6 | ES (Spain) |
| 7 | PL (Poland) |
| 8 | IT (Italy) |
| 9 | CN (China) |

---

## Control: how does it work?

### Architecture

```
Home Assistant
    │
    │ Modbus TCP (port 502)
    ▼
RS485-to-Ethernet Adapter
    │
    │ RS485 (115200 baud, 8N1)
    ▼
Marstek Venus A
```

### Required control sequence

The Marstek requires a strict order for forced control:

```
[1] Activate RS485 control
    Register 42000 ← 21930 (0x55AA)

[2] Set target values
    Register 42011 ← target SOC (optional)
    Register 42020 ← charge power (Watts)
    Register 42021 ← discharge power (Watts)

[3] Start the desired mode
    Register 42010 ← 1 (charge) or 2 (discharge) or 0 (stop)

[4] To stop
    Register 42010 ← 0
    Register 42000 ← 21947 (0x55BB)  [recommended]
```

### Using scripts (recommended)

The included scripts handle the sequence automatically:

**Via Developer Tools → Actions:**
```yaml
action: script.marstek_force_charge
data:
  power: 1500       # Watts
  target_soc: 80    # %
```

```yaml
action: script.marstek_force_discharge
data:
  power: 1000       # Watts
```

```yaml
action: script.marstek_stop_forcing
```

### Direct Modbus write actions

You can also write registers directly via Developer Tools → Actions:

```yaml
action: modbus.write_register
data:
  hub: marstek_venus
  slave: 1
  address: 42000
  value: 21930
```

### Set work mode

```yaml
action: modbus.write_register
data:
  hub: marstek_venus
  slave: 1
  address: 43000
  value: 1     # 0=Manual, 1=Anti Feed-In, 2=Trade Mode
```

---

## Automations explained

### 1. Sync Work Mode
Links `input_select.marstek_work_mode` UI dropdown to register 43000.
Change the dropdown → register is automatically updated.

### 2. Sync Force Mode
Links `input_select.marstek_force_mode` to the corresponding scripts.
Use the dropdown as the primary control for force charge/discharge.

### 3. Night Tariff Charging (23:00–07:00)
- Activated at 23:00 if SOC < 90%
- Charges at 2000W to 95% SOC
- Stops automatically at 07:00
- **Adjust:** times and SOC threshold to your tariff

### 4. Peak Price Discharging (17:00–21:00)
- Forces discharging during the most expensive hours
- Condition: SOC > 30%
- **Adjust:** times and power to your situation

### 5. SOC Protection — stop at low/high SOC
- Automatically stops force discharging when SOC < 15%
- Automatically stops force charging when SOC > 98%
- Failsafe on top of built-in BMS protection

### 6. Anti Feed-In
- Toggled via `input_boolean.marstek_anti_feedin_enabled`
- Active from 08:00 to 20:00 (adjustable)
- Writes work mode 1 to register 43000

### 7. Backup Power Reserve
- Warning notification when SOC < 20% + discharging
- Manual decision whether backup mode is needed

### 8. Safety Sync on HA Restart
- Waits 30 seconds after restart
- Reads actual state from Marstek
- Syncs UI helpers (input_select) with actual status

### 9. Alarm Notification
- `persistent_notification` when alarms are active (register 36000 > 0)
- Notification is automatically dismissed when alarm is resolved

### 10. Dynamic Energy Pricing (Nordpool/Tibber)
- Charge when price < €0.10/kWh
- Discharge when price > €0.30/kWh
- Stops automatically at neutral price
- **Adjust:** `entity_id` to your price sensor + threshold values

### 11. Zero-Grid Control
- Runs every 10 seconds when `input_boolean.marstek_zero_grid_enabled` is on
- Reads `sensor.marstek_grid_power` (requires CT clamp)
- Calculates the required charge/discharge correction: `new_setpoint = current_battery_power + grid_power`
- Positive new setpoint → force charge at that power
- Negative new setpoint → force discharge at that power
- Does nothing if grid power is within ±50W deadband
- Respects SOC limits (soc_min 10%, soc_max 98%)
- **Tune:** `deadband`, `max_power`, `soc_min`, `soc_max` variables in the automation

---

## FAQ & Troubleshooting

### Modbus connection not working

1. Check IP address in `secrets.yaml`
2. Verify the RS485 adapter is listening on port 502
3. Check RS485 wiring (swap A/B if no connection)
4. Ensure no other tool is connected at the same time (only 1 allowed!)
5. Increase `timeout` to `10` in the modbus hub config

### Sensors show "unavailable"

- Increase `message_wait_milliseconds` to 80ms if some sensors drop out
- Check `scan_interval`: too short intervals can overload the connection
- Check Modbus logs via HA Logger

### Force charge/discharge not working

- Check that `switch.marstek_rs485_control` is **on** (value 21930)
- RS485 control MUST be active BEFORE writing to 42010/42020/42021
- Use the provided scripts — they handle the sequence correctly

### Wrong values (too high/low)

- Check the scale factor in the register table
- For `int32`/`uint32` registers: HA reads 2 registers automatically
- Verify `data_type` is correct (signed int16 vs unsigned uint16)

### SOC cutoff registers (44000/44001) behave unexpectedly

- Register value is in tenths of percent: value 900 = 90%
- Always write the tenfold value: 80% → write 800

### HA shows "modbus.write_register" error

- Check `hub` name: must be exactly `marstek_venus` (or adjust)
- `slave` parameter is required: `slave: 1`
- `address` is the direct register value (e.g. `42000`)

### I already have `modbus: !include modbus.yaml`

See the [Installation section](#if-you-already-have-modbus-include-modbusyaml) above.
In short: copy the Marstek hub block into your existing `modbus.yaml` and remove the `modbus:` key from `marstek_venus_a.yaml`.

### Zero-grid control is unstable / oscillates

- Increase the `deadband` variable (default 50W → try 100W or 150W)
- Check that `sensor.marstek_grid_power` reflects your actual grid import/export correctly (CT clamp orientation matters)
- Reduce the update frequency by changing `seconds: "/10"` to `seconds: "/30"`

### How do I debug Modbus communication?

Add to `configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    homeassistant.components.modbus: debug
```

View logs via HA → Settings → System → Logs

---

## References

- [ViperRNMC/marstek_venus_modbus](https://github.com/ViperRNMC/marstek_venus_modbus) — HACS integration (alternative to YAML approach)
- [Superduper1969/MarstekVenus-ElfinEW11](https://github.com/Superduper1969/MarstekVenus-ElfinEW11) — YAML for Elfin EW11
- [fonske/MarstekVenusV3-modbus-TCP-IP](https://github.com/fonske/MarstekVenusV3-modbus-TCP-IP) — V3 direct Ethernet config
- [du.nkel.dev blog](https://du.nkel.dev/blog/2026-01-11_marstek-battery-homeassistant/) — Venus E HA integration
- [HA Modbus documentation](https://www.home-assistant.io/integrations/modbus/)
