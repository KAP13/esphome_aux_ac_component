import logging
import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.components import climate, uart, sensor, binary_sensor
from esphome.const import (
    CONF_ID,
    CONF_UART_ID,
    CONF_PERIOD,
    CONF_CUSTOM_FAN_MODES,
    CONF_CUSTOM_PRESETS,
    CONF_INTERNAL,
    UNIT_CELSIUS,
    UNIT_PERCENT,
    ICON_THERMOMETER,
    ICON_POWER,
    DEVICE_CLASS_TEMPERATURE,
    STATE_CLASS_MEASUREMENT,
    DEVICE_CLASS_HEAT,
    DEVICE_CLASS_POWER,
)
from esphome.components.climate import (
    ClimateMode,
    ClimatePreset,
    ClimateSwingMode,
)
_LOGGER = logging.getLogger(__name__)

CODEOWNERS = ["@GrKoR"]
DEPENDENCIES = ["climate", "uart"]
AUTO_LOAD = ["sensor", "binary_sensor"]

CONF_SUPPORTED_MODES = 'supported_modes'
CONF_SUPPORTED_SWING_MODES = 'supported_swing_modes'
CONF_SUPPORTED_PRESETS = 'supported_presets'
CONF_SHOW_ACTION = 'show_action'
CONF_INDOOR_TEMPERATURE = 'indoor_temperature'
CONF_OUTDOOR_TEMPERATURE = 'outdoor_temperature'
CONF_DEFROST_SENSOR = 'defrost_sensor'
CONF_INVERTOR_POWER = 'invertor_power'

aux_ac_ns = cg.esphome_ns.namespace("aux_ac")
AirCon = aux_ac_ns.class_("AirCon", climate.Climate, cg.Component)
Capabilities = aux_ac_ns.namespace("Constants")

ALLOWED_CLIMATE_MODES = {
    "HEAT_COOL": ClimateMode.CLIMATE_MODE_HEAT_COOL,
    "COOL": ClimateMode.CLIMATE_MODE_COOL,
    "HEAT": ClimateMode.CLIMATE_MODE_HEAT,
    "DRY": ClimateMode.CLIMATE_MODE_DRY,
    "FAN_ONLY": ClimateMode.CLIMATE_MODE_FAN_ONLY,
}
validate_modes = cv.enum(ALLOWED_CLIMATE_MODES, upper=True)

ALLOWED_CLIMATE_PRESETS = {
    "SLEEP": ClimatePreset.CLIMATE_PRESET_SLEEP,
}
validate_presets = cv.enum(ALLOWED_CLIMATE_PRESETS, upper=True)

ALLOWED_CLIMATE_SWING_MODES = {
    "BOTH": ClimateSwingMode.CLIMATE_SWING_BOTH,
    "VERTICAL": ClimateSwingMode.CLIMATE_SWING_VERTICAL,
    "HORIZONTAL": ClimateSwingMode.CLIMATE_SWING_HORIZONTAL,
}
validate_swing_modes = cv.enum(ALLOWED_CLIMATE_SWING_MODES, upper=True)

CUSTOM_FAN_MODES = {
    "MUTE": Capabilities.MUTE,
    "TURBO": Capabilities.TURBO,
}
validate_custom_fan_modes = cv.enum(CUSTOM_FAN_MODES, upper=True)

CUSTOM_PRESETS = {
    "CLEAN": Capabilities.CLEAN,
    "FEEL": Capabilities.FEEL,
    "HEALTH": Capabilities.HEALTH,
    "ANTIFUNGUS": Capabilities.ANTIFUNGUS,
}
validate_custom_presets = cv.enum(CUSTOM_PRESETS, upper=True)

def output_info(config):
    """_LOGGER.info(config)"""
    return config

