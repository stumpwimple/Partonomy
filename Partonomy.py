import PySimpleGUI as sg
import math
import random
import webbrowser
from collections import OrderedDict
from openpyxl import load_workbook

min_dc = 1
max_dc = 12

unique_trait_id = 0
unique_build_id = 0
build_trait_parent_id = "0"
game_trait_parent_id = "0"

list_of = {}
categories_of_list = {}

the_aggregate = OrderedDict()


# build_aggregate = OrderedDict()

class Trait:
    """Trait Class - A class that displays a trait ui, with a number of other ui elements meant for running a pprpg"""

    def __init__(self, trait_name, trait_id, parent_id, children_id=[], rand_table="", trait_type="untyped",
                 primary_trait=False, trait_unit=""):
        self.trait_name = trait_name
        self.trait_id = trait_id
        self.parent_id = parent_id
        self.children_id = children_id
        self.trait_type = trait_type
        self.rand_table = rand_table
        self.trait_result = sr(random.choice(list_of[self.rand_table]))
        self.trait_unit = trait_unit
        self.is_discovered = False
        self.primary_trait = primary_trait

        self.journal_entries = {}

    def __str__(self):
        trait_str = str(self.trait_name + ":")
        # print only the left 60 characters of value
        trait_str += str(self.trait_result) + " " + str(self.trait_unit)
        trait_str += str(self.proficiency)
        return trait_str

    def generate(self, trait_name=0):
        pass

    def reroll_trait(self):
        # self.value = eval(self.formula)
        self.proficiency = random.randint(min_dc, max_dc)


class Build_Trait:

    def __init__(self, trait_id, trait_name="", parent_id="0", children_id=[], trait_logic_type="default",
                 rand_table="Error", complex_trait="false", trait_type="untyped",
                 primary_trait=False, trait_unit=""):
        self.trait_name = trait_name
        self.trait_id = trait_id
        self.parent_id = parent_id
        self.children_id = children_id
        self.trait_type = trait_type
        self.trait_logic = Build_Logic(trait_logic_type)
        self.rand_table = rand_table
        self.trait_unit = trait_unit
        self.primary_trait = primary_trait
        self.complex_trait = complex_trait

        # These Traits pertain to gameplay.
        self.trait_result = sr(random.choice(list_of[self.rand_table]))
        self.proficiency_result = random.randint(min_dc, max_dc)
        self.is_discovered = False
        self.journal_entries = {}

    def __str__(self):
        trait_str = self.trait_name + "/ " + str(self.trait_id) + ":"
        trait_str += "Table: " + str(self.trait_result) + ", with proficiency:" + str(self.proficiency_result)
        return trait_str


class Build_Logic:
    def __init__(self, logic_type="default"):
        self.logic_type = logic_type

    def __str__(self):
        return self.logic_type

    print("in Build_Logic")


def import_random_lists_from_file():
    """ imports excel workbook, creates random generation lists, and list of random list categories.

    Also collects a list of categories this list could belong to and stores it in a list.
    """
    wb = load_workbook(filename='Random Lists.xlsx')
    ws = wb["SHORT_LISTS"]  ### CURRENTLY SET TO SHORT_LISTS FOR FASTER LOAD DEFAULT SHOULD BE "LISTS"

    for col in ws.iter_cols():
        this_list = []
        list_categories = []
        for cell in col:
            # stores list_name for this list of random items
            if cell.row == 1 and cell.value:
                list_name = cell.value
            # stores categories of list and stores them. Excel file uses rows 2-10 as categories
            elif (1 < cell.row <= 10) and cell.value:
                list_categories.append(cell.value)
            # stores items in list of random items
            elif cell.value:
                this_list.append(cell.value)
            else:
                break
        list_of[list_name] = this_list
        categories_of_list[list_name] = list_categories


