from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.audio import SoundLoader
from MorseStation import MorseStation
from pycube import Cube, CubeKDF

class StationM(App):
    tmpfile = "tmpfile.wav"
    frequency = 1000
    wpm = 18
    last_msg = ""
    encrypt = False
    key = ""

    def normalize(self, data):
        result = "".join(data.split()).upper()
        return result.encode('ascii')

    def on_pause(self):
        text = self.input
        key = self.key
        num = self.recipient
        return True

    def on_resume(self):
        self.input = text
        self.key = key
        self.recipient = num

    def on_enter(self, instance, value):
        print value

    def set_filename(self, instance, value):
        self.filename = value
    
    def set_freq(self, instance, value):
        try:
            self.frequency = int(value)
        except ValueError as ver:
            pass
    
    def set_wpm(self, instance, value):
        try:
            self.wpm = int(value)
        except ValueError as ver:
            pass

    def set_key(self, instance, value):
        self.key = value

    def on_text(self, instance, value):
        self.input = value
    
    def build(self):
        self.icon = 'logo2.png'
        self.layout = BoxLayout(orientation='vertical')
        blue = (0, 0, 1.5, 2.5)
        red = (2.5, 0, 0, 1.5)
        self.texttitle = Label(text='Text input:', valign='top', halign='center', font_size='12sp')
        self.btn = Button(text='Play Message', background_color=red, pos=(5,20), size_hint=(1, 1))
        self.btn.bind(on_release=self.playmsg)
        self.texttitle = Label(text='Key input:', valign='top', halign='center', font_size='12sp')
        self.btn = Button(text='Play Message', background_color=red, pos=(5,20), size_hint=(1, 1))
        self.btn.bind(on_release=self.playmsg)
        self.btn2 = Button(text='Play Encrypted Message', background_color=red, pos=(5,20), size_hint=(1, 1))
        self.btn2.bind(on_release=self.encryptmsg)
        self.filename_box = TextInput(multiline=False, size_hint=(.5, .4), height='30', halign='center')
        self.input_box = TextInput(multiline=True, height='50', size_hint=(.8,.8))
        self.input_box.bind(text=self.on_text)
        self.input_box.bind(on_text_validate=self.on_enter)
        self.keybox = TextInput(password=True, multiline=False, size_hint=(.5, .4), height='30', halign='center')
        self.keybox.bind(text=self.set_key)
        self.freqbox = TextInput(multiline=False, size_hint=(.5, .4), height='30', halign='center')
        self.freqbox.bind(text=self.set_freq)
        self.wpmbox = TextInput(multiline=False, size_hint=(.5, .4), height='30', halign='center')
        self.wpmbox.bind(text=self.set_wpm)
        self.layout.add_widget(self.texttitle)
        self.layout.add_widget(self.input_box)
        self.layout.add_widget(self.btn)
        self.layout.add_widget(self.keybox)
        self.layout.add_widget(self.btn2)
        self.layout.add_widget(self.freqbox)
        self.layout.add_widget(self.wpmbox)
        self.key = ""
        self.key_length = 16
        self.nonce_length = 8
	return self.layout

    def show_key(self, event):
        if self.keybox.password == True:
            self.keybox.password = False
        else:
            self.keybox.password = True
    
    def encryptmsg(self, event):
        data = self.normalize(self.input)
        if data != self.last_msg and len(self.last_msg) != 0:
            MorseStation(self.frequency, self.wpm).transmit(ctxt, self.tmpfile)
        key = CubeKDF().genkey(self.normalize(self.key))
        ctxt = Cube(key).encrypt(data)
        pop = Popup(title='Playing', content=Label(text=ctxt), size_hint=(None, None))
        pop.open()
        sound = SoundLoader.load(self.tmpfile)
        if sound:
            sound.play()
            self.last_msg = data

    def playmsg(self, event):
        data = self.normalize(self.input)
        if data != self.last_msg and len(self.last_msg) != 0:
            MorseStation(self.frequency, self.wpm).transmit(data, self.tmpfile)
        pop = Popup(title='Playing', content=Label(text=data), size_hint=(None, None))
        pop.open()
        sound = SoundLoader.load(self.tmpfile)
        if sound:
            sound.play()
            self.last_msg = data

if __name__ == '__main__':
     StationM().run()
