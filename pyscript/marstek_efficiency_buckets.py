"""
Marstek Venus A efficiency buckets for Home Assistant Pyscript.

This script:
- samples every 30 seconds
- uses grid power to assign a charge/discharge bucket in 100 W steps
- compares per-interval grid energy against per-interval battery counter delta
- persists per-bucket totals and publishes efficiency states in Home Assistant

Default bucket range: 5 W .. 1200 W
Published entities live under the `pyscript.` domain.
"""

import time


GRID_POWER_ENTITY = "sensor.marstek_grid_power"
TOTAL_CHARGED_ENTITY = "sensor.marstek_total_energy_charged"
TOTAL_DISCHARGED_ENTITY = "sensor.marstek_total_energy_discharged"

SAMPLE_SECONDS = 30
BUCKET_SIZE_W = 100
MAX_BUCKET_W = 1200
MIN_ACTIVE_POWER_W = 5
MIN_INTERVAL_ENERGY_KWH = 0.0001
MAX_SAMPLE_GAP_SECONDS = 180
MAX_REASONABLE_EFFICIENCY = 1.05

PERSIST_ENTITIES = {
    "prev_ts": 0.0,
    "prev_grid_power_w": 0.0,
    "prev_total_charged_kwh": 0.0,
    "prev_total_discharged_kwh": 0.0,
}


def _state_id(name):
    return f"pyscript.marstek_efficiency_{name}"


def _bucket_label(bucket_w):
    if bucket_w == MAX_BUCKET_W:
        return f"{bucket_w:04d}w"
    return f"{bucket_w:04d}_{bucket_w + BUCKET_SIZE_W - 1:04d}w"


def _bucket_ids(bucket_w, direction):
    label = _bucket_label(bucket_w)
    prefix = f"marstek_efficiency_{direction}_{label}"
    return {
        "input": f"pyscript.{prefix}_input_kwh",
        "output": f"pyscript.{prefix}_output_kwh",
        "efficiency": f"pyscript.{prefix}_pct",
        "samples": f"pyscript.{prefix}_samples",
    }


def _safe_float(entity_id):
    value = state.get(entity_id)
    if value in [None, "unknown", "unavailable", "none", ""]:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _persist_defaults():
    for name, default in PERSIST_ENTITIES.items():
        state.persist(_state_id(name), default_value=default)

    for bucket_w in range(0, MAX_BUCKET_W + BUCKET_SIZE_W, BUCKET_SIZE_W):
        for direction in ("charge", "discharge"):
            ids = _bucket_ids(bucket_w, direction)
            attrs = {
                "friendly_name": f"Marstek {direction.title()} {bucket_w} W bucket efficiency",
                "bucket_lower_w": bucket_w,
                "bucket_upper_w": bucket_w if bucket_w == MAX_BUCKET_W else bucket_w + BUCKET_SIZE_W - 1,
                "bucket_size_w": BUCKET_SIZE_W,
                "direction": direction,
                "unit_of_measurement": "%",
            }
            state.persist(ids["input"], default_value=0.0)
            state.persist(ids["output"], default_value=0.0)
            state.persist(ids["samples"], default_value=0)
            state.persist(ids["efficiency"], default_value=0.0, default_attributes=attrs)


def _read_persisted(name, cast=float):
    value = state.get(_state_id(name))
    if value in [None, "unknown", "unavailable", ""]:
        return cast(PERSIST_ENTITIES[name])
    return cast(value)


def _write_persisted(name, value):
    state.set(_state_id(name), value=value)


