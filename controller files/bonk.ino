int ledPin = 10;
int microphonePin = 1;
int state = 0;
int state2 = 0;
const int microphonePin2 = A0;


void setup() {
  pinMode(microphonePin2, INPUT);
  pinMode(microphonePin, INPUT);
  Serial.begin(9600);
  state2 = analogRead(microphonePin2);
  state = analogRead(microphonePin2);



}

void loop() {
  

  //Serial.println(state);

  state2 = analogRead(microphonePin2);

  //Serial.println(state2);

  if (abs(state-state2)>100) {
    //for(int i = 0; i<20; i++){
    Serial.println("BONK");
    //}
    Serial.println(state);
    Serial.println(state2);

    //delay(10000);
    //delay(1000);
    //Serial.println("high");
  }


  state = analogRead(microphonePin2);

}
