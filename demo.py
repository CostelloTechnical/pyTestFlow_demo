from pathlib import Path
import sys
import configparser

from pytestflow.core import ptf_context
from pytestflow.core.sequence import TestSequence
from pytestflow.steps.action_step import action_step
from pytestflow.steps.numeric_limit import numeric_limit_step
from pytestflow.steps.string_check import string_check_step
from pytestflow.steps.pass_fail import pass_fail_step

sys.path.insert(0, str(Path(__file__).parent))

from drivers.daq import NIDAQ as DAQ
from drivers.psu import RSPowerSupply as PSU

CONFIG_PATH = Path(__file__).parent / "drivers" / "config.ini"

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

EXPECTED_MODEL = config.get("PSU", "model")

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def get_user_serial_number() -> str:
    user_response = ptf_context.locals.get("_pre_uut_user_response")
    if not isinstance(user_response, dict):
        return ""
    return str(user_response.get("text", "") or "")


def get_daq():
    daq = ptf_context.locals.get("daq_handle")
    if daq is None:
        raise RuntimeError("daq_handle not initialized")
    return daq


def get_psu():
    psu = ptf_context.locals.get("psu_handle")
    if psu is None:
        raise RuntimeError("psu_handle not initialized")
    return psu

# ------------------------------------------------------------
# Startup Steps
# ------------------------------------------------------------

@action_step(name="init_daq", store_as="daq_handle")
def init_daq():
    daq = DAQ.from_config(str(CONFIG_PATH))
    daq.open()
    return daq


@action_step(name="init_psu", store_as="psu_handle")
def init_psu():
    psu = PSU.from_config(str(CONFIG_PATH))
    psu.open()
    return psu

# ------------------------------------------------------------
# Main Test Steps
# ------------------------------------------------------------

@action_step(name="enable_output")
def enable_output():
    get_psu().set_output(True)


@pass_fail_step(name="check_output_on")
def check_output_on():
    return get_psu().get_output_status()


@string_check_step(name="check_serial_number", expected=get_user_serial_number, match="exact")
def check_serial_number():
    return get_psu().get_serial_number()


@string_check_step(name="check_model", expected=EXPECTED_MODEL, match="exact")
def check_model():
    return get_psu().get_device_model()


@action_step(name="set_voltage_0VDC")
def set_voltage_0VDC():
    get_psu().set_voltage(0.00)


@numeric_limit_step(name="measure_0VDC", limit=(-0.1, 0.1), mode="between")
def measure_0VDC():
    return get_daq().read_voltage()


@action_step(name="set_voltage_1VDC")
def set_voltage_1VDC():
    get_psu().set_voltage(1.00)


@numeric_limit_step(name="measure_1VDC", limit=(0.9, 1.1), mode="between")
def measure_1VDC():
    return get_daq().read_voltage()


@action_step(name="set_voltage_3VDC")
def set_voltage_3VDC():
    get_psu().set_voltage(3.00)


@numeric_limit_step(name="measure_3VDC", limit=(2.9, 3.1), mode="between")
def measure_3VDC():
    return get_daq().read_voltage()

@action_step(name="disable_output")
def disable_output():
    get_psu().set_output(False)

# ------------------------------------------------------------
# Cleanup Steps
# ------------------------------------------------------------

@action_step(name="close_daq")
def close_daq():
    daq = ptf_context.locals.get("daq_handle")
    if daq is not None:
        daq.close()


@action_step(name="close_psu")
def close_psu():
    psu = ptf_context.locals.get("psu_handle")
    if psu is not None:
        psu.close()


def main_sequence() -> TestSequence:
    return TestSequence(
        name="demo_sequence",
        setup_steps=[init_daq, init_psu],
        main_steps=[
            check_serial_number,
            check_model,
            enable_output,
            check_output_on,
            set_voltage_0VDC, measure_0VDC,
            set_voltage_1VDC, measure_1VDC,
            set_voltage_3VDC, measure_3VDC,
            disable_output,
        ],
        cleanup_steps=[close_daq, close_psu],
    )


PROCESS_HOOKS = {
    "main_sequence": main_sequence,
}