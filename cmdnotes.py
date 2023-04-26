import os
import os.path
import colorama
from colorama import Fore, Style, Back
import keyboard
import sys
import json

sel = 0
sel_isdir = False
sel_path = ''
editing = False
size = 0
open_dirs = []
notes = {}
colors = {}

def cls ():
    os.system('cls' if os.name=='nt' else 'clear')

def clear_input ():
    for i in range(100):
        keyboard.press_and_release('\b')

def printdir (dir_path = '.', indent = '', i = 0):
    global sel, sel_isdir, sel_path, editing

    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        isdir = os.path.isdir(item_path)
        expand_dir = (item_path in open_dirs)
        padding = '|' if not isdir else ('-' if expand_dir else '+')
        padding += ' '

        if i == sel:
            sel_isdir = isdir
            sel_path = item_path

        color = 0
        if item_path in colors:
            color = colors[item_path]

        if i == sel:
            back = Back.LIGHTRED_EX if color==1 else Back.YELLOW if color==2 else Back.GREEN if color==3 else Back.WHITE
            print(back + Fore.BLACK, end="")
        else:
            fore = Fore.LIGHTRED_EX if color==1 else Fore.YELLOW if color==2 else Fore.GREEN if color==3 else Fore.WHITE
            print(fore, end="")
        print(indent + padding + item, end="")

        print(Style.RESET_ALL + Fore.LIGHTBLACK_EX + ' ', end="")
        edited = False
        if i == sel and editing:
            edited = True
            
            if item_path in notes:
                for c in (notes[item_path] + ' '):
                    keyboard.press_and_release(c) # doesn't really work that well

            note = input()
            if note=='x' or note=='q':
                notes[item_path] = ''
            elif note != '':
                notes[item_path] = note

            editing = False
        elif item_path in notes:
            print(notes[item_path], end="")

        if edited:
            print(Style.RESET_ALL, end="")
        else:
            print(Style.RESET_ALL)

        i += 1

        if expand_dir:
            i = printdir(item_path, indent + '  ', i)
    return i

def update ():
    global size
    clear_input()
    cls()
    size = printdir()
    print()
    print(f'{Fore.WHITE}q     {Fore.LIGHTBLACK_EX} exit')
    print(f'{Fore.WHITE}del   {Fore.LIGHTBLACK_EX} delete save')
    print(f'{Fore.WHITE}w     {Fore.LIGHTBLACK_EX} up')
    print(f'{Fore.WHITE}s     {Fore.LIGHTBLACK_EX} down')
    print(f'{Fore.WHITE}e     {Fore.LIGHTBLACK_EX} edit note')
    print(f'{Fore.WHITE}space {Fore.LIGHTBLACK_EX} expand/collapse folder')
    print(f'{Fore.WHITE}1,2,3 {Fore.LIGHTBLACK_EX} set color')
    print()

def up ():
    global sel, editing
    if editing:
        return
    if sel > 0:
        sel -= 1
        update()

def down ():
    global sel, editing
    if editing:
        return
    if sel < size - 1:
        sel += 1
        update()

def expand ():
    global sel, sel_path, sel_isdir, editing
    if editing:
        return
    if sel_isdir:
        if sel_path in open_dirs:
            open_dirs.remove(sel_path)
        else:
            open_dirs.append(sel_path)
        update()

def edit ():
    global sel_path, editing
    if editing:
        return
    editing = True
    update()

def set_color (color):
    global sel_path
    if (sel_path in colors) and (colors[sel_path] == color):
        colors[sel_path] = 0
    else:
        colors[sel_path] = color
    update()

def delete ():
    global open_dirs, notes, colors
    open_dirs = []
    notes = {}
    colors = {}
    update()

if __name__ == "__main__":
    colorama.init()

    if os.path.exists('.cmdnotes.json'):
        f = open('.cmdnotes.json')
        data = json.load(f)
        open_dirs = data['open_dirs']
        notes = data['notes']
        colors = data['colors']
        f.close()

    update()
    keyboard.add_hotkey('e', edit)
    keyboard.add_hotkey('w', up)
    keyboard.add_hotkey('s', down)
    keyboard.add_hotkey('space', expand)
    keyboard.add_hotkey('1', lambda: set_color(1))
    keyboard.add_hotkey('2', lambda: set_color(2))
    keyboard.add_hotkey('3', lambda: set_color(3))
    keyboard.add_hotkey('del', delete)

    keyboard.wait('q')
    cls()
    clear_input()
    with open('.cmdnotes.json', 'w', encoding='utf-8') as f:
        json.dump({
            "colors": colors,
            "open_dirs": open_dirs,
            "notes": notes
        }, f, ensure_ascii=False, indent=4)
