#include <FastLED.h>

#define NUM_LEDS 1
#define LED_PIN 2
#define COLOR_ORDER GRB

CRGB leds[NUM_LEDS];

const int relay = 5;

String incomingData; // for incomingData serial data
String dataArray[4]; // for storing incomingData

int rVal = 0;
int gVal = 0;
int bVal = 0;
int relayVal = 0;
char colOrRelay;

void fillArray(String data, String tArray[], char separator){
  int maxIndex = data.length();
  int arrayIndex = 0;
  int startIndex = 0;
  
  for(int i=0; i<maxIndex; i++){
    if(data.charAt(i)==separator){
      tArray[arrayIndex] = data.substring(startIndex, i);
      arrayIndex++;
      startIndex = i + 1; // +1 to skip the separator
    }
  }
}

void jiggleQuack(){
  digitalWrite(relay, LOW);
  delay(400);
  digitalWrite(relay, HIGH);
  delay(200);
  digitalWrite(relay, LOW);
  delay(200);
  digitalWrite(relay, HIGH);
  delay(200);
  digitalWrite(relay, LOW);
  delay(200);
  digitalWrite(relay, HIGH);
  delay(200);
}


void setup() {
  Serial.begin(9600);
  pinMode(relay, OUTPUT);
  digitalWrite(relay, HIGH);
  FastLED.addLeds<WS2812, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS);
  //blink once to indicate turning on/rebooting.
  for(int i = 0; i<NUM_LEDS; i++){
          leds[i] = CRGB(255, 255, 255);
  }
  FastLED.show();
  delay(500);
  
  for(int i = 0; i<NUM_LEDS; i++){
          leds[i] = CRGB(0, 0, 0);
  }
  FastLED.show();
  
  Serial.println("Arduino up and running");
  delay(500);
}

void loop() {
  // send data only when you receive data:
  if (Serial.available() > 0) {
    // read the incomingData byte:
    incomingData = Serial.readString();
    Serial.print("I received: ");
    Serial.println(incomingData);
    fillArray(incomingData, dataArray, '/');
    
    if(dataArray[0] == "c"){
      Serial.println("color control");
      rVal = dataArray[1].toInt();
      gVal = dataArray[2].toInt();
      bVal = dataArray[3].toInt();
      // Not really needed as i only use 1 LED right now...
      for(int i = 0; i<NUM_LEDS; i++){
        leds[i] = CRGB(rVal, gVal, bVal);
      }
      FastLED.show();
    }
    else if(dataArray[0] == "r"){
      relayVal = dataArray[1].toInt();

      if(relayVal == 1){
      Serial.println("Jiggle jiggle");
      jiggleQuack();
      }
      else{
        Serial.print("Nothing to do, got: ");
        Serial.println(relayVal);
      }
    }
    else{
      Serial.print("first index is: ");
      Serial.println(dataArray[0]);
    }
  }
}
