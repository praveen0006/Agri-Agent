from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
from src.api.hardware_serial import ArduinoSerialManager

app = FastAPI(title="Agri-Agent IoT Gateway")

# Current state of the simulated hardware
# In a real scenario, this would be updated via Serial communication with Arduino
hardware_state = {"moisture_percent": 0.0, "pump_status": "OFF"}

arduino_manager = ArduinoSerialManager(port="COM4", state_ref=hardware_state)


@app.on_event("startup")
async def startup_event():
    """Connect to the Arduino when the API starts."""
    arduino_manager.connect()


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up the serial connection when the API stops."""
    arduino_manager.disconnect()


class PumpRequest(BaseModel):
    duration_seconds: int


@app.get("/moisture")
async def get_moisture():
    """
    Reads from the hardware state, which is continuously updated by the serial thread.
    If hardware is disconnected (simulation mode), returns a random fluctuation.
    """
    if arduino_manager.serial_conn is None:
        # Simulate slight sensor noise if running without physical hardware
        current_moisture = hardware_state["moisture_percent"] + random.uniform(-1.5, 1.5)
        current_moisture = max(0.0, min(100.0, current_moisture))
        hardware_state["moisture_percent"] = current_moisture

    return {"moisture_percent": round(hardware_state["moisture_percent"], 2)}


# --- CONFIG ---
SIMULATION_MODE = False  # Set to False to use real Arduino over Serial


@app.post("/pump")
async def trigger_pump(request: PumpRequest):
    """
    Simulates sending a pump activation command to the Arduino via Serial.
    """
    if request.duration_seconds <= 0:
        raise HTTPException(status_code=400, detail="Duration must be positive")
    if request.duration_seconds > 600:
        raise HTTPException(status_code=400, detail="Duration too long for safety limit (10 mins max)")

    hardware_state["pump_status"] = "ON"

    # If we had a real serial command for a pump we would send it here
    if arduino_manager.serial_conn and arduino_manager.serial_conn.is_open:
        arduino_manager.serial_conn.write(f"PUMP:{request.duration_seconds}\n".encode())

    return {
        "status": "success",
        "message": f"Pump activated for {request.duration_seconds} seconds",
        "current_state": "ON",
    }


@app.get("/status")
async def get_hardware_status():
    """Returns the overall state of the simulated hardware"""
    return hardware_state
