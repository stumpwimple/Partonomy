import PySimpleGUI as sg
import math
import random
import webbrowser
from collections import OrderedDict
from openpyxl import load_workbook

min_dc = 1
max_dc = 12

unique_trait_id = 1
unique_build_id = 0
current_build_parent=0
current_trait_parent=0

list_of = {}
categories_of_list = {}

the_aggregate = OrderedDict()
build_aggregate = OrderedDict()

class Trait:
    """Trait Class - A class that displays a trait ui, with a number of other ui elements meant for running a pprpg"""

    def __init__(self, trait_name, trait_id, parent_id, children_id, rand_table, trait_type = "untyped", primary_trait=False, trait_unit=""):
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

    def __init__(self, trait_id, trait_name="",parent_id=0, children_id="", trait_logic_type = "default", rand_table="", complex_trait="false", trait_type="untyped",
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

    def __str__(self):
        trait_str = self.trait_name + "/ " + str(self.trait_id) + ":"
        # print only the left 60 characters of value
        trait_str += "Table: " + str(self.rand_table) + ",   is_primary?:" + str(self.primary_trait)
        return trait_str

class Build_Logic:
    def __init__(self, logic_type = "default"):
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
    print ("unique_build_id = ",unique_build_id)

    if unique_build_id == 0:
        button_element = sg.Button('SAVE ALL', key=("SAVE_ALL"))
        logic_disabled=True
    else:
        button_element = sg.Button('EXPAND', key=("EXPAND_TRAIT"+str(unique_build_id)))
        logic_disabled=False

    layout = [[sg.Text(unique_build_id, size = (5,1)),
               sg.Input(unique_build_id, size = (5,1),k="BUILD_ID"+str(unique_build_id), disabled = True),
               sg.Input(size = (25,1), key=("TRAIT_NAME"+str(unique_build_id))),
               sg.Button('LOGIC',key=("LOGIC"+str(unique_build_id)), disabled=logic_disabled, size = (10,1)),
               sg.Combo(values = [*list_of], size = (25,1), key=("TRAIT_TABLE"+str(unique_build_id))),
               sg.Input(size = (15,1), key=("TRAIT_UNITS"+str(unique_build_id))),
               sg.Checkbox('',k='is_complex'+str(unique_build_id)),
               sg.Checkbox('',k='is_primary'+str(unique_build_id)), button_element]]
    return layout

def build_layout(build_aggregate):
    global unique_build_id
    global screen_w
    global screen_h

    layout = [[sg.Text("lay_id", size = (5,1)),
               sg.Text("bld_id", size = (5,1)),
               sg.Text("Complex Trait", size = (22,1)),
               sg.Text("LOGIC", size = (10,1)),
               sg.Text("Trait Roll", size = (23,1)),
               sg.Text("Units", size = (13,1)),
               sg.Text("Comp?"), sg.Text("Prim?")]]
    layout += build_trait_layout()
    unique_build_id += 1


    layout += [[sg.Text("", size = (13,1)), sg.Text("Sub-Trait", size = (22,1))]]

    trait_layout = [[]]
    # for key, values in build_aggregate.items():
    #     if key == 0:
    #         print("this is the prime trait")
    #     else:
    #         print(key, ": this is NOT the prime trait")
    #         new_trait_layout = build_trait_layout(unique_build_id, "cats")
    #         unique_build_id += 1
    #         trait_layout += new_trait_layout

    for i in range(1,26):
        new_trait_layout = build_trait_layout()
        unique_build_id += 1
        trait_layout += new_trait_layout

    layout += [[sg.Column(trait_layout, size=(int(screen_w/2),int(screen_h*.70)))]] #scrollable=True, vertical_scroll_only=True)
   # layout += [[sg.Text("", size = (5,1)), sg.Button('ADD TRAIT', k = "ADD_TRAIT")]]

    return layout

def logic_button_menu():
    print('============ Event ===============')

def logic_layout():
    layout = [[sg.Button("If-Then: ",key='if_then'), sg.Text("Optional: Else")],
              [sg.Button("Quantity X: ",key='quantity'), sg.Text("Optional: By Trait, Random Range")],
              [sg.Button("Chance %: ",key='chance'), sg.Text("Optional: Multi-select")],
              [sg.Button("Case: ",key='case'), sg.Text("Optional: By %, By List, By Trait")],
              [sg.Button("Exploding: ",key='exploding'), sg.Text("Optional: by %, maybe w/ decay")],
              [sg.Button("Inherit from Parent: ",key='inherit'), sg.Text("Optional: N/A for now")]]

    return sg.Window("Select Logic", layout, modal=True)

def logic_tabbed_layout():

    if_then_layout = [[sg.Text("If Then Logic Settings")],
                      [sg.Text("If: "), sg.Combo(values = [*list_of], size = (25,1), key="TRAIT TABLES2"), sg.Combo(values = ('<','>','=','?'), size = (5,1), key="LOG-OP"), sg.Input(size = (10,1), key="LOG-input")],]

    quantity_layout = [[sg.Text("Quantity Logic Settings")]]
    chance_layout = [[sg.Text("Chance Logic Settings")]]
    case_layout = [[sg.Text("Case Logic Settings")]]
    exploding_layout = [[sg.Text("Exploding Logic Settings")]]
    inherit_layout = [[sg.Text("Inherit Logic Settings")]]

    layout = [[sg.TabGroup([[sg.Tab('If-Then', if_then_layout), sg.Tab('Quantity', quantity_layout), sg.Tab('Chance', chance_layout),
               sg.Tab('Case', case_layout), sg.Tab('Exploding', exploding_layout), sg.Tab('Inherit', inherit_layout)]])],
              [sg.Text('                                              '),sg.Button('CANCEL', k='Logic_cancel'),sg.Button('OK', k='Logic_ok')]]

    return sg.Window("Select Logic", layout, modal=True)

def main():
    global unique_build_id
    global unique_trait_id

    current_complex_trait = 0
    build_aggregate[0] = Build_Trait(0)

    print(sg.Window.get_screen_size())
    global screen_w, screen_h
    screen_w, screen_h = sg.Window.get_screen_size()

    screen_w = int(screen_w*.5)
    screen_h = int(screen_h*.8)


    menu_def = [['&File', ['E&xit']],
                ['&Help', ['&About']] ]

    journal_layout = [[sg.Text('JOURNAL WINDOW')]]
    trait_layout = [[sg.Text('trait_layout', size=(int(screen_w/2),screen_h), background_color='red', pad=(0,0))]]
    right_layout = [[sg.Column(build_layout(build_aggregate), size=(int(screen_w/2),int(screen_h*.8)), background_color='blue', pad=(0,0))],
                    [sg.Column(journal_layout, size=(int(screen_w/2),int(screen_h*.2)), background_color='green', pad=(0,0))]]
    layout = [[sg.Column(trait_layout, size=(int(screen_w/2),screen_h)), sg.Column(right_layout, size=(int(screen_w/2),screen_h))]]

    window = sg.Window('Meronomy or Partonomy?', layout, size=(screen_w,screen_h))

    LOGIC_window_active = False
    while True:
        event, values = window.read(timeout=100)

        if event in (None, 'Exit'):
            print("[LOG] Clicked Exit!")            
            break

        elif event == 'About':
            sg.popup('BOOM!') 

        if not LOGIC_window_active and event[:5] == "LOGIC": # LOOK AT LEFT 5 CHARACTERS of EVENT TO DETERMINE IF ANY LOGIC BUTTON HAS BEEN PRESSED
            LOGIC_window_active = True
            logic_window = logic_tabbed_layout()  
            test_int = event[5:]
            print("[LOG] User Entered LOGIC #"+event[5:]+" menu: ")
        elif not LOGIC_window_active and event == 'ADD_TRAIT':
            print("MOCK: ADDING TRAIT #", unique_build_id)
        elif not LOGIC_window_active and event == 'SAVE_ALL':
            print("SAVING")
            print(unique_build_id)

            for key in range (0,26):
                print(values[("BUILD_ID"+str(key))])

                if values[('TRAIT_TABLE'+str(key))] != "" and values[('BUILD_ID' +str(key))] != "":
                    print("MOCK ADDING TO AGGREGATE")
                    build_aggregate[values[('BUILD_ID'+str(key))]] = Build_Trait(values[('BUILD_ID'+str(key))], parent_id= current_build_parent ,trait_name=values['TRAIT_NAME'+str(key)], rand_table=values['TRAIT_TABLE'+str(key)],
                                                 primary_trait=values['is_primary'+str(key)])
                    print(build_aggregate[values[('BUILD_ID'+str(key))]])

        elif not LOGIC_window_active and event[:12] == 'EXPAND_TRAIT':
            print("EXPANDING TRAIT:", event[12:] )

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
                #LOGIC_window_active = False
                #logic_window.close()

            elif logic_event == 'Logic_ok':
                print("LOGIC CONFIRMED")

                #LOGIC_window_active = False
                #logic_window.close()

    window.close()
    exit(0)


import_random_lists_from_file()      #TURNED OFF FOR TESTING UI

if __name__ == '__main__':
    main()