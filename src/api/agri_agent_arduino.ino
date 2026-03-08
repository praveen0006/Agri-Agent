/*
 * Agri-Agent: Precision Irrigation System - Arduino Mega 2560 Sketch
 * 
 * This sketch:
 * 1. Reads a capacitive soil moisture sensor on Analog Pin A0.
 * 2. Outputs the moisture value over Serial in the format "MOISTURE:XX.X".
 * 3. Listens for "PUMP:XXX" commands from the PC to trigger a relay.
 */

const int moisturePin = A0;      // Soil moisture sensor pin
const int relayPin = 7;          // Relay module pin for pump
const int airValue = 790;        // Value in air (dry) - CALIBRATE THIS
const int waterValue = 380;      // Value in water (wet) - CALIBRATE THIS

void setup() {
  Serial.begin(9600);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH);  // Assuming Active LOW relay, turn OFF initially
  
  // Wait for serial to initialize
  while (!Serial); 
}

void loop() {
  // 1. Read Soil Moisture
  int sensorValue = analogRead(moisturePin);
  
  // Convert to percentage (0% to 100%)
  // Inverse mapping: higher analog value usually means dryer soil for capacitive sensors
  float moisturePercent = map(sensorValue, airValue, waterValue, 0, 100);
  
  // Constrain to 0-100 range
  if (moisturePercent > 100) moisturePercent = 100;
  if (moisturePercent < 0) moisturePercent = 0;

  // 2. Transmit to Gateway
  Serial.print("MOISTURE: ");
  Serial.println(moisturePercent);

  // 3. Listen for commands from Gateway
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("PUMP:")) {
      int duration = command.substring(5).toInt();
      if (duration > 0) {
        handlePump(duration);
      }
    }
  }

  delay(2000); // Read every 2 seconds
}

void handlePump(int durationSeconds) {
  // Turn ON pump (assuming Active LOW relay)
  digitalWrite(relayPin, LOW); 
  
  // Calculate end time
  unsigned long endTime = millis() + (durationSeconds * 1000UL);
  
  // Wait while reporting status or checking for abort (optional)
  while (millis() < endTime) {
    // Keep reporting moisture during pumping
    // ...
  }
  
  // Turn OFF pump
  digitalWrite(relayPin, HIGH);
}
