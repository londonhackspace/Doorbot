int triggerPin = D11;
int ledPin = D12;
// We're using analogue pins in digital mode.
int doorBellButton = A0;
int doorBellLEDRed = A2;
int doorBellLEDGreen = A1;
int sounder = A3;
int changed = 0;

// Variables will change:
int buttonState;             // the current reading from the input pin
int lastButtonState = HIGH;   // the previous reading from the input pin

// the following variables are long's because the time, measured in miliseconds,
// will quickly become a bigger number than can be stored in an int.
long lastDebounceTime = 0;  // the last time the output pin was toggled
long debounceDelay = 50;    // the debounce time; increase if the output flickers

void setup()
{
  Serial.begin(9600);
  pinMode(triggerPin, OUTPUT);
  pinMode(ledPin, OUTPUT);


  pinMode(doorBellButton, INPUT);
  digitalWrite(doorBellButton, HIGH);
  pinMode(doorBellLEDGreen, OUTPUT);
  pinMode(doorBellLEDRed, OUTPUT);
  pinMode(sounder, OUTPUT);


  // Booted signal
  for(int i = 0; i < 3; i++) {
    digitalWrite(ledPin, LOW);
    delay(300);
    digitalWrite(ledPin, HIGH);
    delay(100);
  }

}

void loop()
{

  // Check for door unlock command
  if (Serial.available() > 0) {
    int inByte = Serial.read();

    if (inByte == '1') {
      Serial.println("Opening door");
      digitalWrite(ledPin, LOW);
      digitalWrite(doorBellLEDGreen, HIGH);

      if(false) {
        // Strobe a little
        for (int i = 0; i < 3; i++) {
          digitalWrite(triggerPin, HIGH);
          delay(100);
          digitalWrite(triggerPin, LOW);
          delay(30);
        }
      } else {
        // Constant on
        digitalWrite(triggerPin, HIGH);
        delay(1000);
        digitalWrite(triggerPin, LOW);
      }

      digitalWrite(ledPin, HIGH);
      digitalWrite(doorBellLEDGreen, LOW);
      Serial.println("Door opened");
    }
    else if (inByte == '2'){
      // Turn Green on
      digitalWrite(doorBellLEDGreen, HIGH);
    }
    else if (inByte == '3'){
      // Turn Green off
      digitalWrite(doorBellLEDGreen, LOW);
    }
    else if (inByte == '4'){
      // Turn Red on
      digitalWrite(doorBellLEDRed, HIGH);
    }
    else if (inByte == '5'){
      // Turn Red off
      digitalWrite(doorBellLEDRed, LOW);
    }
    else if (inByte == '6'){
      digitalWrite(sounder, HIGH);
      delay(500);
      digitalWrite(sounder, LOW);
      delay(500);
      digitalWrite(sounder, HIGH);
      delay(500);
      digitalWrite(sounder, LOW);
      delay(500);
      digitalWrite(sounder, HIGH);
      delay(500);
      digitalWrite(sounder, LOW);
      delay(500);
    }
    
    //Serial.flush();
  }

  // read the state of the switch into a local variable:
  int reading = digitalRead(doorBellButton);
  
  if (reading != lastButtonState) {
    // reset the debouncing timer
    lastDebounceTime = millis();
    changed = 1;
  } 

  if ((millis() - lastDebounceTime) > debounceDelay) {
    // whatever the reading is at, it's been there for longer
    // than the debounce delay, so take it as the actual current state:
    buttonState = reading;
    if(changed == 1){
      // Send bell pressed
      if(buttonState == LOW){
        Serial.println("1");
      }
      changed = 0;
    }
  }
  // save the reading.  Next time through the loop,
  // it'll be the lastButtonState:
  lastButtonState = reading;
}
