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
        self.all_labels = []
        self.all_checkboxes = []
        self.all_buttons = []


    def edit_row(self, instance):
        print('click')
        

    def get_search_results_from_database(self):
        
        for label in self.all_labels:
            self.ids.search_result_id.remove_widget(label)

        for checkbox in self.all_checkboxes:
            self.ids.search_result_id.remove_widget(checkbox)

        for button in self.all_buttons:
            self.ids.search_result_id.remove_widget(button)

        self.all_labels.clear()
        self.all_checkboxes.clear()
        self.all_buttons.clear()


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
                label = Label(text = str(tuple[0]) + str(tuple[1]) + str(tuple[2]) + str(tuple[3]) + str(tuple[4]),
                               font_size = '15sp', text_size = (600, 50), size_hint_x = 0.8)
                checkbox = CheckBox(size_hint_x = 0.1)
                button = Button(text = 'Edit row!', size_hint_x = 0.1, on_press = self.edit_row)

                self.all_labels.append(label)
                self.all_checkboxes.append(checkbox)
                self.all_buttons.append(button)

                self.ids.search_result_id.add_widget(label)
                self.ids.search_result_id.add_widget(checkbox)
                self.ids.search_result_id.add_widget(button)
            cursor.close()

        except sqlite3.Error as error:
            print('Error during database communication. ', error)

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
    