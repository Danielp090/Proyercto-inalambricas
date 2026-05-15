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
  Serial.println("\n INICIANDO UNIDAD DE COBRO");

  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, SS_PIN); 
  rfid.PCD_Init();
  Serial.println("1. Hardware RFID");

  WiFi.begin(ssid, password);
  Serial.print("2. Conectando a Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n Wi-Fi Conectado.");
  Serial.println("ESPERANDO TARJETA PARA COBRO");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.reconnect();
    delay(2000);
    return;
  }

  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;

  Serial.println("\n Tarjeta detectada...");
  
  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    uid += String(rfid.uid.uidByte[i] < 0x10 ? "0" : "");
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();
  Serial.println("UID: " + uid);

  enviarPeticion(uid, "cobro", 0.35);

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
  delay(2500); 
}

void enviarPeticion(String uid, String accion, float monto) {
  WiFiClientSecure *client = new WiFiClientSecure;
  client->setInsecure(); 
  
  HTTPClient http;
  if (http.begin(*client, serverUrl)) {
    http.addHeader("Content-Type", "application/json");

    String json = "{\"uid\":\"" + uid + "\", \"accion\":\"" + accion + "\", \"monto\":" + String(monto) + "}";
    int httpResponseCode = http.POST(json);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Servidor: " + response);
      
      response.toLowerCase();
      if (response.indexOf("rechazado") != -1) {
        Serial.println("SALDO INSUFICIENTE");
      } else {
        Serial.println("Pasaje cobrado.");
      }
    } else {
      Serial.printf(" Error HTTPS: %s\n", http.errorToString(httpResponseCode).c_str());
    }
    http.end();
  }
  delete client;
}