# SUB-RESOLVE RESULTS WITH NESTED RANDOM LISTS
def sr(this_str):
    """Sub-Resolves any nested Random Lists"""
    while "[" in this_str:
        nested_list = this_str[this_str.find("[") + 1:this_str.find("]")]
        this_result = random.choice(list_of[nested_list])
        try:
            this_result = str(this_result)
        except ValueError:
            pass
        this_str = this_str.replace("[" + nested_list + "]", "|" + this_result + "|")
    return this_str


def build_trait_layout():
    global unique_build_id
    # print ("unique_build_id = ",unique_build_id)
    if unique_build_id == 0:
        button_element = sg.Button('SAVE ALL', key=("SAVE_BUILD"))
        logic_disabled = True
    else:
        button_element = sg.Button('EXPAND', key=("EXPAND_TRAIT" + str(unique_build_id)), disabled=True)
        logic_disabled = False

    layout = [[sg.Text(unique_build_id, size=(5, 1)),
               sg.Input(unique_build_id, size=(5, 1), k="BUILD_ID" + str(unique_build_id), disabled=True),
               sg.Input(size=(25, 1), key=("TRAIT_NAME" + str(unique_build_id))),
               sg.Button('LOGIC', key=("LOGIC" + str(unique_build_id)), disabled=logic_disabled, size=(10, 1)),
               sg.Combo(values=[*list_of], size=(25, 1), key=("TRAIT_TABLE" + str(unique_build_id))),
               sg.Input(size=(15, 1), key=("TRAIT_UNIT" + str(unique_build_id))),
               sg.Checkbox('', k='is_complex' + str(unique_build_id)),
               sg.Checkbox('', k='is_primary' + str(unique_build_id)), button_element]]
    return layout


def game_trait_layout():
    global unique_trait_id
    if unique_trait_id == 0:
        button_element = sg.Button('SAVE GAME', key=("SAVE_GAME"))
        logic_disabled = True
    else:
        button_element = sg.Button('EXPAND', key=("EXPAND_GAME_TRAIT" + str(unique_trait_id)), disabled=True)
        logic_disabled = False

    layout = [[sg.Text(unique_trait_id, size=(5, 1)),
               sg.Input(unique_trait_id, size=(5, 1), k="GAME_ID" + str(unique_trait_id), disabled=True),
               sg.Input(size=(5, 1), k="GAME_PROFICIENCY_RESULT" + str(unique_trait_id)),
               sg.Button("R", size=(5, 1), k="GAME_ROLL_PROFICIENCY" + str(unique_trait_id)),
               sg.Input(size=(20, 1), key=("GAME_TRAIT_NAME" + str(unique_trait_id))),
               sg.Input(size=(40, 1), key=("GAME_TRAIT_RESULT" + str(unique_trait_id))),
               sg.Button("Roll", size=(5, 1), k="GAME_REROLL_TRAIT" + str(unique_trait_id)),
               sg.Button("G", size=(5, 1), k="GAME_SEARCH" + str(unique_trait_id)),
               sg.Button("J", size=(5, 1), k="GAME_JOURNAL" + str(unique_trait_id)),
               button_element]]
    return layout


def build_layout(build_aggregate):
    global unique_build_id
    global screen_w
    global screen_h

    layout = [[sg.Button('TO PARENT', key=("GO_TO_PARENT")), sg.Text("PARENTS NAME HERE", key="PARENTS_PARENT"),
               sg.Text("", size=(60, 1)), sg.Button('GENERATE AGGREGATE', key=("GENERATE_AGGREGATE"))]]

    layout += [[sg.Text("lay_id", size=(5, 1)),
                sg.Text("bld_id", size=(5, 1)),
                sg.Text("Complex Trait", size=(22, 1)),
                sg.Text("LOGIC", size=(10, 1)),
                sg.Text("Trait Roll", size=(23, 1)),
                sg.Text("Units", size=(13, 1)),
                sg.Text("Comp?"), sg.Text("Prim?")]]
    layout += build_trait_layout()
    unique_build_id += 1

    layout += [[sg.Text("", size=(13, 1)), sg.Text("Sub-Trait", size=(22, 1))]]

    trait_layout = [[]]

    for i in range(1, 26):
        new_trait_layout = build_trait_layout()
        unique_build_id += 1
        trait_layout += new_trait_layout

    layout += [[sg.Column(trait_layout, size=(int(screen_w / 2), int(screen_h * .70)))]]

    return layout


