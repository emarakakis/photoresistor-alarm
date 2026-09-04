#include <string.h>

char command[50];
int index = 0;
bool commandFinished = false;

const int ledPin = 2;
int photoResValue = 0;

int RATE = 100;
int lastMeasurement = 0;

bool RUNNING = false;
bool GET = false;

void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
}

void updateCommand(){
  //  If we have bytes to read
  if(Serial.available()){
    char c = Serial.read();

    // The command that we were given has finished
    if (c == '\n'){
      commandFinished = true;
      index = 0;
    } else {

      // Add character, in else case as don't want \n in command
      command[index++] = c;
    }
  }

}

void executeCommand(){

  if(strcmp(command, "START") == 0){
    RUNNING = true;
    Serial.println("START");
  } else if (strcmp(command, "STOP") == 0){
    RUNNING = false;
    Serial.println("STOP");
  } else if (strcmp(command, "GET") == 0){
    GET = true;

    lastMeasurement = millis();
    photoResValue = analogRead(A0);
    
    Serial.print("LIGHT:");
    Serial.println(photoResValue);

  } else if (strcmp(command, "ALARM ON") == 0){
    digitalWrite(ledPin, HIGH);
    Serial.println("ALARM ON");

  } else if (strcmp(command, "ALARM OFF") == 0){
    digitalWrite(ledPin, LOW);
    Serial.println("ALARM OFF");

  } else {

    char rate_string[4];
    char rate_value[45];

    int rate_value_index = 0;

    for(int i = 0; i < 50; i++){
      if(i < 4){
        rate_string[i] = command[i];
      }

      else if(i == 4){
        continue;
      }

      else if(command[i] == '\n')
        break;

      else{
        rate_value[rate_value_index++] = command[i];
      }
    }

    if (strcmp(rate_string, "RATE")){
      
      RATE = atoi(rate_value);
      Serial.print("RATE ");
      Serial.println(RATE);
    }
  }
  clearCommand();
}

void clearCommand(){
  for(int i = 0; i < 50; i++){
    command[i] = NULL;
  }
}

void loop() {

  updateCommand();

  if(commandFinished){
    commandFinished = false;
    executeCommand();
  }

  runProgram();

}

void runProgram(){
  if(!RUNNING){
    return;
  }

  if(millis() > lastMeasurement + RATE){
    
    lastMeasurement = millis();
    photoResValue = analogRead(A0);

    Serial.print("LIGHT:");
    Serial.println(photoResValue);
  }

}
