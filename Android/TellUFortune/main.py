from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
import socket

class FortuneClient(BoxLayout):

     #pressed = ListProperty([0, 0])

     #def on_touch_down(self, touch):
     #    if self.collide_point(*touch.pos):
     #        self.pressed = touch.pos
     #         #we consumed the touch. return False here to propagate
     #        # the touch further to the children.
     #        return True
     #    return super(FortuneClient, self).on_touch_down(touch)

     #def on_pressed(self, instance, pos):
     #	response = get_fortune()
	#root = FortuneWidget()
#	fortune = Label(text='[b]' + response + '[/b]', markup=True)
#	print response
	#fortune = Popup(title="FORTUNE",content=Label(text=response))
	#fortune.open()
#	return Label(text=response)

     def get_fortune():
	host = "thrash.hacked.jp"
	port = 34568
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host, port))
	except socket.error as ser:
		pass
	response = s.recv(1024)
	s.close()
	return

class TellUFortune(App):
     
	def build(self):
		layout = BoxLayout(orientation='vertical')
		blue = (0, 0, 1.5, 2.5)
		red = (2.5, 0, 0, 1.5)

		btn = Button(text='Get Fortune', background_color=blue, font_size=40)

		btn.bind(on_press=self.get_fortune)
		self.label = Label(text="-", font_size='10sp')
		#self.fortune = Popup(title="Fortune", content=Label(text="-", font_size='12sp'), size=(400,400))
		layout.add_widget(btn)
		layout.add_widget(self.label)
		return layout
     
	def get_fortune(self, event):
		host = "thrash.hacked.jp"
		port = 34568
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host, port))
		response = s.recv(1024)
		self.label.text = response
		s.close()
		return response


if __name__ == '__main__':
     TellUFortune().run()
