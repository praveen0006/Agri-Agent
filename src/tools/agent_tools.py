import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_moisture_data() -> dict:
    """
    Retrieves soil moisture percentage from the FastAPI gateway (ESP32 / Arduino mock).
    Returns a dictionary with the moisture percentage.
    """
    try:
        response = requests.get("http://127.0.0.1:8000/moisture", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to retrieve moisture data: {str(e)}", "moisture_percent": None}


def trigger_pump(duration: int) -> dict:
    """
    Activates irrigation pump for specified seconds via the FastAPI gateway.
    Requires human approval before execution in the agent node logic.
    """
    try:
        response = requests.post("http://127.0.0.1:8000/pump", json={"duration_seconds": duration}, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to trigger pump: {str(e)}"}


def get_weather_forecast() -> dict:
    """
    Retrieves real-time weather forecast parameters using OpenWeatherMap API.
    Used for anticipating rain before deciding to irrigate.
    """
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    lat = os.getenv("APP_LAT", "17.3850")  # Default to Hyderabad, India if not set
    lon = os.getenv("APP_LON", "78.4867")

    if not api_key:
        print("   ⚠️ No OpenWeatherMap API Key found. Using mock data.")
        return {"temperature_celsius": 28.5, "humidity_percent": 45.0, "rain_probability": 0.0, "wind_speed_ms": 2.5}

    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Forecasts come in 3-hour intervals. We look at the next 12 hours (4 intervals).
        forecasts = data.get("list", [])[:4]
        if not forecasts:
            return {"error": "No forecast data found in API response."}

        avg_temp = sum(f["main"]["temp"] for f in forecasts) / len(forecasts)
        avg_humidity = sum(f["main"]["humidity"] for f in forecasts) / len(forecasts)
        # 'pop' is Probability of Precipitation (0 to 1)
        rain_prob = max(f.get("pop", 0) for f in forecasts) * 100

        return {
            "temperature_celsius": round(avg_temp, 1),
            "humidity_percent": round(avg_humidity, 1),
            "rain_probability": round(rain_prob, 1),
            "wind_speed_ms": forecasts[0]["wind"]["speed"],
        }

    except Exception as e:
        return {"error": f"Failed to retrieve weather: {str(e)}"}


def calculate_evapotranspiration(temperature_c: float, humidity_percent: float, wind_speed_ms: float) -> str:
    """
    Python REPL tool wrapper used to compute general Evapotranspiration (ET).
    This uses a simplified Penman-Monteith approximation.
    Formula: ET = (0.408Δ(Rn-G) + γ(900/(T+273))u₂(es-ea)) / (Δ + γ(1+0.34u₂))
    """
    # Simply using the tool as a wrapper logic for the theoretical Python REPL node
    # to evaluate the required formula:
    script = f"""
import math
T = {temperature_c}
u2 = {wind_speed_ms}
rh = {humidity_percent}
# Simplified estimate for demonstration
es = 0.6108 * math.exp((17.27 * T) / (T + 237.3))
ea = es * (rh / 100)
ET_approx = (0.408 * 12 + 0.066 * (900/(T+273)) * u2 * (es-ea)) / (0.6 + 0.066*(1+0.34*u2))
print(round(ET_approx, 2))
"""
    try:
        # A real REPL would exec() or run via subprocess.
        # Here we just evaluate locally for safety.
        import math

        T = temperature_c
        u2 = wind_speed_ms
        rh = humidity_percent
        es = 0.6108 * math.exp((17.27 * T) / (T + 237.3))
        ea = es * (rh / 100)
        et_approx = (0.408 * 12 + 0.066 * (900 / (T + 273)) * u2 * (es - ea)) / (0.6 + 0.066 * (1 + 0.34 * u2))
        return f"Evapotranspiration (ETo): {round(et_approx, 2)} mm/day"
    except Exception as e:
        return f"Error calculating ET: {str(e)}"


def get_camera_frame() -> str:
    """
    Retrieves the latest image/frame path from the mobile IP camera.
    In production, this would hit the MJPEG stream or an RTSP snapshot.
    """
    # Mocking the camera feed location
    camera_url = os.getenv("IP_CAMERA_URL", "http://192.168.0.124:8080/video")
    return f"Camera Feed Active at {camera_url}. Image analysis: Crop appears healthy, soil surface is visually dry."