def _classify_power(power_w):
    abs_power = abs(power_w)
    if abs_power < MIN_ACTIVE_POWER_W:
        return None, None

    bucket_w = int(abs_power // BUCKET_SIZE_W) * BUCKET_SIZE_W
    if bucket_w > MAX_BUCKET_W:
        return None, None

    direction = "charge" if power_w < 0 else "discharge"
    return direction, bucket_w


def _update_bucket_states(direction, bucket_w, input_add_kwh, output_add_kwh):
    ids = _bucket_ids(bucket_w, direction)
    current_input = _safe_float(ids["input"]) or 0.0
    current_output = _safe_float(ids["output"]) or 0.0
    current_samples = int((_safe_float(ids["samples"]) or 0))

    new_input = current_input + input_add_kwh
    new_output = current_output + output_add_kwh
    new_samples = current_samples + 1

    efficiency = 0.0
    if new_input > 0:
        efficiency = round((new_output / new_input) * 100, 2)

    state.set(ids["input"], value=round(new_input, 5))
    state.set(ids["output"], value=round(new_output, 5))
    state.set(ids["samples"], value=new_samples)
    state.set(
        ids["efficiency"],
        value=efficiency,
        new_attributes={
            "friendly_name": f"Marstek {direction.title()} {bucket_w} W bucket efficiency",
            "bucket_lower_w": bucket_w,
            "bucket_upper_w": bucket_w if bucket_w == MAX_BUCKET_W else bucket_w + BUCKET_SIZE_W - 1,
            "bucket_size_w": BUCKET_SIZE_W,
            "direction": direction,
            "input_kwh": round(new_input, 5),
            "output_kwh": round(new_output, 5),
            "samples": new_samples,
            "unit_of_measurement": "%",
        },
    )


def _process_interval(current_ts, current_power_w, current_charged_kwh, current_discharged_kwh):
    prev_ts = _read_persisted("prev_ts")
    prev_power_w = _read_persisted("prev_grid_power_w")
    prev_charged_kwh = _read_persisted("prev_total_charged_kwh")
    prev_discharged_kwh = _read_persisted("prev_total_discharged_kwh")

    if prev_ts <= 0:
        return

    dt_seconds = current_ts - prev_ts
    if dt_seconds <= 0 or dt_seconds > MAX_SAMPLE_GAP_SECONDS:
        return

    direction, bucket_w = _classify_power(prev_power_w)
    if direction is None:
        return

    grid_energy_kwh = abs(prev_power_w) * (dt_seconds / 3600.0) / 1000.0

    if direction == "charge":
        input_kwh = grid_energy_kwh
        output_kwh = max(0.0, current_charged_kwh - prev_charged_kwh)
    else:
        input_kwh = max(0.0, current_discharged_kwh - prev_discharged_kwh)
        output_kwh = grid_energy_kwh

    if input_kwh < MIN_INTERVAL_ENERGY_KWH or output_kwh <= 0:
        return

    efficiency = output_kwh / input_kwh
    if efficiency <= 0 or efficiency > MAX_REASONABLE_EFFICIENCY:
        return

    _update_bucket_states(direction, bucket_w, input_kwh, output_kwh)


@time_trigger("startup")
def marstek_efficiency_buckets_init():
    _persist_defaults()


@time_trigger(f"period(now, {SAMPLE_SECONDS}s)")
def marstek_efficiency_buckets_sample():
    current_power_w = _safe_float(GRID_POWER_ENTITY)
    current_charged_kwh = _safe_float(TOTAL_CHARGED_ENTITY)
    current_discharged_kwh = _safe_float(TOTAL_DISCHARGED_ENTITY)

    if current_power_w is None or current_charged_kwh is None or current_discharged_kwh is None:
        return

    current_ts = time.time()
    _process_interval(current_ts, current_power_w, current_charged_kwh, current_discharged_kwh)

    _write_persisted("prev_ts", current_ts)
    _write_persisted("prev_grid_power_w", current_power_w)
    _write_persisted("prev_total_charged_kwh", current_charged_kwh)
    _write_persisted("prev_total_discharged_kwh", current_discharged_kwh)


@service
def marstek_efficiency_reset():
    """Reset all bucket totals."""

    for bucket_w in range(0, MAX_BUCKET_W + BUCKET_SIZE_W, BUCKET_SIZE_W):
        for direction in ("charge", "discharge"):
            ids = _bucket_ids(bucket_w, direction)
            state.set(ids["input"], value=0.0)
            state.set(ids["output"], value=0.0)
            state.set(ids["samples"], value=0)
            state.set(
                ids["efficiency"],
                value=0.0,
                new_attributes={
                    "friendly_name": f"Marstek {direction.title()} {bucket_w} W bucket efficiency",
                    "bucket_lower_w": bucket_w,
                    "bucket_upper_w": bucket_w if bucket_w == MAX_BUCKET_W else bucket_w + BUCKET_SIZE_W - 1,
                    "bucket_size_w": BUCKET_SIZE_W,
                    "direction": direction,
                    "input_kwh": 0.0,
                    "output_kwh": 0.0,
                    "samples": 0,
                    "unit_of_measurement": "%",
                },
            )

    _write_persisted("prev_ts", 0.0)
    _write_persisted("prev_grid_power_w", 0.0)
    _write_persisted("prev_total_charged_kwh", 0.0)
    _write_persisted("prev_total_discharged_kwh", 0.0)
