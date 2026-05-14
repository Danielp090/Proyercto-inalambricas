#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// --- CONFIGURACIÓN ---
const char* ssid = "Martin Peralta";
const char* password = "Mar7o10.21.";
const char* serverUrl = "http://192.168.1.XX:8000/api/transaccion"; 

// --- PINES (Configuración image_ce2957.jpg) ---
#define SCK_PIN   4
#define MISO_PIN  5
#define MOSI_PIN  6
#define SS_PIN    7
#define RST_PIN   3
#define PIN_BOTON 1

MFRC522 mfrc522(SS_PIN, RST_PIN);

// --- ESTADOS ---
bool modoRecarga = false; 
int ultimoEstadoBoton = HIGH; // Para lógica Pull-Up

void setup() {
  Serial.begin(115200);
  
  // Inicialización de periféricos
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN); 
  mfrc522.PCD_Init();
  pinMode(PIN_BOTON, INPUT_PULLUP);

  // Conexión a la red
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ Conectado. Esperando tarjetas...");
}

void loop() {
  // 1. GESTIÓN DEL BOTÓN (Cambio de modo)
  int lecturaBoton = digitalRead(PIN_BOTON);
  if (lecturaBoton == LOW && ultimoEstadoBoton == HIGH) {
    modoRecarga = !modoRecarga;
    Serial.println("--------------------------------");
    Serial.println(modoRecarga ? ">>> MODO: RECARGA ($1.00)" : ">>> MODO: COBRO ($0.35)");
    Serial.println("--------------------------------");
    delay(300); // Evita rebotes mecánicos
  }
  ultimoEstadoBoton = lecturaBoton;

  // 2. GESTIÓN DEL LECTOR RFID
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  // Obtener UID
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    uid += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();

  // Definir acción
  float monto = modoRecarga ? 1.00 : 0.35;
  String tipo = modoRecarga ? "recarga" : "cobro";

  Serial.printf("Tarjeta: %s | Acción: %s\n", uid.c_str(), tipo.c_str());

  // 3. ENVÍO AL SERVIDOR
  enviarAlBackend(uid, tipo, monto);

  // Pausa para evitar lecturas dobles
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
}

void enviarAlBackend(String uid, String accion, float monto) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Construcción del JSON
    StaticJsonDocument<128> doc;
    doc["uid"] = uid;
    doc["accion"] = accion;
    doc["monto"] = monto;

    String jsonPayload;
    serializeJson(doc, jsonPayload);

    int httpCode = http.POST(jsonPayload);
    
    if (httpCode > 0) {
      Serial.printf("Respuesta servidor: %d\n", httpCode);
    } else {
      Serial.printf("Error de conexión: %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();
  }
}