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
from pycube90 import Cube
#import android

#class CubeSMS(BoxLayout):

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


class CubeSMS(App):
        def __init__(self):
                num = "3854991198"
                droid = android.Android()
                droid.smsSend(num,"Hello sucker")
     
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
     
	def sendsms(self):
                num = "3854991198"
                #droid = android.Android()
                #droid.smsSend(num,"Hello sucker")


if __name__ == '__main__':
     CubeSMS().run()
