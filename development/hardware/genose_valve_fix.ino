#include <Wire.h>

// Alamat I2C untuk masing-masing ADS1115
//R
#define ADS1115_ADDRESS_1 0x48 //kanan atas kepake 2
#define ADS1115_ADDRESS_2 0x4A //kanan bawah kepake 3

//L
#define ADS1115_ADDRESS_3 0x49 //kiri bawah kepake 2
#define ADS1115_ADDRESS_4 0x4B //kiri atas kepake 3

// Registrasi pada ADS1115
#define ADS1115_REG_CONVERT 0x00
#define ADS1115_REG_CONFIG  0x01

#define PIN_VALVE 10

#define DEFAULT_SERIAL_BAUDRATE 9600
#define SAMPLE_DELAY_TIME 20

typedef enum COMMAND {
  START_SAMPLING = 0,
  STOP_SAMPLING,
  SET_FLUSH,
  SET_INHALE
} command_t;

unsigned long previousMillis = 0; // untuk menyimpan waktu sebelumnya
const long intervalHigh = 500;   // durasi HIGH 1 detik (1000 ms)
const long intervalLow = 20000;    // durasi LOW 3 detik (3000 ms)
bool isHigh = false;              // status pin 10 apakah HIGH atau LOW

bool isSampling = false;

String serialRecv = "";

void configureADS1115(uint8_t address);
int16_t readADS1115(uint8_t address, uint8_t channel);
void sampling();
void handleValve();
void sampleSerial();
void parseMessage(String message);

void setup() {
  Wire.begin();
  Serial.begin(DEFAULT_SERIAL_BAUDRATE);
  pinMode(PIN_VALVE, OUTPUT); // Set pin 10 sebagai output
  
  // Konfigurasi masing-masing channel ADS1115
  configureADS1115(ADS1115_ADDRESS_1);
  configureADS1115(ADS1115_ADDRESS_2);
  configureADS1115(ADS1115_ADDRESS_3);
  configureADS1115(ADS1115_ADDRESS_4);
}

void loop() {
  handleValve();
  sampleSerial();
  if(isSampling) sampling();
}

void configureADS1115(uint8_t address) {
  for (int channel = 0; channel < 4; channel++) {
    uint16_t config = 0x8583 | (channel << 12); // Konfigurasi default, bisa diubah sesuai kebutuhan
    Wire.beginTransmission(address);
    Wire.write(ADS1115_REG_CONFIG);
    Wire.write(config >> 8);
    Wire.write(config & 0xFF);
    Wire.endTransmission();
  }
}

int16_t readADS1115(uint8_t address, uint8_t channel) {
  uint16_t config = 0x8583 | (channel << 12); // Konfigurasi untuk masing-masing channel
  Wire.beginTransmission(address);
  Wire.write(ADS1115_REG_CONFIG);
  Wire.write(config >> 8);
  Wire.write(config & 0xFF);
  Wire.endTransmission();
  
  delay(10); // Tunggu konversi selesai

  Wire.beginTransmission(address);
  Wire.write(ADS1115_REG_CONVERT);
  Wire.endTransmission();

  Wire.requestFrom(address, (uint8_t)2);
  int16_t result = Wire.read() << 8;
  result |= Wire.read();

  return result;
}

void handleValve() {
  unsigned long currentMillis = millis(); // Mendapatkan waktu sekarang

  // Cek apakah waktunya untuk mengubah status pin 10
  if (isHigh && currentMillis - previousMillis >= intervalHigh) {
    // Ubah ke LOW setelah 1 detik
    digitalWrite(PIN_VALVE, LOW);
    isHigh = false;
    previousMillis = currentMillis;  // reset waktu sebelumnya
  } 
  else if (!isHigh && currentMillis - previousMillis >= intervalLow) {
    // Ubah ke HIGH setelah 3 detik
    digitalWrite(PIN_VALVE, HIGH);
    isHigh = true;
    previousMillis = currentMillis;  // reset waktu sebelumnya
    
    // Send a signal to Python script when solenoid is HIGH
    Serial.println('S');  // Send 'S' command
  }
}

void sampling() {
  //  Serial.print("Atas:"); 
  //  Serial.print(30000); Serial.print(",");
  //  Serial.print("Bawah:"); 
  //  Serial.print(-30000); Serial.print(",");
  
  // Baca data dari masing-masing channel pada ADS1115 pertama (board R)
  int16_t value_1_A0 = readADS1115(ADS1115_ADDRESS_1, 0);
  int16_t value_1_A1 = readADS1115(ADS1115_ADDRESS_1, 1);

  //  Serial.print("TGS2600:"); 
  Serial.print(value_1_A0); Serial.print(",");
  //  Serial.print("TGS2602:"); 
  Serial.print(value_1_A1); Serial.print(",");

  // Baca data dari masing-masing channel pada ADS1115 kedua (board R)
  int16_t value_2_A1 = readADS1115(ADS1115_ADDRESS_2, 1);
  int16_t value_2_A2 = readADS1115(ADS1115_ADDRESS_2, 2);
  int16_t value_2_A3 = readADS1115(ADS1115_ADDRESS_2, 3);

  //  Serial.print("TGS816:"); 
  Serial.print(value_2_A1); Serial.print(",");
  //  Serial.print("TGS813:");
  Serial.print(value_2_A2); Serial.print(",");
  //  Serial.print("MQ8:"); 
  Serial.print(value_2_A3); Serial.print(",");

  // Baca data dari masing-masing channel pada ADS1115 ketiga (board L)
  int16_t value_3_A0 = readADS1115(ADS1115_ADDRESS_3, 0);
  int16_t value_3_A1 = readADS1115(ADS1115_ADDRESS_3, 1);

  //  Serial.print("TGS2611:"); 
  Serial.print(value_3_A0); Serial.print(",");
  //  Serial.print("TGS2620:"); 
  Serial.print(value_3_A1); Serial.print(",");

  // Baca data dari masing-masing channel pada ADS1115 keempat (board L)
  int16_t value_4_A1 = readADS1115(ADS1115_ADDRESS_4, 1);
  int16_t value_4_A2 = readADS1115(ADS1115_ADDRESS_4, 2);
  int16_t value_4_A3 = readADS1115(ADS1115_ADDRESS_4, 3);

  //  Serial.print("TGS822:"); 
  Serial.print(value_4_A1); Serial.print(",");
  //  Serial.print("MQ135:"); 
  Serial.print(value_4_A2); Serial.print(",");
  //  Serial.print("MQ3:");
  Serial.println(value_4_A3);

  delay(SAMPLE_DELAY_TIME); // Bisa disesuaikan
}

void sampleSerial(){
  while(Serial.available() > 0){
    char recv = Serial.read();

    if(recv == '\n'){
      parseCommand(serialRecv);

      serialRecv = "";
    } 
    else {
      serialRecv += recv;
    }
  }
}

void parseMessage(String message){
  int command = -1;
  int value = -1;

  memcpy(&command, message[0], sizeof(int));
  memcpy(&value, message[4], sizeof(int));

  switch (command)
  {
  case command_t::START_SAMPLING :
    isSampling = true;
    break;

  case command_t::STOP_SAMPLING :
    isSampling = false;
    break;

  case command_t::SET_INHALE :
    intervalHigh = value;
    break;
  
  case command_t::SET_INHALE :
    intervalLow = value;
    break;
  
  default:
    break;
  }
}