def game_layout():
    global unique_trait_id
    global screen_w
    global screen_h

    layout = [[sg.Button('TO PARENT', key=("GO_TO_GAME_PARENT")),
               sg.Text("GAME PARENTS NAME HERE", key="GAME_PARENTS_PARENT"), sg.Text("", size=(60, 1)),
               sg.Button('REGENERATE AGGREGATE', key=("GAME_REGENERATE_AGGREGATE"))]]

    layout += [[sg.Text("lay_id", size=(5, 1)),
                sg.Text("gam_id", size=(5, 1)),
                sg.Text("Prof", size=(5, 1)),
                sg.Text("R.Prf", size=(5, 1)),
                sg.Text("Trait Name", size=(20, 1)),
                sg.Text("Trait Result", size=(40, 1))]]
    layout += game_trait_layout()
    unique_trait_id += 1

    layout += [[sg.Text("", size=(13, 1)), sg.Text("Sub-Trait", size=(22, 1))]]

    trait_layout = [[]]

    for i in range(1, 26):
        new_trait_layout = game_trait_layout()
        unique_trait_id += 1
        trait_layout += new_trait_layout

    layout += [[sg.Column(trait_layout, size=(int(screen_w / 2), int(screen_h * .70)))]]

    return layout


def logic_button_menu():
    print('============ Event ===============')


def logic_layout():
    layout = [[sg.Button("If-Then: ", key='if_then'), sg.Text("Optional: Else")],
              [sg.Button("Quantity X: ", key='quantity'), sg.Text("Optional: By Trait, Random Range")],
              [sg.Button("Chance %: ", key='chance'), sg.Text("Optional: Multi-select")],
              [sg.Button("Case: ", key='case'), sg.Text("Optional: By %, By List, By Trait")],
              [sg.Button("Exploding: ", key='exploding'), sg.Text("Optional: by %, maybe w/ decay")],
              [sg.Button("Inherit from Parent: ", key='inherit'), sg.Text("Optional: N/A for now")]]

    return sg.Window("Select Logic", layout, modal=True)


def logic_tabbed_layout():
    if_then_layout = [[sg.Text("If Then Logic Settings")],
                      [sg.Text("If: "), sg.Combo(values=[*list_of], size=(25, 1), key="TRAIT TABLES2"),
                       sg.Combo(values=('<', '>', '=', '?'), size=(5, 1), key="LOG-OP"),
                       sg.Input(size=(10, 1), key="LOG-input")], ]

    quantity_layout = [[sg.Text("Quantity Logic Settings")]]
    chance_layout = [[sg.Text("Chance Logic Settings")]]
    case_layout = [[sg.Text("Case Logic Settings")]]
    exploding_layout = [[sg.Text("Exploding Logic Settings")]]
    inherit_layout = [[sg.Text("Inherit Logic Settings")]]

    layout = [[sg.TabGroup(
        [[sg.Tab('If-Then', if_then_layout), sg.Tab('Quantity', quantity_layout), sg.Tab('Chance', chance_layout),
          sg.Tab('Case', case_layout), sg.Tab('Exploding', exploding_layout), sg.Tab('Inherit', inherit_layout)]])],
              [sg.Text('                                              '), sg.Button('CANCEL', k='Logic_cancel'),
               sg.Button('OK', k='Logic_ok')]]

    return sg.Window("Select Logic", layout, modal=True)


