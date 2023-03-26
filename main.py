#:kivy 2.1.0

from kivy.core.window import Window
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.properties import NumericProperty
import sqlite3
import yaml
from yaml.loader import SafeLoader
from functools import partial

Window.size = (1000, 600)





class InvalidIdValueException(Exception):
    def __init__(self):
            super().__init__("You can`t modify 'id' value!")
class InvalidDownloadedValueException(Exception):
    def __init__(self):
            super().__init__("You can`t modify 'downloaded' value!")
class InvalidInstalledValueException(Exception):
    def __init__(self):
            super().__init__("You can`t modify 'installed' value!")      



Builder.load_file('.\gui.kv')


class PopupWindowAdd(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.yaml_formatted = {'name': 'Name of a program',
                               'url':'URL link to program',
                               'install_command':'Program will be installed using this command'}
        self.converted_to_yaml = yaml.dump(self.yaml_formatted, sort_keys=False)
        self.ids.textinput_id.text = self.converted_to_yaml

    def save_changes_to_database(self):
        try:
            self.edited_text_in_yaml = yaml.load(self.ids.textinput_id.text, Loader=SafeLoader)
            print(type(self.edited_text_in_yaml))
            print(self.edited_text_in_yaml)
            sqlite_connection = sqlite3.connect('.\programs.db')
            cursor = sqlite_connection.cursor()
            cursor.execute("""INSERT INTO ProgramManager3000(name,url,install_command,downloaded,installed) VALUES(?,?,?,0,0)""",
                         (self.edited_text_in_yaml['name'], self.edited_text_in_yaml['url'], self.edited_text_in_yaml['install_command']))
            sqlite_connection.commit()
            cursor.close()
        except yaml.YAMLError as error:
            error_popup = Popup(size_hint=(None, None), size=(800, 400), title = 'Error', content = Label(text = 'Error in YAML syntax. Changes are not saved to database.'))
            error_popup.open()
        except KeyError as error:
            error_popup = Popup(size_hint=(None, None), size=(800, 400), title = 'Error', content = Label(text = 'You modifed KEY. Please don`t do that.'))
            error_popup.open()
        except sqlite3.Error as error:
            error_popup = Popup(size_hint=(None, None), size=(800, 400), title = 'Error', content = Label(text = str(error)))
            error_popup.open()





class PopupWindowEdit(Popup):
    def __init__(self, row_id, **kwargs):
        super().__init__(**kwargs)
        self.text_from_row_label = MainScreen.all_textinputs[row_id].text
        self.ids.textinput_id.text = self.text_from_row_label
    def save_changes_to_database(self):
        try:
            self.edited_text_in_yaml = yaml.load(self.ids.textinput_id.text, Loader = SafeLoader)
            self.orginal_text_in_yaml = yaml.load(self.text_from_row_label, Loader = SafeLoader)
            if self.edited_text_in_yaml['id'] != self.orginal_text_in_yaml['id']:
                raise InvalidIdValueException()

            if self.edited_text_in_yaml['downloaded'] != self.orginal_text_in_yaml['downloaded']:
                raise InvalidDownloadedValueException()

            if self.edited_text_in_yaml['installed'] != self.orginal_text_in_yaml['installed']:
                raise InvalidInstalledValueException()

            sqlite_connection = sqlite3.connect('.\programs.db')
            cursor = sqlite_connection.cursor()
            cursor.execute("""UPDATE ProgramManager3000 SET name=?,url=?,install_command=?,downloaded=?,installed=? WHERE id=?""",
                         (self.edited_text_in_yaml['name'], self.edited_text_in_yaml['url'], self.edited_text_in_yaml['install_command'],
                             self.edited_text_in_yaml['downloaded'], self.edited_text_in_yaml['installed'], self.edited_text_in_yaml['id']))
            sqlite_connection.commit()
            cursor.close()
            
        except yaml.YAMLError as error:
            error_popup = Popup(size_hint=(None, None), size=(800, 400), title = 'Error', content = Label(text = 'Error in YAML syntax. Changes are not saved to database.'))
            error_popup.open()
        except KeyError as error:
            error_popup = Popup(size_hint=(None, None), size=(800, 400), title = 'Error', content = Label(text = 'You modifed KEY. Please don`t do that.'))
            error_popup.open()
        except sqlite3.Error as error:
            error_popup = Popup(size_hint=(None, None), size=(800, 400), title = 'Error', content = Label(text = str(error)))
            error_popup.open()
        except InvalidInstalledValueException as error:
            error_popup = Popup(size_hint=(None, None), size=(800, 400), title = 'Error', content = Label(text = "You can`t modify 'installed' value!"))
            error_popup.open()
        except InvalidDownloadedValueException as error:
            error_popup = Popup(size_hint=(None, None), size=(800, 400), title = 'Error', content = Label(text = "You can`t modify 'downloaded' value!"))
            error_popup.open()
        except InvalidIdValueException as error:
            error_popup = Popup(size_hint=(None, None), size=(800, 400), title = 'Error', content = Label(text = "You can`t modify 'id' value!"))
            error_popup.open()


# Declare both screens
class MainScreen(Screen):
    all_textinputs = []
    all_checkboxes = []
    all_buttons = []
    def __init__(self, **kw):
        super().__init__(**kw)

    def edit_row(self, *args, **kwargs):
        print(kwargs['row_id'])
        popup = PopupWindowEdit(kwargs['row_id'], size_hint=(None, None), size=(800, 400), title = 'Edit row in YAML')
        popup.open()


    def add_new_program(self):
        popup = PopupWindowAdd(size_hint=(None, None), size=(800, 400), title = 'Add new program')
        popup.open()


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
                rid= data_returned_from_query.index(column_data)



                textinput = Label(font_size = '15sp', size_hint_x = 0.8, text = converted_to_yaml, text_size = (600, None))
                checkbox = CheckBox(size_hint_x = 0.1)
                button_in_box_layout = BoxLayout(orientation = 'vertical', size_hint_x = 0.1)
                button_in_box_layout.add_widget(Label(text = ''))
                button_in_box_layout.add_widget(Button(text = 'Edit row!', on_press = partial(self.edit_row, row_id = rid)))
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
    