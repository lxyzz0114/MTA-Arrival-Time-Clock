#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

////----------------------------------------------------
////    Hardware Configurations
////----------------------------------------------------

// OLED LCD display configuration
constexpr int SCREEN_WIDTH = 128;
constexpr int SCREEN_HEIGHT = 64;
constexpr int OLED_SDA_PIN = 21;
constexpr int OLED_SCL_PIN = 22;
constexpr uint8_t OLED_ADDRESS = 0x3C;
constexpr int OLED_RESET_PIN = -1;

Adafruit_SSD1306 display(
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    &Wire,
    OLED_RESET_PIN
);

//Push buttons Configuration
constexpr int PREVIOUS_BUTTON_PIN = 27;
constexpr int NEXT_BUTTON_PIN = 26;

////----------------------------------------------------
////    Declare Functions
////----------------------------------------------------

////----------------------------------------------------
////    Boards
////----------------------------------------------------
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(PREVIOUS_BUTTON_PIN, INPUT_PULLUP);
  pinMode(NEXT_BUTTON_PIN, INPUT_PULLUP); 
}

void loop() {
  // put your main code here, to run repeatedly:
}

////----------------------------------------------------
////    Functions Definitions
////----------------------------------------------------