def initialize_test_agg(window):
    # This way of initializing Agg is dumb, redo this so that it is directly modifying the build aggregate
    window['TRAIT_NAME0'].update(value="Society")
    window['TRAIT_TABLE0'].update(value="TypeOfSociety")
    window['TRAIT_UNIT0'].update(value="feet")

    window['TRAIT_NAME1'].update(value="Society Status")
    window['TRAIT_TABLE1'].update(value="SocietyStatus")
    window['TRAIT_UNIT1'].update(value="km")
    window['is_primary1'].update(value=True)

    window['TRAIT_NAME2'].update(value="Era")
    window['TRAIT_TABLE2'].update(value="Era")
    window['TRAIT_UNIT2'].update(value="snitches")

    window['TRAIT_NAME3'].update(value="Economy")
    window['TRAIT_TABLE3'].update(value="MajorEconomy")
    window['TRAIT_UNIT3'].update(value="Dolla Dolla")
    window['is_primary3'].update(value=True)


def main():
    global unique_build_id
    global unique_trait_id
    global build_trait_parent_id
    global game_trait_parent_id
    global build_aggregate
    build_aggregate = OrderedDict()

    current_complex_trait = 0
    build_aggregate["0"] = Build_Trait("0")

    print(sg.Window.get_screen_size())

    global screen_w, screen_h
    # screen_w, screen_h = sg.Window.get_screen_size()  #Was using to size window based on Monitor size.
    # screen_w = int(screen_w*.45)
    # screen_h = int(screen_h*.8)

    # Static Window Size (Was trying to hit 1080P resolution, but couldn't fit all the lines.)
    screen_w = 1920
    screen_h = 1180

    # For possible future menu implementation
    menu_def = [['&File', ['E&xit']],
                ['&Help', ['&About']]]

    journal_layout = [[sg.Text('JOURNAL WINDOW')]]
    traits_layout = [[sg.Column(game_layout(), size=(int(screen_w / 2), int(screen_h * .8)), pad=(0, 0))]]
    right_layout = [[sg.Column(build_layout(build_aggregate), size=(int(screen_w / 2), int(screen_h * .8)),
                               background_color='blue', pad=(0, 0))],
                    [sg.Column(journal_layout, size=(int(screen_w / 2), int(screen_h * .2)), background_color='green',
                               pad=(0, 0))]]
    layout = [[sg.Column(traits_layout, size=(int(screen_w / 2), screen_h)),
               sg.Column(right_layout, size=(int(screen_w / 2), screen_h))]]

    window = sg.Window('Meronomy or Partonomy?', layout, size=(screen_w, screen_h))

    do_this_once = True

    LOGIC_window_active = False
    while True:
        event, values = window.read(timeout=100)

        if do_this_once:
            initialize_test_agg(window)
            do_this_once = False

        if event in (None, 'Exit'):
            print("[LOG] Clicked Exit!")
            break

        elif event == 'About':
            sg.popup('BOOM!')

        if not LOGIC_window_active and event[
                                       :5] == "LOGIC":  # LOOK AT LEFT 5 CHARACTERS of EVENT TO DETERMINE IF ANY LOGIC BUTTON HAS BEEN PRESSED
            LOGIC_window_active = True
            logic_window = logic_tabbed_layout()
            test_int = event[5:]
            print("[LOG] User Entered LOGIC #" + event[5:] + " menu: ")

        elif not LOGIC_window_active and event == 'SAVE_BUILD':
            print("SAVING")
            for key in range(0, 26):
                if values[('TRAIT_TABLE' + str(key))] != "":
                    t_table = values[('TRAIT_TABLE' + str(key))]
                    t_name = values[('TRAIT_NAME' + str(key))]
                    print("Table =", t_table, ", Name =", t_name)
                    if t_name == "":
                        print("didn't get name, should be giving default of Trait_table :", t_table)
                        window['TRAIT_NAME' + str(key)].update(value=t_table)
                        t_name = t_table

                    build_id = values[('BUILD_ID' + str(key))]
                    if key == 0:
                        trait_parent_id = build_aggregate[values['BUILD_ID' + str(key)]].parent_id
                    else:
                        trait_parent_id = build_trait_parent_id

                    build_aggregate[build_id] = Build_Trait(build_id,
                                                            trait_name=t_name,
                                                            trait_logic_type=['TRAIT_LOGIC' + str(key)],
                                                            parent_id=trait_parent_id,
                                                            rand_table=values['TRAIT_TABLE' + str(key)],
                                                            trait_unit=values['TRAIT_UNIT' + str(key)],
                                                            primary_trait=values['is_primary' + str(key)])
                    build_aggregate[build_id].children_id = []
                    # print(build_aggregate[build_id])
                    if key != 0:
                        window['EXPAND_TRAIT' + str(key)].update(disabled=False)

                        if build_id != "0":
                            build_aggregate[build_trait_parent_id].children_id.append(str(build_id))

        elif not LOGIC_window_active and event == 'GO_TO_PARENT':
            if build_trait_parent_id != build_aggregate[build_trait_parent_id].parent_id:
                build_trait_parent_id = build_aggregate[build_trait_parent_id].parent_id
                window['BUILD_ID0'].update(value=build_trait_parent_id)
                window['TRAIT_NAME0'].update(value=build_aggregate[build_trait_parent_id].trait_name)
                window['TRAIT_TABLE0'].update(value=build_aggregate[build_trait_parent_id].rand_table)
                window['TRAIT_UNIT0'].update(value=build_aggregate[build_trait_parent_id].trait_unit)
                window['is_complex0'].update(value=build_aggregate[build_trait_parent_id].complex_trait)
                window['is_primary0'].update(value=build_aggregate[build_trait_parent_id].primary_trait)

                if build_aggregate[build_trait_parent_id].children_id:
                    layout_id = 1

                    for id in build_aggregate[build_trait_parent_id].children_id:
                        window['BUILD_ID' + str(layout_id)].update(value=build_aggregate[id].trait_id)
                        window['TRAIT_NAME' + str(layout_id)].update(value=build_aggregate[id].trait_name)
                        window['TRAIT_TABLE' + str(layout_id)].update(value=build_aggregate[id].rand_table)
                        window['TRAIT_UNIT' + str(layout_id)].update(value=build_aggregate[id].trait_unit)
                        window['is_complex' + str(layout_id)].update(value=build_aggregate[id].complex_trait)
                        window['is_primary' + str(layout_id)].update(value=build_aggregate[id].primary_trait)
                        window['EXPAND_TRAIT' + str(layout_id)].update(disabled=False)
                        layout_id += 1

                    for empty_id in range(layout_id, 26):
                        window['BUILD_ID' + str(empty_id)].update(value=unique_build_id)
                        unique_build_id += 1
                        window['TRAIT_NAME' + str(empty_id)].update(value="")
                        window['TRAIT_TABLE' + str(empty_id)].update(value="")
                        window['TRAIT_UNIT' + str(empty_id)].update(value="")
                        window['is_complex' + str(empty_id)].update(value=False)
                        window['is_primary' + str(empty_id)].update(value=False)
                        window['EXPAND_TRAIT' + str(empty_id)].update(disabled=True)

                else:
                    for empty_id in range(1, 26):
                        print('"BUILD_ID"' + str(empty_id) + ": " + values[("BUILD_ID" + str(empty_id))])
                        window['BUILD_ID' + str(empty_id)].update(value=unique_build_id)
                        unique_build_id += 1
                        window['TRAIT_NAME' + str(empty_id)].update(value="")
                        window['TRAIT_TABLE' + str(empty_id)].update(value="")
                        window['TRAIT_UNIT' + str(empty_id)].update(value="")
                        window['is_complex' + str(empty_id)].update(value=False)
                        window['is_primary' + str(empty_id)].update(value=False)
                        window['EXPAND_TRAIT' + str(empty_id)].update(disabled=True)

        elif not LOGIC_window_active and event[:12] == 'EXPAND_TRAIT':
            layout_id = event[12:]
            build_trait_parent_id = values[('BUILD_ID' + layout_id)]
            window['BUILD_ID0'].update(value=build_trait_parent_id)
            window['TRAIT_NAME0'].update(value=build_aggregate[build_trait_parent_id].trait_name)
            window['TRAIT_TABLE0'].update(value=build_aggregate[build_trait_parent_id].rand_table)
            window['TRAIT_UNIT0'].update(value=build_aggregate[build_trait_parent_id].trait_unit)
            window['is_complex0'].update(value=build_aggregate[build_trait_parent_id].complex_trait)
            window['is_primary0'].update(value=build_aggregate[build_trait_parent_id].primary_trait)

            if build_aggregate[build_trait_parent_id].children_id:
                layout_id = 1
                for id in build_aggregate[build_trait_parent_id].children_id:
                    window['BUILD_ID' + str(layout_id)].update(value=build_aggregate[id].trait_id)
                    window['TRAIT_NAME' + str(layout_id)].update(value=build_aggregate[id].trait_name)
                    window['TRAIT_TABLE' + str(layout_id)].update(value=build_aggregate[id].rand_table)
                    window['TRAIT_UNIT' + str(layout_id)].update(value=build_aggregate[id].trait_unit)
                    window['is_complex' + str(layout_id)].update(value=build_aggregate[id].complex_trait)
                    window['is_primary' + str(layout_id)].update(value=build_aggregate[id].primary_trait)
                    window['EXPAND_TRAIT' + str(layout_id)].update(disabled=False)
                    layout_id += 1

                for empty_id in range(layout_id, 26):
                    window['BUILD_ID' + str(empty_id)].update(value=unique_build_id)
                    unique_build_id += 1
                    window['TRAIT_NAME' + str(empty_id)].update(value="")
                    window['TRAIT_TABLE' + str(empty_id)].update(value="")
                    window['TRAIT_UNIT' + str(empty_id)].update(value="")
                    window['is_complex' + str(empty_id)].update(value=False)
                    window['is_primary' + str(empty_id)].update(value=False)
                    window['EXPAND_TRAIT' + str(empty_id)].update(disabled=True)
            else:
                for empty_id in range(1, 26):
                    window['BUILD_ID' + str(empty_id)].update(value=unique_build_id)
                    unique_build_id += 1
                    window['TRAIT_NAME' + str(empty_id)].update(value="")
                    window['TRAIT_TABLE' + str(empty_id)].update(value="")
                    window['TRAIT_UNIT' + str(empty_id)].update(value="")
                    window['is_complex' + str(empty_id)].update(value=False)
                    window['is_primary' + str(empty_id)].update(value=False)
                    window['EXPAND_TRAIT' + str(empty_id)].update(disabled=True)

        elif not LOGIC_window_active and event == 'GENERATE_AGGREGATE':
            window['GAME_ID0'].update(value=game_trait_parent_id)
            window['GAME_PROFICIENCY_RESULT0'].update(value=build_aggregate[game_trait_parent_id].proficiency_result)
            window['GAME_TRAIT_NAME0'].update(value=build_aggregate[game_trait_parent_id].trait_name)
            window['GAME_TRAIT_RESULT0'].update(
                value=build_aggregate[game_trait_parent_id].trait_result + " " + build_aggregate[
                    game_trait_parent_id].trait_unit)

            if build_aggregate[game_trait_parent_id].children_id:
                layout_id = 1

                for id in build_aggregate[game_trait_parent_id].children_id:
                    window['GAME_ID' + str(layout_id)].update(value=build_aggregate[id].trait_id)
                    window['GAME_PROFICIENCY_RESULT' + str(layout_id)].update(
                        value=build_aggregate[id].proficiency_result)
                    window['GAME_TRAIT_NAME' + str(layout_id)].update(value=build_aggregate[id].trait_name)
                    window['GAME_TRAIT_RESULT' + str(layout_id)].update(
                        value=build_aggregate[id].trait_result + " " + build_aggregate[id].trait_unit)
                    window['EXPAND_GAME_TRAIT' + str(layout_id)].update(disabled=False)
                    layout_id += 1

                for empty_id in range(layout_id, 26):
                    window['GAME_ID' + str(layout_id)].update(value=unique_build_id)
                    unique_build_id += 1
                    window['GAME_PROFICIENCY_RESULT' + str(layout_id)].update(value="")
                    window['GAME_TRAIT_NAME' + str(layout_id)].update(value="")
                    window['GAME_TRAIT_RESULT' + str(layout_id)].update(value="")
                    window['EXPAND_GAME_TRAIT' + str(layout_id)].update(disabled=True)

        elif not LOGIC_window_active and event == 'GO_TO_GAME_PARENT':
            if game_trait_parent_id != build_aggregate[game_trait_parent_id].parent_id:
                game_trait_parent_id = build_aggregate[game_trait_parent_id].parent_id
                window['GAME_ID0'].update(value=game_trait_parent_id)
                window['GAME_PROFICIENCY_RESULT0'].update(
                    value=build_aggregate[game_trait_parent_id].proficiency_result)
                window['GAME_TRAIT_NAME0'].update(value=build_aggregate[game_trait_parent_id].trait_name)
                window['GAME_TRAIT_RESULT0'].update(
                    value=build_aggregate[game_trait_parent_id].trait_result + " " + build_aggregate[id].trait_unit)

                if build_aggregate[game_trait_parent_id].children_id:
                    layout_id = 1

                    for id in build_aggregate[game_trait_parent_id].children_id:
                        window['GAME_ID' + str(layout_id)].update(value=build_aggregate[id].trait_id)
                        window['GAME_PROFICIENCY_RESULT' + str(layout_id)].update(
                            value=build_aggregate[id].proficiency_result)
                        window['GAME_TRAIT_NAME' + str(layout_id)].update(value=build_aggregate[id].trait_name)
                        window['GAME_TRAIT_RESULT' + str(layout_id)].update(
                            value=build_aggregate[id].trait_result + " " + build_aggregate[id].trait_unit)
                        window['EXPAND_GAME_TRAIT' + str(layout_id)].update(disabled=False)
                        layout_id += 1

                    for empty_id in range(layout_id, 26):
                        window['GAME_ID' + str(empty_id)].update(value=unique_build_id)
                        unique_build_id += 1
                        window['GAME_PROFICIENCY_RESULT' + str(empty_id)].update(value="")
                        window['GAME_TRAIT_NAME' + str(empty_id)].update(value="")
                        window['GAME_TRAIT_RESULT' + str(empty_id)].update(value="")
                        window['EXPAND_GAME_TRAIT' + str(empty_id)].update(disabled=True)

                else:
                    for empty_id in range(1, 26):
                        print('"BUILD_ID"' + str(empty_id) + ": " + values[("BUILD_ID" + str(empty_id))])
                        window['BUILD_ID' + str(empty_id)].update(value=unique_build_id)
                        unique_build_id += 1
                        window['TRAIT_NAME' + str(empty_id)].update(value="")
                        window['TRAIT_TABLE' + str(empty_id)].update(value="")
                        window['TRAIT_UNIT' + str(empty_id)].update(value="")
                        window['is_complex' + str(empty_id)].update(value=False)
                        window['is_primary' + str(empty_id)].update(value=False)
                        window['EXPAND_TRAIT' + str(empty_id)].update(disabled=True)

        elif not LOGIC_window_active and event[:17] == 'EXPAND_GAME_TRAIT':
            print('in EXPAND_GAME_TRAIT')
            layout_id = event[17:]
            game_trait_parent_id = values[('GAME_ID' + layout_id)]
            window['GAME_ID0'].update(value=game_trait_parent_id)
            window['GAME_PROFICIENCY_RESULT0'].update(value=build_aggregate[game_trait_parent_id].proficiency_result)
            window['GAME_TRAIT_NAME0'].update(value=build_aggregate[game_trait_parent_id].trait_name)
            window['GAME_TRAIT_RESULT0'].update(
                value=build_aggregate[game_trait_parent_id].trait_result + " " + build_aggregate[
                    game_trait_parent_id].trait_unit)

            if build_aggregate[game_trait_parent_id].children_id:
                layout_id = 1
                for id in build_aggregate[game_trait_parent_id].children_id:
                    window['GAME_ID' + str(layout_id)].update(value=build_aggregate[id].trait_id)
                    window['GAME_PROFICIENCY_RESULT' + str(layout_id)].update(
                        value=build_aggregate[id].proficiency_result)
                    window['GAME_TRAIT_NAME' + str(layout_id)].update(value=build_aggregate[id].trait_name)
                    window['GAME_TRAIT_RESULT' + str(layout_id)].update(
                        value=build_aggregate[id].trait_result + " " + build_aggregate[id].trait_unit)
                    window['EXPAND_GAME_TRAIT' + str(layout_id)].update(disabled=False)
                    layout_id += 1

                for empty_id in range(layout_id, 26):
                    window['GAME_ID' + str(empty_id)].update(value=unique_build_id)
                    unique_build_id += 1
                    window['GAME_PROFICIENCY_RESULT' + str(empty_id)].update(value="")
                    window['GAME_TRAIT_NAME' + str(empty_id)].update(value="")
                    window['GAME_TRAIT_RESULT' + str(empty_id)].update(value="")
                    window['EXPAND_GAME_TRAIT' + str(empty_id)].update(disabled=True)
            else:
                for empty_id in range(1, 26):
                    window['GAME_ID' + str(empty_id)].update(value=unique_build_id)
                    unique_build_id += 1
                    window['GAME_PROFICIENCY_RESULT' + str(empty_id)].update(value="")
                    window['GAME_TRAIT_NAME' + str(empty_id)].update(value="")
                    window['GAME_TRAIT_RESULT' + str(empty_id)].update(value="")
                    window['EXPAND_GAME_TRAIT' + str(empty_id)].update(disabled=True)

        if LOGIC_window_active:
            logic_event, logic_values = logic_window.read(timeout=100)
            if logic_event == "if_then":
                print("[LOG] Pressed If-Then Button")
                LOGIC_window_active = False
                logic_window.close()
            elif logic_event == "quantity":
                print("[LOG] Pressed quantity Button")
                LOGIC_window_active = False
                logic_window.close()
            elif logic_event == "chance":
                print("[LOG] Pressed chance Button")
                LOGIC_window_active = False
                logic_window.close()
            elif logic_event == "case":
                print("[LOG] Pressed case Button")
                LOGIC_window_active = False
                logic_window.close()
            elif logic_event == "exploding":
                print("[LOG] Pressed exploding Button")
                LOGIC_window_active = False
                logic_window.close()
            elif logic_event == "inherit":
                print("[LOG] Pressed inherit Button")
                LOGIC_window_active = False
                logic_window.close()
            elif logic_event == None:
                print("LOGIC WINDOW CLOSED")
                LOGIC_window_active = False
                logic_window.close()

            elif logic_event == 'Logic_cancel':
                print("LOGIC WINDOW canceled")
                # LOGIC_window_active = False
                # logic_window.close()

            elif logic_event == 'Logic_ok':
                print("LOGIC CONFIRMED")

                # LOGIC_window_active = False
                # logic_window.close()

    window.close()
    exit(0)


import_random_lists_from_file()  # TURNED OFF FOR TESTING UI

if __name__ == '__main__':
    main()
