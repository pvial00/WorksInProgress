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
from plyer import sms
#from pycube90 import Cube
from dh import DHE
from base64 import b64encode, b64decode
from pycube256 import Cube, CubeKDF, CubeRandom

class CubeSMS(App):

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

    def get_num(self, instance, value):
        self.recipient = value

    def on_text(self, instance, value):
        self.input = value
    
    def set_key(self, instance, value):
        self.key = value
    
    def build(self):
        self.icon = 'logo2.png'
        self.layout = BoxLayout(orientation='vertical')
        blue = (0, 0, 1.5, 2.5)
        red = (2.5, 0, 0, 1.5)
        self.numtitle = Label(text='Phone number:', valign='top', halign='center', font_size='12sp')
        self.texttitle = Label(text='Text input:', valign='top', halign='center', font_size='12sp')
        self.keytitle = Label(text='Key:', valign='top', halign='center', font_size='12sp')
        self.btn = Button(text='Send SSMS', background_color=red, pos=(5,20), size_hint=(1, 1))
        self.btn.bind(on_release=self.sendsms)
        self.dbtn = Button(text='Decrypt text', background_color=blue, pos=(5, 5), size_hint=(.5, .5))
        self.dbtn.bind(on_release=self.decrypt)
        self.ebtn = Button(text='Encrypt text', background_color=blue, pos=(0, 10), size_hint=(.5, .5))
        self.ebtn.bind(on_release=self.solo_encrypt)
        self.kbtn = Button(text='Generate key', background_color=blue, pos=(0, 10), size_hint=(.5, .5))
        self.kbtn.bind(on_release=self.gen_key)
        self.sbtn = Button(text='Show key', background_color=blue, pos=(0, 10), size_hint=(.5, .5))
        self.sbtn.bind(on_release=self.show_key)
        self.recipient_box = TextInput(multiline=False, size_hint=(.5, .4), height='30', halign='center')
        self.recipient_box.bind(text=self.get_num)
        self.recipient_box.bind(on_text_validate=self.on_enter)
        self.input_box = TextInput(multiline=True, height='50', size_hint=(.8,.8))
        self.input_box.bind(text=self.on_text)
        self.input_box.bind(on_text_validate=self.on_enter)
        self.key_box = TextInput(password=True, multiline=False, size_hint=(.5, .4), height='30', halign='center')
        self.key_box.bind(text=self.set_key)
        self.layout.add_widget(self.numtitle)
        self.layout.add_widget(self.recipient_box)
        self.layout.add_widget(self.texttitle)
        self.layout.add_widget(self.input_box)
        self.layout.add_widget(self.keytitle)
        self.layout.add_widget(self.key_box)
        self.layout.add_widget(self.btn)
        self.layout.add_widget(self.dbtn)
        self.layout.add_widget(self.ebtn)
        self.layout.add_widget(self.kbtn)
        self.layout.add_widget(self.sbtn)
        self.key = ""
        self.key_length = 16
        self.nonce_length = 8
	return self.layout

    def sendsms(self, event):
        if len(self.recipient) >= 8 and self.key != "" and self.input != "":
            #if len(self.input) <= 105:
            msg = self.encrypt(self.input)
            sms.send(self.recipient, msg)
            #elif len(self.input) > 105:
            #    blocks = []
            #    num_blocks = len(self.input) / 105
            #    extra_block = len(self.input) % 105
            #    if extra_block != 0:
            #        num_block += 1
            #    start_block = 0
            #    end_block = 105
            #    last_block = len(self.input) - extra_block
            #    for x in range(num_blocks):
            #        if start_block != last_block:
            #            block = self.input[start_block:end_block]
            #            response, nonce = self.encrypt(block)
            #            sms.send(self.recipient, nonce+response)
            #            start_block += 105
            #            end_block += 105
            #        else:
            #            block = self.input[start_block:]
            #            response, nonce = self.encrypt(block)
            #            sms.send(self.recipient, nonce+response)
        else:
            pass

    def encrypt(self, data):
        nonce = self.random(self.nonce_length)
        key = CubeKDF().genkey(self.key, length=(self.key_length * 8))
        cipher_text = Cube(key, nonce).encrypt(data)
        msg = nonce + cipher_text
        return b64encode(msg)

    def random(self,length):
        return CubeRandom().random(length)

    def randomint(self):
        return ord(CubeRandom().random(1))

    def gen_key(self, event):
        self.key = self.random(self.key_length)
        self.key_box.text = b64encode(self.key)

    def show_key(self, event):
        if self.key_box.password == True:
            self.key_box.password = False
        else:
            self.key_box.password = True

    def decrypt(self, data):
        if self.key != "" and self.input != "":
            data = b64decode(self.input)
            nonce = data[:self.nonce_length]
            content = data[self.nonce_length:]
            key = CubeKDF().genkey(self.key, length=(self.key_length * 8))
            plain_text = Cube(key, nonce).decrypt(content)
            self.input_box.text = plain_text
            #layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
            #stuff = Label(text='%s' % plain_text, size_hint_y=None, valign='top', halign='center', text_size=(400,200))
            #scroll = ScrollView(size_hint_y=None, text=stuff)
            #stuff.add_widget(scroll)
            #popup = Popup(title='Decrypted Message', content=stuff, size=(100,100))
            #popup.open()

    def solo_encrypt(self, event):
        if self.key != "" and self.input != "":
            ctxt = self.encrypt(self.input)
            self.input_box.text = ctxt

if __name__ == '__main__':
     CubeSMS().run()
