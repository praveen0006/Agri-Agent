import serial
import time
import threading


class ArduinoSerialManager:
    """
    Manages the connection and data retrieval from an Arduino Mega 2560.
    Runs a background thread to continuously read data into the hardware_state.
    """

    def __init__(self, port: str = "COM4", baud_rate: int = 9600, state_ref: dict = None):
        self.port = port
        self.baud_rate = baud_rate
        self.state_ref = state_ref if state_ref is not None else {}
        self.serial_conn = None
        self._running = False
        self._thread = None

    def connect(self):
        """
        Opens the serial connection to the Arduino and starts the background read thread.
        Falls back to simulation mode if the port is unavailable.
        """
        try:
            self.serial_conn = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset upon connection
            print(f"Connected to Arduino on {self.port}")
            self._running = True
            self._thread = threading.Thread(target=self._read_loop, daemon=True)
            self._thread.start()
        except serial.SerialException as e:
            print(f"Error connecting to Arduino: {e}")
            print("Running in simulation mode.")
            self.serial_conn = None

    def _read_loop(self):
        """
        Internal loop running in a background thread to parse incoming serial data.
        Updates the shared state reference with moisture values.
        """
        print(f"   [SERIAL] Background read thread started for {self.port}")
        loop_count = 0
        while self._running and self.serial_conn:
            try:
                loop_count += 1
                if loop_count % 50 == 0:  # Every ~5 seconds
                    print(f"   [SERIAL HEARTBEAT] Thread is alive, waiting for data on {self.port}...")

                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode("utf-8").strip()
                    if line:
                        print(f"   [SERIAL DEBUG] Raw Line: '{line}'")
                        # Check for the MOISTURE: prefix
                        if "MOISTURE" in line.upper():
                            try:
                                # Split by : and handle potential format variations
                                parts = line.split(":")
                                if len(parts) >= 2:
                                    val_str = parts[1].strip()
                                    val = float(val_str)
                                    self.state_ref["moisture_percent"] = val
                                    print(f"   [SERIAL] Updated State: {val}%")
                            except (ValueError, IndexError) as e:
                                print(f"   [SERIAL] Parse Error: {e} in '{line}'")
                else:
                    time.sleep(0.1)  # Small sleep to prevent CPU spiking
            except Exception as e:
                print(f"   [SERIAL] Read error: {e}")
                time.sleep(1)

    def disconnect(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("Disconnected from Arduino.")


if __name__ == "__main__":
    test_state = {"moisture_percent": 0.0}
    manager = ArduinoSerialManager(port="COM4", state_ref=test_state)
    manager.connect()
    try:
        for _ in range(5):
            print(f"Current State: {test_state}")
            time.sleep(2)
    finally:
        manager.disconnect()
