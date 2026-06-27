import serial
import time
import configparser

class RSPowerSupply:

    def __init__(self, port: str, baudrate: int, timeout: float):
        self.port     = port
        self.baudrate = baudrate
        self.timeout  = timeout
        self.ser      = None

    @classmethod
    def from_config(cls, config_path: str) -> "RSPowerSupply":
        cfg = configparser.ConfigParser()
        cfg.read(config_path)
        return cls(
            port     = cfg.get("PSU", "port"),
            baudrate = cfg.getint("PSU", "baudrate"),
            timeout  = cfg.getfloat("PSU", "timeout"),
        )

    def open(self):
        try:
            self.ser = serial.Serial(
                port=self.port, baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE, timeout=self.timeout
            )
            time.sleep(0.1)
        except Exception as e:
            raise RuntimeError(f"Failed to open {self.port}: {type(e).__name__}: {e}") from e

    def close(self):
        if self.ser is not None and self.ser.is_open:
            self.ser.close()
            self.ser = None

    def _send_command(self, cmd: str):
        self.ser.write(f"{cmd}\n".encode("utf-8"))
        time.sleep(0.05)

    def _read_response(self) -> str:
        return self.ser.readline().decode("utf-8").strip()

    def identify(self) -> str:
        self._send_command("*IDN?")
        return self._read_response()

    def get_serial_number(self) -> str:
        self._send_command("*IDN?")
        return self._read_response().partition("SN:")[2]

    def get_device_model(self) -> str:
        self._send_command("*IDN?")
        return self._read_response().partition("V")[0].strip()

    def get_device_status(self) -> dict:
        self.ser.write(b"STATUS?\n")
        raw_data = self.ser.readline()
        if not raw_data:
            raise RuntimeError("STATUS? timed out — no data received.")
        status_int = raw_data[0]
        return {
            "raw_decimal":   status_int,
            "binary_string": f"{status_int:08b}",
            "output_on":     (status_int & 64) == 64,
            "mode":          "CV" if (status_int & 1) == 1 else "CC"
        }
    
    def enable_output(self):
        self.set_output(True)

    def disable_output(self):
        self.set_output(False)

    def get_output_status(self) -> bool:
        return self.get_device_status()["output_on"]

    def set_voltage(self, voltage: float, channel: int = 1):
        self._send_command(f"VSET{channel}:{voltage:.2f}")

    def get_actual_voltage(self, channel: int = 1) -> str:
        self._send_command(f"VOUT{channel}?")
        return self._read_response()

    def set_output(self, state: bool):
        self._send_command(f"OUT{1 if state else 0}")