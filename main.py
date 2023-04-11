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
from kivy.uix.image import Image
from kivy.properties import NumericProperty
import sqlite3
import yaml
from yaml.loader import SafeLoader
from functools import partial
import requests
import os

Window.size = (1500, 600)
Window.minimum_width, Window.minimum_height = Window.size

dirname = os.path.dirname(__file__)
red_dot_path = os.path.join(dirname, 'images\\red_dot.png')
green_dot_path = os.path.join(dirname, 'images\\green_dot.png')
database_path = os.path.join(dirname, 'programs.db')
downloads_path = os.path.join(dirname, 'downloads\\')
if os.path.isdir(downloads_path) != True:
    os.mkdir(downloads_path)


class InvalidIdValueException(Exception):
    def __init__(self):
            super().__init__("You can`t modify 'id' value!")
class InvalidDownloadedValueException(Exception):
    def __init__(self):
            super().__init__("You can`t modify 'downloaded' value!")
class InvalidInstalledValueException(Exception):
    def __init__(self):
            super().__init__("You can`t modify 'installed' value!")  
class InvalidURLException(Exception):
    def __init__(self):
            super().__init__("Operation failed. Something is wrong with URL")        



Builder.load_file('.\gui.kv')


class PopupWindowAdd(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.yaml_formatted = {'name': 'Name of a program',
                               'url':'URL link to program',
                               'install_command':'Program will be installed using this command',
                               'check_presence_path':'Presence will be indicated whether or not this file exist'}
        self.converted_to_yaml = yaml.dump(self.yaml_formatted, sort_keys=False)
        self.ids.textinput_id.text = self.converted_to_yaml

    def save_changes_to_database(self):
        try:
            self.edited_text_in_yaml = yaml.load(self.ids.textinput_id.text, Loader=SafeLoader)
            print(type(self.edited_text_in_yaml))
            print(self.edited_text_in_yaml)
            sqlite_connection = sqlite3.connect(database_path)
            cursor = sqlite_connection.cursor()
            cursor.execute("""INSERT INTO ProgramManager3000(name,url,install_command,check_presence_path,installed) VALUES(?,?,?,?,0)""",
                         (self.edited_text_in_yaml['name'], self.edited_text_in_yaml['url'], self.edited_text_in_yaml['install_command'], self.edited_text_in_yaml['check_presence_path']))
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

            if self.edited_text_in_yaml['installed'] != self.orginal_text_in_yaml['installed']:
                raise InvalidInstalledValueException()

            sqlite_connection = sqlite3.connect(database_path)
            cursor = sqlite_connection.cursor()
            cursor.execute("""UPDATE ProgramManager3000 SET name=?,url=?,install_command=?,check_presence_path=?,installed=? WHERE id=?""",
                         (self.edited_text_in_yaml['name'], self.edited_text_in_yaml['url'], self.edited_text_in_yaml['install_command'],
                             self.edited_text_in_yaml['check_presence_path'], self.edited_text_in_yaml['installed'], self.edited_text_in_yaml['id']))
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
    all_icons = []
    def __init__(self, **kw):
        super().__init__(**kw)

    def remove_program_entry(self):
        try:
            to_be_removed = []
            for i in range(len(self.all_checkboxes)):
                if self.all_checkboxes[i].active:
                    text_in_yaml = yaml.load(self.all_textinputs[i].text, Loader = SafeLoader)
                    to_be_removed.append(text_in_yaml)

            sqlite_connection = sqlite3.connect(database_path)
            cursor = sqlite_connection.cursor()
            for entry in to_be_removed:
                cursor.execute("""DELETE FROM ProgramManager3000 WHERE id=?""", (entry['id'],))
            sqlite_connection.commit()
            cursor.close()
            self.get_search_results_from_database()
        except sqlite3.Error as error:
            error_popup = Popup(size_hint=(None, None), size=(800, 400), title = 'Error', content = Label(text = str(error)))
            error_popup.open()







    def install_selected(self):
        try:
            to_be_installed = []
            for i in range(len(self.all_checkboxes)):
                if self.all_checkboxes[i].active:
                    #print("This label is checked: ", self.all_textinputs[i].text)
                    text_in_yaml = yaml.load(self.all_textinputs[i].text, Loader = SafeLoader)
                    to_be_installed.append(text_in_yaml)
            for program in to_be_installed:
                print(program['name'])
                print(program['url'])
                url = program['url']
                if url.find('/') != -1:
                    name_from_url = url.rsplit('/', 1)[1]
                    save_path = downloads_path + name_from_url
                    response = requests.get(url, allow_redirects=True)
                    data_type = response.headers.get('content-type')
                    print(data_type)
                    if data_type != 'application/x-msi' and data_type != 'application/octet-stream':
                        raise InvalidURLException()
                        
                    open(save_path, 'wb').write(response.content)
                    status = os.system(program['install_command'])
                    print(status)


                else:
                    raise InvalidURLException
               
        except InvalidURLException as error:
                error_popup = Popup(size_hint=(None, None), size=(800, 400), title = 'Error', content = Label(text = "Operation failed. Something is wrong with URL"))
                error_popup.open()
        except requests.exceptions.ConnectionError as error:
                error_popup = Popup(size_hint=(None, None), size=(800, 400), title = 'Error', content = Label(text = "Operation failed. Something is wrong with URL"))
                error_popup.open()  


    def edit_row(self, *args, **kwargs):
        print(kwargs['row_id'])
        popup = PopupWindowEdit(kwargs['row_id'], size_hint=(None, None), size=(1000, 400), title = 'Edit row in YAML')
        popup.open()


    def add_new_program(self):
        popup = PopupWindowAdd(size_hint=(None, None), size=(1000, 400), title = 'Add new program')
        popup.open()



    def check_program_exist(self, path_to_file):
        if os.path.isfile(path_to_file):
            return 1
        else:
            return 0



    def get_search_results_from_database(self):
        
        for icon in self.all_icons:
            self.ids.search_result_id.remove_widget(icon)

        for textinput in self.all_textinputs:
            self.ids.search_result_id.remove_widget(textinput)

        for checkbox in self.all_checkboxes:
            self.ids.search_result_id.remove_widget(checkbox)

        for button in self.all_buttons:
            self.ids.search_result_id.remove_widget(button)
        
        self.all_icons.clear()
        self.all_textinputs.clear()
        self.all_checkboxes.clear()
        self.all_buttons.clear()

        try:
            sqlite_connection = sqlite3.connect(database_path)
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
                converted_to_yaml_dict = yaml.load(converted_to_yaml, Loader=SafeLoader)
                print(self.check_program_exist(converted_to_yaml_dict['check_presence_path']))

                if self.check_program_exist(converted_to_yaml_dict['check_presence_path']) == 1:
                    cursor.execute("""UPDATE ProgramManager3000 SET installed=? WHERE id=?""", (1,converted_to_yaml_dict['id']))
                    sqlite_connection.commit()
                    status_icon = Image(source=green_dot_path, size_hint_x = 0.05) 
                else:
                    cursor.execute("""UPDATE ProgramManager3000 SET installed=? WHERE id=?""", (0,converted_to_yaml_dict['id']))
                    sqlite_connection.commit()
                    status_icon = Image(source=red_dot_path, size_hint_x = 0.05)              
                textinput = Label(font_size = '15sp', size_hint_x = 0.75, text = converted_to_yaml, text_size = (1000, None))
                checkbox = CheckBox(size_hint_x = 0.05, color = [86, 230, 59, 0.8])
                button_in_box_layout = BoxLayout(orientation = 'vertical', size_hint_x = 0.15, padding = [0,0,50,0])
                button_in_box_layout.add_widget(Label(text = ''))
                button_in_box_layout.add_widget(Button(text = 'Edit row!', on_press = partial(self.edit_row, row_id = rid)))
                button_in_box_layout.add_widget(Label(text = ''))

                self.all_icons.append(status_icon)
                self.all_textinputs.append(textinput)
                self.all_checkboxes.append(checkbox)
                self.all_buttons.append(button_in_box_layout)

                self.ids.search_result_id.add_widget(status_icon)
                self.ids.search_result_id.add_widget(textinput)
                self.ids.search_result_id.add_widget(checkbox)
                self.ids.search_result_id.add_widget(button_in_box_layout)
            cursor.close()

        except sqlite3.Error as error:
            print('Error during database communication. ', error)

class HistoryScreen(Screen):
    pass



class TestApp(App):

    def build(self):
        # Create the screen manager
        self.title = 'ProgramManager3000'
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        #sm.add_widget(HistoryScreen(name='history'))

        return sm

if __name__ == '__main__':
    print(red_dot_path)
    TestApp().run()
    