from decimal import Decimal
import RPi.GPIO as GPIO
import PCF8591 as ADC
import math
import requests
import time
import LCD1602 as LCD
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

GPIO.setmode(GPIO.BOARD)
myMQTTClient = AWSIoTMQTTClient("RishabClientID") #random key, if another connection using the same key is opened the previous one is auto closed by AWS IOT
myMQTTClient.configureEndpoint("a1l83aslu1wtwg-ats.iot.us-east-1.amazonaws.com", 8883)

myMQTTClient.configureCredentials("/home/pi/AWSIoT/root-ca.pem", "/home/pi/AWSIoT/private.pem.key", "/home/pi/AWSIoT/certificate.pem.crt")

myMQTTClient.configureOfflinePublishQueueing(-1) # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2) # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10) # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5) # 5 sec
print ('Initiating Realtime Data Transfer From Raspberry Pi...')
myMQTTClient.connect()

def setup():
    ADC.setup(0x48)
    GPIO.setup(11, GPIO.IN)
    LCD.init(0x27, 1)

def loop():
    while True:
        analogVal = ADC.read(0)
        Vr = 5 * float(analogVal) / 255
        Rt = 10000 * Vr / (5 - Vr)
        temperature = 1 / (((math.log(Rt / 10000)) / 3950) + (1 / (273.15 + 25)))
        temperature = (temperature - 273.15)
        temperature = round(temperature, 1)
        fahrenheit = ((temperature*1.8)+32)
        LCD.write(0,0, 'Temp: {} F'.format(fahrenheit)+'        ')
        time.sleep(.5)
        print("Sending Temperature: ", fahrenheit)


        myMQTTClient.publish(
            topic="RealTimeDataTrasfer/Temperature",
            QoS=1,
            payload='{"Temperature":"'+str(fahrenheit)+'"}')

if __name__ == '__main__':
    try:
        setup()
        loop()
    except KeyboardInterrupt:
        pass

    
