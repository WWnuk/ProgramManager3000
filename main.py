#:kivy 2.1.0

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.properties import NumericProperty
import sqlite3
import yaml
Builder.load_file('.\gui.kv')

# Declare both screens
class MainScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.all_textinputs = []
        self.all_checkboxes = []
        self.all_buttons = []


    def edit_row(self, instance):
        print('click')
        

    def get_search_results_from_database(self):
        
        for textinput in self.all_textinputs:
            self.ids.search_result_id.remove_widget(textinput)

        for checkbox in self.all_checkboxes:
            self.ids.search_result_id.remove_widget(checkbox)

        for button in self.all_buttons:
            self.ids.search_result_id.remove_widget(button)

        self.all_textinputs.clear()
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
            column_names = list(map(lambda x: x[0], cursor.description))

            for column_data in data_returned_from_query:
                yaml_formatted = {column_names[0]: column_data[0],
                                  column_names[1]: column_data[1],
                                  column_names[2]: column_data[2],
                                  column_names[3]: column_data[3],
                                  column_names[4]: column_data[4],
                                  column_names[5]: column_data[5]}
                converted_to_yaml = yaml.dump(yaml_formatted, sort_keys = False)



                textinput = Label(font_size = '15sp', size_hint_x = 0.8, text = str(converted_to_yaml))
                checkbox = CheckBox(size_hint_x = 0.1)
                button_in_box_layout = BoxLayout(orientation = 'vertical', size_hint_x = 0.1)
                button_in_box_layout.add_widget(Label(text = ''))
                button_in_box_layout.add_widget(Button(text = 'Edit row!', on_press = self.edit_row))
                button_in_box_layout.add_widget(Label(text = ''))


                self.all_textinputs.append(textinput)
                self.all_checkboxes.append(checkbox)
                self.all_buttons.append(button_in_box_layout)

                self.ids.search_result_id.add_widget(textinput)
                self.ids.search_result_id.add_widget(checkbox)
                self.ids.search_result_id.add_widget(button_in_box_layout)
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
    