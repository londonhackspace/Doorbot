int triggerPin = 13;
int ledPin = 12;
int doorBellButton = 14;
int doorBellLEDRed = 15;
int doorBellLEDGreen = 16;

void setup()
{
  Serial.begin(9600);
  pinMode(triggerPin, OUTPUT);
  pinMode(ledPin, OUTPUT);


  pinMode(doorBellButton, INPUT);
  pinMode(doorBellLEDGreen, OUTPUT);
  pinMode(doorBellLEDRed, OUTPUT);
  digitalWrite(doorBellButton, HIGH);


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
      Serial.println("Door opened");
    }
    Serial.flush();
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
