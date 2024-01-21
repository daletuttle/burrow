import Burrow, schedule
import MQTTlistener
import houseMQTT
from libraries import loggerdo, utils
import datetime
import time
import control
import threading
import alerts
import base64
import meross


def run():

    while True:
        # update
        dayschedule.checkvalid()
        # Run eval before updates
        burrow.eval()
        time.sleep(3)


def runmqttlistenbroker():
    mqttlistener.run()

def runmqttthermometerbroker():
    mqttthermometer.run()

def makebase64(file):
    with open(file, 'rb') as binary_file:

        binary_file_data = binary_file.read()
        base64_encoded_data = base64.b64encode(binary_file_data)
        base64_message = base64_encoded_data.decode('utf-8')
        return base64_message

def updateschedule(direction):
    now = datetime.datetime.now()
    thishour = now.hour
    tophour = thishour + 2

    while thishour <= tophour:
        if thishour > 23.5:
            break
        if direction:
            dayschedule.increment(now)
            if test:
                loggerdo.log.info("checking schedule")

                base, high, low = dayschedule.pullhourdetails(now)

                loggerdo.log.info("Low = {} and High = {}".format(low, high))
        else:
            dayschedule.decrement(now)
            if test:
                loggerdo.log.info("checking schedule")
                base, high, low = dayschedule.pullhourdetails(now)
                loggerdo.log.info("Low = {} and High = {}".format(low, high))

        now = now + datetime.timedelta(minutes=30)
        thishour += 0.5


def printhome():
    ltempf, htempf = ourhome.getroomtemplimit()
    print ("Low temp - {} High temp - {}".format(ltempf, htempf))
    outtemplimitf = ourhome.getoutsidetemplimit()
    print("Outside temp limit - {}".format(outtemplimitf))
    nightstart, nightend = ourhome.getnightschedule()
    print("Night start - {} Night end - {}".format(nightstart, nightend))

def runmeross(switches, mqttserver):
    merossswitcharray = []

    for switch in switches:
        merossswitcharray.append(meross.merossswitch(IP=switches[switch]['ip'], Name=switches[switch]['name'],
                                            mqttserver=mqttserver, managed=True,
                                            zone=0, AC=False))
    while True:
        for msw in merossswitcharray:
            ret=msw.getstate()
        time.sleep(10)

def main(importedconfig):
    global config, test
    global ourhome, dayschedule, burrow, mqttlistener, mqttthermometer

    config = importedconfig

    test = config["test"]

    myclient = None

    ealert = alerts.prevere(config)

    ourhome = houseMQTT.home(config, ealert)

    dayschedule = schedule.day(config)

    burrow = Burrow.Burrow(ourhome, dayschedule, config, ealert)

  
    mqttlistener = MQTTlistener.broker(mqttconfig=config["MQTT"], house=ourhome, burrow=burrow, schedule=dayschedule,
                               config=config)
    
    mqttthermometer = MQTTlistener.broker(mqttconfig=config["MQTT"], house=ourhome)
    #controlthread = threading.Thread(target=controlchanges)
    #controlthread.setDaemon(True)
    #controlthread.start()

    mqttlistenthread = threading.Thread(target=runmqttlistenbroker)
    mqttlistenthread.setDaemon(True)
    mqttlistenthread.start()

    mqttthermometerthread = threading.Thread(target=runmqttthermometerbroker)
    mqttthermometerthread.setDaemon(True)
    mqttthermometerthread.start()

    run()


if __name__ == "__main__":
    print('needs to be imported to run')
