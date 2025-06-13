#include <DFRobot_LTR308.h>

DFRobot_LTR308 light;

void setup(){
    Serial.begin(115200);
  //// If a camera is used, please initialize the camera before the initialization of LTR308; otherwise, the read value will be 0
    while(!light.begin()){
    Serial.println("Initialization failed!");
    delay(1000);
  }
  Serial.println("Initialization successful!");
}
void loop(){
  uint32_t data = light.getData();
  Serial.print("Original Data: ");
  Serial.println(data);
  Serial.print("Lux Data: ");
  Serial.println(light.getLux(data));
  delay(500);
}