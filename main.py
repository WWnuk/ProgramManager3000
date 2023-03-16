#:kivy 2.1.0

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.properties import NumericProperty
import sqlite3

Builder.load_file('.\gui.kv')

# Declare both screens
class MainScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.all_columns = []
        

    def get_search_results_from_database(self):
        print(self.ids.search_field_id.text)
        try:
            sqlite_connection = sqlite3.connect('.\programs.db')
            cursor = sqlite_connection.cursor()
            if self.ids.search_field_id.text == '':
               cursor.execute('SELECT * FROM ProgramManager3000')
            else:
                cursor.execute('SELECT * FROM ProgramManager3000 WHERE name LIKE "%' + self.ids.search_field_id.text + '%"')
            data_returned_from_query = cursor.fetchall()
            for tuple in data_returned_from_query:
                self.ids.search_result_id.add_widget(Label(text = str(tuple[0]), font_size = '15sp', shorten = True, text_size = (60,30)))
                self.ids.search_result_id.add_widget(Label(text = str(tuple[1]), font_size = '15sp', shorten = True, text_size = (60,30)))
                self.ids.search_result_id.add_widget(Label(text = str(tuple[2]), font_size = '15sp', shorten = True, text_size = (60,30)))
                self.ids.search_result_id.add_widget(Label(text = str(tuple[3]), font_size = '15sp', shorten = True, text_size = (60,30)))
                self.ids.search_result_id.add_widget(Label(text = str(tuple[4]), font_size = '15sp', shorten = True, text_size = (60,30)))
                self.ids.search_result_id.add_widget(Label(text = str(tuple[5]), font_size = '15sp', shorten = True, text_size = (60,30)))
                self.ids.search_result_id.add_widget(CheckBox())
                self.ids.search_result_id.add_widget(Button(text = 'Edit row!'))
            cursor.close()

        except sqlite3.Error as error:
            print('Error during database communication. ', error)



    def add_row(self):
        self.ids.search_result_id.add_widget(Label(text = 'labvvvsvsdvdgdydfthyfthftyftyftyvvvelh', font_size = '20sp', shorten = True, text_size = (60,30)))
        self.ids.search_result_id.add_widget(Label(text = 'label', font_size = '20sp'))
        self.ids.search_result_id.add_widget(Label(text = 'label', font_size = '20sp'))
        self.ids.search_result_id.add_widget(Label(text = 'label', font_size = '20sp'))
        self.ids.search_result_id.add_widget(Label(text = 'label', font_size = '20sp'))

        self.ids.search_result_id.add_widget(CheckBox())
        self.ids.search_result_id.add_widget(Button(text = 'Edit row!'))
class SettingsScreen(Screen):
    pass



class TestApp(App):

    def build(self):
        # Create the screen manager

        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SettingsScreen(name='settings'))

        return sm

if __name__ == '__main__':
    TestApp().run()
    