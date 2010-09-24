int triggerPin = 13;
int doorBellButton = 2;

void setup()
{
  Serial.begin(9600);
  pinMode(triggerPin, OUTPUT);
  pinMode(doorBellButton, INPUT);
  pinMode(doorBellLEDGreen, OUTPUT);
  pinMode(doorBellLEDRed, OUTPUT);
  digitalWrite(doorBellButton, HIGH);
}

void loop()
{
  // Check for door unlock command
  if (Serial.available() > 0) {
    char inByte = Serial.read();

    if (inByte == '1') {
      // Strobe a little
      for (int i = 0; i < 2; i++) {
        digitalWrite(triggerPin, HIGH);
        delay(100);
        digitalWrite(triggerPin, LOW);
        delay(30);
      }
      delay(500); // Pause to ensure it resets
    }
  }
  // Check door bell button
  if(digitalRead(doorBellButton)){
    digitalWrite(doorBellLEDGreen, LOW);
    digitalWrite(doorBellLEDRed, HIGH);
  }
  else{
    digitalWrite(doorBellLEDRed, LOW);
    digitalWrite(doorBellLEDGreen, HIGH);
  }  
}
