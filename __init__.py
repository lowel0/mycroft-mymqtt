# Revised from "git clone https://github.com/jamiehoward430/mycroft-mymqtt.git"

from os.path import dirname
from os import uname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

import paho.mqtt.client as mqtt

__author__ = 'lowel'

LOGGER = getLogger(__name__)

class mymqttskill(MycroftSkill):

    def __init__(self):
        super(mymqttskill, self).__init__(name="mymqttskill")
       
        self.protocol = self.config["protocol"]
	self.mqttssl = self.config["mqtt-ssl"]
	self.mqttca = self.config["mqtt-ca-cert"]
	self.mqtthost = self.config["mqtt-host"]
	self.mqttport = self.config["mqtt-port"]
	self.mqttauth = self.config["mqtt-auth"]
	self.mqttuser = self.config["mqtt-user"]
	self.mqttpass = self.config["mqtt-pass"]
 
    
    def initialize(self):
        self.load_data_files(dirname(__file__))
        self. __build_single_command()
        
        
    def __build_single_command(self):
        intent = IntentBuilder("mymqttIntent").require("CommandKeyword").require("ModuleKeyword").require("ActionKeyword").build()
        self.register_intent(intent, self.handle_single_command)
        
    def handle_single_command(self, message):
        cmd_name = message.data.get("CommandKeyword")
        mdl_name = message.data.get("ModuleKeyword")
        act_name = message.data.get("ActionKeyword")
        dev_name = mdl_name.replace(' ', '_').replace("'s", "")
        
        if (dev_name.find("light") < 0):
            cmd = cmd_name + "/" + dev_name
        else:
            cmd = dev_name
        if (cmd == "light"):
            hostName = uname()[1]
            if (hostName == "picroft-rmo"):
                cmd = "living_room_light"
            elif (hostName == "picroft-ao"):
                cmd = "alexia_light"
            elif (hostName == "picroft-so"):
                cmd = "chelsea_light"
            elif (hostName == "emoncms"):
                cmd = "living_room_light"
        if (self.protocol == "mqtt"):
            mqttc = mqtt.Client("MycroftAI")
            if (self.mqttauth == "yes"):
                mqttc.username_pw_set(self.mqttuser,self.mqttpass)
            if (self.mqttssl == "yes"):
                mqttc.tls_set(self.mqttca) #/etc/ssl/certs/ca-certificates.crt
            mqttc.connect(self.mqtthost, self.mqttport)
            mqttc.publish("mycroft/" + cmd, act_name)
            mqttc.disconnect()
            self.speak_dialog("cmd.sent")
            LOGGER.info(cmd + "," + act_name)
        else:
            self.speak_dialog("not.found", {"command": cmd_name, "action": act_name, "module": dev_name})
            LOGGER.error("Error: {0}".format(e))
        
    def stop(self):
        pass
        
def create_skill():
    return mymqttskill()
