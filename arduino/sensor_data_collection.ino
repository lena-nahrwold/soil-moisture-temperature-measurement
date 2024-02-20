#include <SPI.h>
#include <SD.h>  
#include "DHT.h"

#define DHTPIN 2 // Digital pin connected to the DHT sensor
#define DHTTYPE DHT11 // DHT 11
#define POWER_PIN   7
#define WATER_SENSOR_PIN  A0
#define air 445 // Calibration of soil moisture sensor
#define water 189

File file;

// Initialize DHT sensor
DHT dht(DHTPIN, DHTTYPE);

void setup(){
  Serial.begin(9600);

  Serial.println("initialize SD-card");   

  while (!SD.begin(5)) {                          
    Serial.println("initialization failed");   
  }
  
  Serial.println("SD card initialized");

  while (!file) {
    if (SD.exists("data.csv")) {
      file = SD.open("data.csv", FILE_WRITE);
      Serial.println("found csv file");
    } else {
      file = SD.open("data.csv", FILE_WRITE);
      Serial.println("created csv file");
      file.println("soil_moisture,soil_moisture_p,humidity_p,temperature_c,heat_index_c"); // Column headers
    }
    if (!file) {
      Serial.println("error creating or opening file");
    }
  }

  file.close();
  pinMode(POWER_PIN, OUTPUT);
  digitalWrite(POWER_PIN, LOW);
  dht.begin();
}

//globals
int freq = 1000; // Data collection frequency ~x milliseconds
float m = 0;
float p = 0;
float h = 0;
float t = 0;
float hic = 0;

void loop(){
  while (!SD.begin(5)) {                          
    Serial.println("SD card not found");   
  }
  file = SD.open("data.csv", FILE_WRITE);
  if (file) { 
    Serial.println("taking measurements");                               
    // Soil moisture sensor
    digitalWrite(POWER_PIN, HIGH);  // Turn the sensor ON
    delay(10);                      // Wait 10 milliseconds
    m = analogRead(WATER_SENSOR_PIN); // Read the analog moisture value from sensor
    digitalWrite(POWER_PIN, LOW);   // Turn the sensor OFF
    file.print(m);
    file.print(",");
    p = map(m, air, water, 0, 100); // Calculate soil moisture percentage
    if (p >= 100) {
      file.print(100);
    } else if (p <= 0) {
      file.print(0);
    } else if (p > 0 && p < 100) {
      file.print(p);
    }
    file.print(",");

    // Humidity and temperatur sensor
    // Reading temperature or humidity takes about 250 milliseconds!
    // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
    h = dht.readHumidity();
    // Read temperature as Celsius (the default)
    t = dht.readTemperature();
    // Check if any reads failed and exit early (to try again).
    if (isnan(h) || isnan(t)) {
      Serial.println(F("Failed to read from DHT sensor!"));
      return;
    }
    // Compute heat index in Celsius (isFahreheit = false)
    hic = dht.computeHeatIndex(t, h, false);
    file.print(h);
    file.print(",");
    file.print(t);
    file.print(",");
    file.println(hic);
                                
    file.close();
  } else {
    Serial.println("could not read file");
  }

  delay(freq);
}