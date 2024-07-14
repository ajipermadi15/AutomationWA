import PySimpleGUI as sg
import os.path

from autoWA import AutomationWA

def textBox_validity(
        key: str,
        max_char: int,
) -> None:
    if (event == key and len(values[key]) and values[key][-1] not in ('123456789')) or (len(values[key]) > max_char):
        window[key].update(values[key][:-1])

def disable_all(
        value: bool = True
) -> None:
    for key in keys:
        window[key].update(disabled = value)

def visible_pbar(
        value: bool = True
) -> None:
    for key in pbar_keys:
        window[key].update(visible = value)

def about_popup():
    layout = [
        [sg.Push(), sg.Text("About"), sg.Push()],
        [sg.Text("This source code can be found in \githublink.\nFeel free to give feedback for further improvement.")],
        [sg.Push(), sg.Button('OK'), sg.Push()],
    ]
    sg.Window('About', layout, modal=True, keep_on_top=True).read(close=True)

class AutomationWA(AutomationWA):
    def update_progress_bar(
            self,
            finished: bool = False
    )-> None:
        global progress, add_progress
        
        if finished:
            progress = 100
        else:
            progress += add_progress
    
        window['-PROGRESS VALUE-'].update(str(progress))
        window['-PBAR-'].update(current_count=progress)
        print('progress bar updated!')

menu = [['File', ['Setting', 'Exit']], ['About', ['Help', 'About']]]

layout = [
    [
        sg.Menu(menu)
    ],
    [
        sg.Text("Data Path"),
        sg.Push(),
        sg.In(size=(25, 1), enable_events=True, disabled=True),
        sg.FileBrowse(file_types=(("Text Files", "*.csv"),), key='-DATA-'),
    ],
    [
        sg.Text("Files Folder Path"),
        sg.Push(),
        sg.In(size=(25, 1), enable_events=True, disabled=True),
        sg.FolderBrowse(key='-FOLDER-'),
    ],
    [
        sg.Text("Start:"),
        sg.In('1', size=(3, 1), enable_events=True,  key='-START INPUT-'),
        sg.Text("End:"),
        sg.In('', size=(3, 1), enable_events=True,  key='-END INPUT-'),
    ],
    [
        sg.Checkbox('Auto Logout', enable_events=True, default=True, key='-LOGOUT-'),
    ],
    [
        sg.Checkbox('Set Custom Caption', enable_events=True, default=False, key='-CUSTOM CAPTION-'),
    ],
    [
        sg.Push(),
        sg.Multiline(size=(50, 5), enable_events=True, key='-CAPTION BOX-', disabled=True)
    ],
    [
        sg.Push(),
        sg.Button('Process!', key='-PROCESS-'),
        sg.Push(),
    ],
    [
        sg.ProgressBar(max_value=100, size=(25, 5), visible=False, expand_x=True, expand_y=True, orientation="h", key='-PBAR-'),
        sg.Text("0", size=(3, 1), visible=False, justification="right", key='-PROGRESS VALUE-'),
        sg.Text("%", size=(2, 1), visible=False, justification="left", key="-PERCENT-"),
    ]
]

keys = ['-DATA-', '-FOLDER-', '-START INPUT-', '-END INPUT-', '-LOGOUT-', '-CUSTOM CAPTION-', '-CAPTION BOX-', '-PROCESS-']
pbar_keys = ['-PBAR-', '-PROGRESS VALUE-', "-PERCENT-"]
window = sg.Window('Automation WA', layout, keep_on_top=True)

while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
        
    if event == "Setting":
        pass

    if event == "Help":
        pass

    if event == "About":
        about_popup()

    textBox_validity('-START INPUT-', 3)
    textBox_validity('-END INPUT-', 3)

    if values['-CUSTOM CAPTION-'] == True:
        window['-CAPTION BOX-'].update(disabled = False)
    else:
        window['-CAPTION BOX-'].update(disabled = True)

    if event == '-PROCESS-':
        disable_all(True)

        if len(values['-END INPUT-']) == 0:
            values['-END INPUT-'] = -999

        data_file_PATH = values['-DATA-']
        files_folder_PATH = values['-FOLDER-']
        auto_logout = values['-LOGOUT-']
        start, end = int(values['-START INPUT-']), int(values['-END INPUT-'])

        if data_file_PATH == "" or files_folder_PATH == "":
            sg.popup("Path can't be empty!", button_justification="center")
        else:
            if values['-CUSTOM CAPTION-'] == True:
                custom_caption = values['-CAPTION BOX-']
            else:
                custom_caption = None

            automation = AutomationWA()

            automation.read_database(data_file_PATH)
            n_data = len(automation.data)
            if end == -999 or end > n_data:
                end = n_data
                window['-END INPUT-'].update(f"{n_data}")

            visible_pbar(True)
            progress = 0
            add_progress = int(100 / (end + 1 - start))
            window['-PROGRESS VALUE-'].update(str(progress))
            window['-PBAR-'].update(current_count=progress)
            print('progress bar updated!')

            automation.files_folder_PATH = files_folder_PATH
            automation.login()
            automation.send_to_multiple_receivers(data_file_PATH, start=start, end=end, custom_caption=custom_caption, auto_logout=auto_logout, gui=True)
           
            #popup finish/error


        disable_all(False)

window.close()