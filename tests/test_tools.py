import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.tools.agent_tools import get_moisture_data, trigger_pump, get_weather_forecast, calculate_evapotranspiration


def test_tools():
    print("--- Testing Agri-Agent Tools ---\n")

    # 1. Test Moisture Sensor Tool
    print("1. Testing get_moisture_data()...")
    moisture = get_moisture_data()
    print(f"   Result: {moisture}\n")

    # 2. Test Weather Tool (using Mock)
    print("2. Testing get_weather_forecast()...")
    weather = get_weather_forecast()
    print(f"   Result: {weather}\n")

    # 3. Test ET Calculation Tool
    print("3. Testing calculate_evapotranspiration()...")
    et = calculate_evapotranspiration(
        weather["temperature_celsius"], weather["humidity_percent"], weather["wind_speed_ms"]
    )
    print(f"   Result: {et}\n")

    # 4. Test Pump Trigger Tool
    print("4. Testing trigger_pump(duration=5)...")
    pump = trigger_pump(5)
    print(f"   Result: {pump}\n")


if __name__ == "__main__":
    test_tools()
