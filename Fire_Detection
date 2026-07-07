#include <DHT.h>
#include <MQ2.h>
#include <Servo.h>

// Pin Configuration
#define DHT_PIN 7
#define FLAME_PIN A1
#define MQ2_PIN A0
#define SERVO_PIN 10
#define LED_RED 12
#define LED_GREEN 13

// DHT Sensor Type
#define DHTTYPE DHT22
DHT dht(DHT_PIN, DHTTYPE);
MQ2 mq2(MQ2_PIN);
Servo fireExtinguisher;

// Sensor Thresholds
#define TEMP_THRESHOLD 50
#define HUMIDITY_THRESHOLD 30
#define SMOKE_THRESHOLD 500
#define TEMP_SPIKE_THRESHOLD 5
#define FLAME_THRESHOLD 400

// Variables for tracking temperature history
float tempHistory[3] = {0, 0, 0};
bool fireActive = false;

void setup() {
    Serial.begin(115200);
    dht.begin();
    mq2.begin();
    pinMode(FLAME_PIN, INPUT);
    pinMode(LED_RED, OUTPUT);
    pinMode(LED_GREEN, OUTPUT);
    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_RED, LOW);
    fireExtinguisher.attach(SERVO_PIN);
    fireExtinguisher.write(0);
}

void loop() {
    float temperature = readTemperature();
    float humidity = readHumidity();
    float smokeLevel = readSmokeLevel();
    bool fireDetected = readFlameSensor();

    // Compute the average of the last three temperature values
    float avgTemperature = (tempHistory[0] + tempHistory[1] + tempHistory[2]) / 3;
    bool tempSpike = (temperature - avgTemperature) > TEMP_SPIKE_THRESHOLD;

    int fireIndicators = 0;
    if (fireDetected) fireIndicators++;
    if (smokeLevel > SMOKE_THRESHOLD) fireIndicators++;
    if (tempSpike) fireIndicators++;
    if (humidity < HUMIDITY_THRESHOLD) fireIndicators++;

    // Send data to Serial (to be read by Python)
    Serial.print(temperature);
    Serial.print(",");
    Serial.print(humidity);
    Serial.print(",");
    Serial.print(smokeLevel);
    Serial.print(",");
    Serial.print(fireDetected);
    Serial.print(",");
    Serial.println(tempSpike);

    if (fireIndicators >= 2) {
        activateFireSuppression();
        fireActive = true;
        digitalWrite(LED_RED, HIGH);
        digitalWrite(LED_GREEN, LOW);
    } else {
        deactivateFireSuppression();
        fireActive = false;
        digitalWrite(LED_RED, LOW);
        digitalWrite(LED_GREEN, HIGH);
    }

    tempHistory[0] = tempHistory[1];
    tempHistory[1] = tempHistory[2];
    tempHistory[2] = temperature;

    delay(2000);
}

float readTemperature() {
    float temp = dht.readTemperature();
    return isnan(temp) ? tempHistory[2] : temp;
}

float readHumidity() {
    float hum = dht.readHumidity();
    return isnan(hum) ? 0 : hum;
}

float readSmokeLevel() {
    return mq2.readSmoke();
}

bool readFlameSensor() {
    return analogRead(FLAME_PIN) < FLAME_THRESHOLD;
}

void activateFireSuppression() {
    fireExtinguisher.write(90);
}

void deactivateFireSuppression() {
    fireExtinguisher.write(0);
}