CONFIG_SCHEMA = cv.All(
    climate.CLIMATE_SCHEMA.extend(
        {
            cv.GenerateID(): cv.declare_id(AirCon),
            cv.Optional(CONF_PERIOD, default="7s"): cv.time_period,
            cv.Optional(CONF_SHOW_ACTION, default="true"): cv.boolean,
            cv.Optional(CONF_DEFROST_SENSOR): binary_sensor.BINARY_SENSOR_SCHEMA,
            cv.Optional(CONF_INVERTOR_POWER): sensor.sensor_schema(
                unit_of_measurement=UNIT_PERCENT,
                icon=ICON_POWER,
                accuracy_decimals=0,
                device_class=DEVICE_CLASS_POWER,
                state_class=STATE_CLASS_MEASUREMENT,
            ).extend(
                {
                    cv.Optional(CONF_INTERNAL, default="true"): cv.boolean,
                }
            ),
            cv.Optional(CONF_INDOOR_TEMPERATURE): sensor.sensor_schema(
                unit_of_measurement=UNIT_CELSIUS,
                icon=ICON_THERMOMETER,
                accuracy_decimals=1,
                device_class=DEVICE_CLASS_TEMPERATURE,
                state_class=STATE_CLASS_MEASUREMENT,
            ).extend(
                {
                    cv.Optional(CONF_INTERNAL, default="true"): cv.boolean,
                }
            ),
            cv.Optional(CONF_OUTDOOR_TEMPERATURE): sensor.sensor_schema(
                unit_of_measurement=UNIT_CELSIUS,
                icon=ICON_THERMOMETER,
                accuracy_decimals=0,
                device_class=DEVICE_CLASS_TEMPERATURE,
                state_class=STATE_CLASS_MEASUREMENT,
            ).extend(
                {
                    cv.Optional(CONF_INTERNAL, default="true"): cv.boolean,
                }
            ),
            cv.Optional(CONF_SUPPORTED_MODES): cv.ensure_list(validate_modes),
            cv.Optional(CONF_SUPPORTED_SWING_MODES): cv.ensure_list(validate_swing_modes),
            cv.Optional(CONF_SUPPORTED_PRESETS): cv.ensure_list(validate_presets),
            cv.Optional(CONF_CUSTOM_PRESETS): cv.ensure_list(validate_custom_presets),
            cv.Optional(CONF_CUSTOM_FAN_MODES): cv.ensure_list(validate_custom_fan_modes),
        }
    )
    .extend(uart.UART_DEVICE_SCHEMA)
    .extend(cv.COMPONENT_SCHEMA),
    output_info
)

async def to_code(config):
    """_LOGGER.info("--------------")"""
    """_LOGGER.info(config)"""
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await climate.register_climate(var, config)
    
    parent = await cg.get_variable(config[CONF_UART_ID])
    cg.add(var.initAC(parent))

    if CONF_INDOOR_TEMPERATURE in config:
        conf = config[CONF_INDOOR_TEMPERATURE]
        sens = await sensor.new_sensor(conf)
        cg.add(var.set_indoor_temperature_sensor(sens))

    if CONF_DEFROST_SENSOR in config:
        conf2 = config[CONF_DEFROST_SENSOR]
        sens2 = await binary_sensor.new_binary_sensor(conf2)
        cg.add(var.set_defrost_sensor(sens2))

    if CONF_INVERTOR_POWER in config:
        conf3 = config[CONF_INVERTOR_POWER]
        sens3 = await sensor.new_sensor(conf3)
        cg.add(var.set_invertor_power_sensor(sens3))

    if CONF_OUTDOOR_TEMPERATURE in config:
        conf4 = config[CONF_OUTDOOR_TEMPERATURE]
        sens4 = await sensor.new_sensor(conf4)
        cg.add(var.set_outdoor_temperature_sensor(sens4))

    cg.add(var.set_period(config[CONF_PERIOD].total_milliseconds))
    cg.add(var.set_show_action(config[CONF_SHOW_ACTION]))
    if CONF_SUPPORTED_MODES in config:
        cg.add(var.set_supported_modes(config[CONF_SUPPORTED_MODES]))
    if CONF_SUPPORTED_SWING_MODES in config:
        cg.add(var.set_supported_swing_modes(config[CONF_SUPPORTED_SWING_MODES]))
    if CONF_SUPPORTED_PRESETS in config:
        cg.add(var.set_supported_presets(config[CONF_SUPPORTED_PRESETS]))
    if CONF_CUSTOM_PRESETS in config:
        cg.add(var.set_custom_presets(config[CONF_CUSTOM_PRESETS]))
    if CONF_CUSTOM_FAN_MODES in config:
        cg.add(var.set_custom_fan_modes(config[CONF_CUSTOM_FAN_MODES]))
    