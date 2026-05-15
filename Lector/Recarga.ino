#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

#define RST_PIN   3
#define SS_PIN    7
#define SCK_PIN   4
#define MISO_PIN  5
#define MOSI_PIN  6

MFRC522 rfid(SS_PIN, RST_PIN);

const char* ssid = "Red_Home";
const char* password = "Red_5egura";
const char* serverUrl = "https://apibuses.fmliagarzon.duckdns.org:4443/api/transaccion";

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n INICIANDO PUNTO DE RECARGA");

  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, SS_PIN); 
  rfid.PCD_Init();
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n Terminal de Recarga Online");
  Serial.println("ESPERANDO TARJETA PARA RECARGA");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) return;

  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;

  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    uid += String(rfid.uid.uidByte[i] < 0x10 ? "0" : "");
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();

  Serial.println("\n Procesando Recarga para: " + uid);
  enviarPeticion(uid, "recarga", 1.00);

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
  delay(3000); 
}

void enviarPeticion(String uid, String accion, float monto) {
  WiFiClientSecure *client = new WiFiClientSecure;
  client->setInsecure();
  
  HTTPClient http;
  if (http.begin(*client, serverUrl)) {
    http.addHeader("Content-Type", "application/json");
    String json = "{\"uid\":\"" + uid + "\", \"accion\":\"" + accion + "\", \"monto\":" + String(monto) + "}";
    
    int httpCode = http.POST(json);
    if (httpCode > 0) {
      Serial.println(" Servidor: " + http.getString());
      Serial.println("RECARGA EXITOSA");
    } else {
      Serial.printf(" Error: %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();
  }
  delete client;
}