from mycroft import MycroftSkill, intent_file_handler
from mycroft.util import get_ipc_directory
from alsaaudio import Mixer
import io
import os
import os.path

   # Monitor IPC file containing microphone level info
   #   start_mic_monitor(os.path.join(get_ipc_directory(), "mic_level"))


  
class AutoSetVolume(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.filename = os.path.join(get_ipc_directory(), "mic_level")
        self.level = 25
        self.mixer = Mixer()
        auto_set_volume()


    @intent_file_handler('volume.set.auto.intent')
    def handle_volume_set_auto(self, message):
        self.speak_dialog('volume.set.auto')

def auto_set_volume():
    global meter_cur
    global meter_thresh
    mixer = Mixer()
    with io.open(os.path.join(get_ipc_directory(), "mic_level"), 'r') as fh:
        fh.seek(0)
        while True:
            line = fh.readline()
            if line == "":
                break

            # Just adjust meter settings
            # Ex:Energy:  cur=4 thresh=1.5
            parts = line.split("=")
            meter_thresh = float(parts[-1])
            meter_cur = float(parts[-2].split(" ")[0])
            if int(meter_thresh) > 10:
                mixer.setvolume(74)
            if int(meter_thresh) < 10:
                mixer.setvolume(25)
            

        
        


def create_skill():
    return AutoSetVolume()

