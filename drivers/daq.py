import nidaqmx
import configparser
from nidaqmx.constants import TerminalConfiguration

class NIDAQ:

    def __init__(self, channel: str, min_val: float, max_val: float):
        self.channel = channel
        self.min_val = min_val
        self.max_val = max_val
        self._task   = None

    @classmethod
    def from_config(cls, config_path: str) -> "NIDAQ":
        cfg = configparser.ConfigParser()
        cfg.read(config_path)
        return cls(
            channel = cfg.get("DAQ", "channel"),
            min_val = cfg.getfloat("DAQ", "min_val"),
            max_val = cfg.getfloat("DAQ", "max_val"),
        )

    def open(self):
        self._task = nidaqmx.Task()
        self._task.ai_channels.add_ai_voltage_chan(
            self.channel,
            terminal_config=TerminalConfiguration.RSE,
            min_val=self.min_val,
            max_val=self.max_val
        )

    def read_voltage(self) -> float:
        if self._task is None:
            raise RuntimeError("DAQ not open. Call open() first.")
        return self._task.read()

    def close(self):
        if self._task is not None:
            self._task.close()
            self._task = None