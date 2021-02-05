/*  This sketch sends a message to a TCP server
 *
 */

#include <WiFi.h>
#include <WiFiMulti.h>

WiFiMulti WiFiMulti;

#include <WiFi.h>

const char* ssid     = "name";
const char* password = "passpasspass";
const char* host = "192.168.1.77";
const uint16_t port = 5050;


void setup()
{
    Serial.begin(115200);
    delay(10);

    // We start by connecting to a WiFi network
    WiFiMulti.addAP(ssid, password);

    Serial.println();
    Serial.println();
    Serial.print("Waiting for WiFi... ");

    while(WiFiMulti.run() != WL_CONNECTED) {
        Serial.print(".");
        delay(500);
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());

    delay(500);
}


void loop()
{
    Serial.print("Connecting to ");
    Serial.println(host);

    // Use WiFiClient class to create TCP connections
    WiFiClient client;

    if (!client.connect(host, port)) {
        Serial.println("Connection failed.");
        Serial.println("Waiting 5 seconds before retrying...");
        delay(5000);
        return;
    }
  
    client.print("   6"); // message length as a 4 byte str
    client.print("001,23");
    Serial.println("Sent msg to server");
    Serial.println("Closing connection.");
    client.stop();

    Serial.println("Waiting 5 seconds before restarting...");
    delay(5000);
}
