from mycroft import MycroftSkill, intent_file_handler
from mycroft.util import get_ipc_directory
#from mycroft.util import wait_while_speaking
from mycroft.audio import wait_while_speaking
from mycroft.skills.audioservice import AudioService
from alsaaudio import Mixer
import io
import os
import os.path

 
class AutoSetVolume(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
    
    def initialize(self):
        self.filename = os.path.join(get_ipc_directory(), "mic_level")
        self.audio_service = AudioService(self.bus)
        self.mixer = Mixer()
        self.schedule_repeating_event(self.auto_set_volume, None,15, 'AutoSetVolume')

        if self.settings.get('High volume') == None:
            self.settings['High volume'] = 75
        if self.settings.get('Normal volume') == None:
            self.settings['Normal volume'] = 60
        if self.settings.get('Low volume') == None:
            self.settings['Low volume'] = 35
                   

    @intent_file_handler('volume.set.auto.intent')
    def handle_volume_set_auto(self, message):
        self.speak_dialog('volume.set.auto')

    @intent_file_handler('reset.intent')
    def handle_volume_set_auto(self, message):
        timeout = time.time() + 60*1   # 5 minutes from now
        self.speak_dialog('messure.lowlevel')
        while True:
            if time.time() > timeout:
                break
                with io.open(self.filename, 'r') as fh:
                    #fh.seek(0)
                    meter_thresh = 0
                    while True:
                        line = fh.readline()
                        if line == "":
                            break
                        # Ex:Energy:  cur=4 thresh=1.5
                        parts = line.split("=")
                        meter_thresh = (meter_thresh + int(float(parts[-1]))) /2
        self.settings['LowNoice'] = meter_thresh
        self.speak_dialog('messure.ok')  
        
        self.speak_dialog('messure.highlevel')
        while True:
            if time.time() > timeout:
                break
                with io.open(self.filename, 'r') as fh:
                    #fh.seek(0)
                    meter_thresh = 0
                    while True:
                        line = fh.readline()
                        if line == "":
                            break
                        # Ex:Energy:  cur=4 thresh=1.5
                        parts = line.split("=")
                        meter_thresh = (meter_thresh + int(float(parts[-1]))) /2
        self.settings['HighNoice'] = meter_thresh
        self.speak_dialog('messure.ok')  


    def auto_set_volume(self, message):
        wait_while_speaking()
        #global meter_thresh
        
        with io.open(self.filename, 'r') as fh:
            #fh.seek(0)
            while True:
                line = fh.readline()
                if line == "":
                    break

                # Ex:Energy:  cur=4 thresh=1.5
                parts = line.split("=")
                meter_thresh = int(float(parts[-1]))
                #meter_cur = float(parts[-2].split(" ")[0])
                
            #    # Store the thresh level
            #    if self.settings.get('HighNoice') == None:
            #        self.settings['HighNoice'] = meter_thresh
            #    if self.settings.get('LowNoice') == None:
            #        self.settings['LowNoice'] = meter_thresh
                
            #    if meter_thresh > self.settings.get('HighNoice'):
            #        self.settings['HighNoice'] = meter_thresh
            #    elif meter_thresh < self.settings.get('LowNoice'):
            #        self.settings['LowNoice'] = meter_thresh
                
                # Calculate high and low levels
                # return 100 * float(part)/float(whole)
                #  return (percent * whole) / 100.0
                range = self.settings.get('HighNoice') - self.settings.get('LowNoice')
                lowlevel = self.settings.get('LowNoice') + int((10 * range) / 100)
                highlevel = self.settings.get('HighNoice') - int((20 * range) /100)
            #    self.log.info("LovNoice: " + str(self.settings.get('LowNoice')) + 
            #                  " LowLevel: " + str(lowlevel) + 
            #                  " HighNoice :" + str(self.settings.get('HighNoice')) + 
            #                  " HighLevel: " + str(highlevel))

                if not self.audio_service.is_playing:
                    volume = 50
                    if meter_thresh > highlevel:
                        volume = self.settings.get('High volume')
                    if meter_thresh < lowlevel:
                        volume = self.settings.get('Low volume')
                    if meter_thresh < highlevel and meter_thresh > lowlevel:
                        volume = self.settings.get('Normal volume')
                    self.log.info("Mesure mic: " + str(meter_thresh) + " Setting volume to :" + str(volume) + "%")
                    #self.log.info(line)
                    self.mixer.setvolume(volume)

                
            
def create_skill():
    return AutoSetVolume()

