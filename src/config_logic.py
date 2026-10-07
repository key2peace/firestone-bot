"""
Configuration related stuff
"""
import json
import os
import re
import sys

import mss
import mss.tools
import tkinter as tk
import requests

from tkinter import ttk
from typing import Any, ClassVar, Dict, List, Optional, Tuple, Union
from custom_vars import (
    alchemist_experiments,
    alchemist_transmutes,
    amulets,
    eventlist,
    exotic_merch,
    forbidden_knowledge,
    guardians,
    machines,
    mission_types,
    oracle_rituals,
    oracle_blessings
)

config = {
    # System settings
    'logfile':                          'logs/firestone-bot.log',   # location of the logfile
    'ollama_url':                       'http://localhost:11434',   # url voor ollama
    'ollama_model':                     'llama3.2:latest',          # model to use for ollama, llama3.2(-vision) should be optimal
    'tracker_file':                     'index.json',               # name of the filetracker index files
    'wait_page':                        5,                          # float or int value for the timeout waiting for a page to appear
    'min_score':                        0.95,                       # minimal match score
    'monitor':                          0,                          # monitor to use for capturing

    # Battle screen
    'bag_open_chests':                  True,                       # bag: open chests
    'upgrade_order':                    'slot 1,slot 2,slot 3,slot 4,slot 5, guardian, specials',
    'upgrade_max':                      True,                       # upgrade max on start/empower
    'upgrade_mode':                     2,                          # set upgrade amount for heroes
    'upgrade_interval':                 1,                          # upgrade interval
    'battle_boss_retry':                5,                          # max battle time
    'battle_level_farm':                1800,                       # farm time in seconds

    # Events
    'decorated_enable':                 True,                       # enable decorated heroes engine
    'decorated_prepare':                14,                         # days to prepare for event

    # Guild
    'guild_bank':                       True,                       # visit guild bank
    'guild_bank_donate':                True,                       # donate leftover guild coins to guild bank
    'guild_hall':                       True,                       # visit guild hall
    'guild_autoaccept':                 True,                       # auto accept guild applications

    # Temple of eternals
    'jump_percentage':                  400,                        # temple of eternals: jump percentage
    'jump_temple_token':                800,                        # temple of eternals: percentage to use temple tokens
    'jump_temple_icon':                 True,                       # jump if icon remains visible on main

    'version':                          2                           # config version on the end
}

# Alchemist
for name, (_, _, _) in alchemist_experiments.items():
    config.update({f'alchemist_{name}': False, f'decorated_{name}': 0, f'decorated_{name}_save': 0})
for _, (_, items) in alchemist_transmutes.items():
    for name, _ in items.items():
        config.update({f'transmute_{name}': False})

# Amulets
for name, (_, _) in amulets.items():
    config.update({f'buy_{name}': False})

# Exotic Merchant
for name, _ in exotic_merch.items():
    config.update({f'sell_{name}': False})

# Machines
for name in machines:
    for item in ['upgrade', 'blueprints', 'rarity']:
        config.update({f'wm_{name}_{item}': False})

# Magic Quarter
for name, _ in guardians.items():
    for item in ['train', 'enlighten', 'evolve', 'chaosrift', 'rarity']:
        config.update({f'guardian_{name}_{item}': False})

# Map
config.update({'map_order': ','.join(mission_types)})

config_file: str = 'bot_settings.json'
config_panel_vars = {}
config_comboboxes = {}
current_tab = None

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        # Bind hover events
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window: return
        # Create window relative to the widget
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True) # Remove standard window borders
        tw.wm_geometry(f'+{x}+{y}')
        tw.wm_attributes("-topmost", True) # Force it above your topmost app window

        # Tooltip styling
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1, padx=4, pady=2)
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

def checkbox(**args) -> None:
    global config_panel_vars

    column = args.get('column', 0)
    row = args.get('row', 0)
    tab = args.get('tab', current_tab)
    text = args.get('text', None)
    varname = args.get('varname', None)
    tooltip = args.get('tooltip', None)
    if not tab or not text or not varname:
        return

    config_panel_vars.update({varname: tk.IntVar(value=config.get(varname, 0))})
    box = tk.Checkbutton(tab, text=text, variable=config_panel_vars.get(varname, 0), onvalue=True, offvalue=False)
    box.grid(row=row, column=column, padx=5, pady=2, sticky='nsw')
    if tooltip:
        ToolTip(box, tooltip)

def combobox(**args) -> None:
    global config_comboboxes

    row = args.get('row', 0)
    tab = args.get('tab', current_tab)
    text = args.get('text', None)
    values = args.get('values', None)
    varname = args.get('varname', None)
    tooltip = args.get('tooltip', None)
    if not tab or not text or not values or not varname:
        return

    label(text=text, row=row, tooltip=tooltip)
    config_panel_vars.update({varname: tk.IntVar(value=config[varname])})
    config_comboboxes.update({varname: ttk.Combobox(tab, state='readonly', values=values)})
    config_comboboxes.get(varname).grid(row=row, column=1, columnspan=20, padx=5, pady=5, sticky='nsew', ipadx=5)
    config_comboboxes.get(varname).current(config[varname])
    config_comboboxes.get(varname).bind('<<ComboboxSelected>>', lambda e: combobox_event(e, varname))

def combobox_event(event, varname) -> None:
    global config_comboboxes, config_panel_vars

    if event:
        pass

    config_panel_vars.update({varname: tk.IntVar(value=config_comboboxes.get(varname).current())})

def config_load() -> None:
    """ Load config """
    global config

    if os.path.exists(config_file):
        conf_version = config.get('version')
        file_version = 0

        with open(config_file, 'rt', encoding='utf-8') as f:
            loaded_config = json.load(f)
            file_version = loaded_config.get('version', 0)
            config.update(loaded_config)

        if conf_version != file_version and __name__ != '__main__':
            config.update({'version': conf_version})
            config_page()

    elif __name__ != '__main__':
        config_page()

def config_page() -> None:
    """ Settings dialog """
    global config_panel_vars, current_tab

    c = tk.Tk()
    c.title('Firestone Bot Configuration')
    c.wm_attributes('-topmost', True)

    style = ttk.Style()
    style.theme_use('xpnative')
    style.configure('LeftTabs.TNotebook', tabposition='wn')
    style.configure('LeftTabs.TNotebook.Tab', width=-20, anchor='e', padding=(10, 2))
    #style.configure('TFrame', background='white')
    style.configure('TLabel', background='black', foreground='white')

    menu_frame = ttk.Frame(c, padding=10)
    menu_frame.pack(side=tk.LEFT, fill=tk.Y)
    tabs = ttk.Notebook(menu_frame, style='LeftTabs.TNotebook')
    tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
    button_frame = ttk.Frame(menu_frame, padding=(0, 5, 0, 0))
    button_frame.pack(side=tk.BOTTOM, fill=tk.X)
    button_save = tk.Button(button_frame, text='Save', command=config_save, bg='green', fg='white')
    button_save.pack(side=tk.LEFT, padx=(10,5), fill=tk.X, expand=True)
    ToolTip(button_save, 'Save the current values to the configuration file')
    button_exit = tk.Button(button_frame, text='Exit', command=c.destroy, bg='red', fg='white')
    button_exit.pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)
    ToolTip(button_exit,'Exit this tool without saving')

    current_tab = ttk.Frame(tabs, padding=10)
    tabs.add(current_tab, text='System')
    current_tab.grid_columnconfigure(1, minsize=400, weight=0)
    input_text(text='Logfile', row=0, varname='logfile', tooltip='The location of the logfile')
    input_text(text='Ollama URL', row=1, varname='ollama_url', on_update=('<Return>', 'ollama_url_verify'), tooltip='The base url for ollama [http(s)://host:port]')
    input_text(text='Ollama Model', row=2, varname='ollama_model', on_update=('<Return>', 'ollama_model_verify'), tooltip='Ollama model to use, please define a vision model')
    input_text(text='Tracker file', row=3, varname='tracker_file', tooltip='The name of the tracker file to use for image tracking')
    input_number(current_tab, 'Page Wait Time', 4, 'wait_page', 1, 30, 0.01)
    slider(current_tab, 'Min match score', 5, 'min_score', 0.8, 1)

    values = []
    monitors = mss.MSS().monitors[1::]
    for idx, monitor in enumerate(monitors):
        i = idx + 1
        n = monitor.get('name', 'unknown')
        w = monitor.get('width', 0)
        h = monitor.get('height', 0)
        text = f'Display {i}: {n} @ {w}x{h}'
        if monitor['is_primary']:
            text += ' (primary)'
        values.append(text)
    combobox(text='Monitor', row=6, varname='monitor', values=values, tooltip='Select the monitor the game will be running on')

    current_tab = ttk.Frame(tabs, padding=10)
    tabs.add(current_tab, text='Alchemist')
    label(text='Experiments', tooltip='Select the experiments to run')
    row = 1
    col = 0
    for name, _ in config.items():
        if name.startswith('alchemist_'):
            item = name[10::].replace('_', ' ').capitalize()
            checkbox(text=item, row=row, varname=name, column=col)
            col += 2
            if col == 8:
                col = 0
                row += 1
    label(text='Transmute Chests', row=row + 1)
    row += 2
    col = 0
    for name, _ in config.items():
        if name.startswith('transmute_'):
            item = name[10::].replace('_', ' ').capitalize()
            checkbox(text=item, row=row, varname=name, column=col)
            col += 2
            if col == 8:
                col = 0
                row += 1

    current_tab = ttk.Frame(tabs, padding=10)
    tabs.add(current_tab, text='Battle Screen')
    values = ['Upgrade x1','Upgrade x10','Upgrade x100','Next milestone','Upgrade max']
    combobox(text='Upgrade mode', row=0, varname='upgrade_mode', values=values)
    checkbox(text='Upgrade max on start/empower', row=2, varname='upgrade_max')
    upgrade_types = ['slot 1', 'slot 2', 'slot 3', 'slot 4', 'slot 5', 'guardian', 'specials']
    listbox(current_tab, 'Upgrade order', 3, 'upgrade_order', upgrade_types)
    input_number(current_tab, 'Upgrade interval', 19, 'upgrade_interval', 0, 60, 0.1)
    input_number(current_tab, 'Boss retry', 20, 'battle_boss_retry', 0, 60, 0.1)
    input_number(current_tab, 'Level back', 21, 'battle_level_back', 0, 60)
    input_number(current_tab, 'Farm time', 22, 'battle_level_farm', 0, 604800)
    checkbox(text='Open chests in bag', row=23, varname='bag_open_chests')

    current_tab = ttk.Frame(tabs, padding=10)
    tabs.add(current_tab, text='Decorated Heroes')
    checkbox(text='Enable decorate heroes mode',  varname='decorated_enable')
    input_number(current_tab, 'Days to prepare', 2, 'decorated_prepare', 0, 60)
    input_number(current_tab, 'Prepare dragon blood', 3, 'decorated_dragon_blood_save', 0, 16800)
    input_number(current_tab, 'Daily dragon blood', 4, 'decorated_dragon_blood', 0, 9)
    input_number(current_tab, 'Prepare strange dust', 5, 'decorated_strange_dust_save', 0, 13440)
    input_number(current_tab, 'Daily strange dust', 6, 'decorated_strange_dust', 0, 9)
    input_number(current_tab, 'Prepare exotic coin', 7, 'decorated_exotic_coin_save', 0, 420000)
    input_number(current_tab, 'Daily exotic coin', 8, 'decorated_exotic_coin', 0, 9)

    current_tab = ttk.Frame(tabs, padding=10)
    tabs.add(current_tab, text='Exotic Merchant')
    label(text='Sell items')
    idx = 1
    offset = 0
    for name, tooltip in exotic_merch.items():
        text = name.replace('_', ' ').capitalize()
        checkbox(text=text, row=idx, varname=f'sell_{name}', column=offset, tooltip=tooltip)
        offset += 2
        if offset == 6:
            idx += 1
            offset = 0

    current_tab = ttk.Frame(tabs, padding=10)
    tabs.add(current_tab, text='Garage')
    for idx, machine in enumerate(machines):
        label(text=machine.capitalize(), row=idx)
        for offset, item in enumerate(['upgrade', 'blueprints', 'rarity']):
            varname = f'wm_{machine}_{item}'
            value = tk.IntVar(value=config.get(varname, 0))
            config_panel_vars.update({varname: value})
            checkbox(text=item.capitalize(), varname=varname, row=idx, column=1+offset)

    current_tab = ttk.Frame(tabs, padding=10)
    tabs.add(current_tab, text='Guild')
    checkbox(text='Visit guild bank', row=0, varname='guild_bank')
    checkbox(text='Donate guild tokens', row=1, varname='guild_bank_donate')
    checkbox(text='Visit guild hall', row=2, varname='guild_hall')
    checkbox(text='Accept applications', row=3, varname='guild_autoaccept')

    current_tab = ttk.Frame(tabs, padding=10)
    tabs.add(current_tab, text='Magic Quarter')
    for idx, guardian in enumerate(guardians):
        label(text=guardian.capitalize(), row=idx)
        for offset, item in enumerate(['train', 'enlighten', 'evolve', 'chaosrift', 'rarity']):
            varname = f'guardian_{guardian}_{item}'
            value = tk.IntVar(value=config.get(varname, 0))
            config_panel_vars.update({varname: value})
            item = 'chaos rift' if item=='chaosrift' else item
            config_panel_vars.update({varname: value})
            checkbox(text=item.capitalize(), varname=varname, row=idx, column=1+offset)

    current_tab = ttk.Frame(tabs, padding=10)
    tabs.add(current_tab, text='Map')
    mission_types = ['adventure', 'dragon', 'monster', 'mystery', 'naval', 'scout', 'shadow', 'titan', 'war']
    listbox(current_tab, 'Mission map order', 0, 'map_order', mission_types)

    current_tab = ttk.Frame(tabs, padding=10)
    tabs.add(current_tab, text='Shop')
    label(text='Obtain Amulets')
    idx = 1
    offset = 0
    for name, _ in config.items():
        if name.startswith('buy_'):
            text = name[3::].replace('_', ' ').strip().capitalize()
            checkbox(text=text, row=idx, varname=name, column=offset)
            offset += 2
            if offset == 6:
                idx += 1
                offset = 0

    current_tab = ttk.Frame(tabs, padding=10)
    tabs.add(current_tab, text='Temple of eternals')
    current_tab.grid_columnconfigure(1, minsize=400, weight=0)
    checkbox(text='Jump when icon remains visible', varname='jump_temple_icon')
    input_number(current_tab, 'Jump percentage', 1, 'jump_percentage', 0, 100000000000)
    input_number(current_tab, 'Use temple token at', 2, 'jump_temple_token', 0, 100000000000)

    c.mainloop()

def config_save() -> None:
    """ Save config """
    global config

    if config_panel_vars:
        for name, value in config_panel_vars.items():
            config.update({name: value.get()})

    with open(config_file, 'wt', encoding='utf-8') as f:
        f.write(json.dumps(config, indent=4))

def input_number(tab, text, row, varname, min_val, max_val, increment = 1) -> None:
    global config_panel_vars

    label(text=text, row=row)
    config_panel_vars.update({varname: tk.DoubleVar(value=config[varname])})
    tk.Spinbox(tab, from_=min_val, to=max_val, increment=increment, textvariable=config_panel_vars.get(varname), width=6).grid(row=row, column=1, padx=5, pady=2, sticky='nsew')

def input_text(**args) -> None:
    global config_panel_vars

    row = args.get('row', 0)
    tab = args.get('tab', current_tab)
    text = args.get('text', None)
    varname = args.get('varname', None)
    tooltip = args.get('tooltip', None)
    on_update = args.get('on_update', None)
    if not tab or not text or not varname:
        return

    label(text=text, row=row, tooltip=tooltip)
    config_panel_vars.update({varname: tk.StringVar(value=config[varname])})
    item = tk.Entry(tab, textvariable=config_panel_vars.get(varname), highlightthickness=2)
    item.grid(row=row, column=1, padx=5, pady=2, sticky='nsew')
    if on_update:
        current_module = sys.modules[__name__]
        trigger, actual = on_update
        actual_function = getattr(current_module, actual)
        if actual_function:
            item.bind(trigger, lambda e: actual_function(e, item, varname))
            actual_function(None, item, varname)

def label(**args) -> None:
    column = args.get('column', 0)
    columnspan = args.get('columnspan', 1)
    row = args.get('row', 0)
    tab = args.get('tab', current_tab)
    text = args.get('text', None)
    tooltip = args.get('tooltip', None)
    if not tab or not text:
        return

    l = ttk.Label(tab, text=text)
    l.grid(row=row, column=column, columnspan=columnspan, pady=5, sticky='nsew', ipadx=5)
    if tooltip:
        ToolTip(l, tooltip)

def listbox(tab, text, row, varname, values) -> None:
    label(text=text, row=row)
    item = tk.Listbox(tab, selectmode=tk.SINGLE, activestyle='none', exportselection=0, height=len(values))
    item.grid(row=row, column=1, rowspan=len(values), padx=5, pady=2, sticky='nsw')
    middle = len(values) // 2 + row
    ttk.Button(tab, text='  Up  ', command=lambda: listbox_event(None, item, 'up', varname)).grid(row=middle - 1, column=0, padx=5, pady=2, sticky='nsew')
    ttk.Button(tab, text='Toggle', command=lambda: listbox_event(None, item, 'dblclick', varname)).grid(row=middle, column=0, padx=5, pady=2, sticky='nsew')
    ttk.Button(tab, text=' Down ', command=lambda: listbox_event(None, item, 'down', varname)).grid(row=middle + 1, column=0, padx=5, pady=2, sticky='nsew')

    current = config.get(varname, ','.join(values)).split(',')
    idx = 0
    for m in current:
        if m not in values:
            continue
        values.remove(m)
        item.insert(idx, m)
        item.itemconfig(idx, fg='green')
        idx += 1
    for m in values:
        item.insert(idx, m)
        item.itemconfig(idx, fg='red')
        idx += 1
    item.bind('<Double-1>', lambda e: listbox_event(e, item, 'dblclick', varname))

def listbox_event(event, item, action, varname) -> None:
    global config_panel_vars

    if event:
        pass

    idx = item.curselection()
    if not idx:
        return
    idx = idx[0]

    if action == 'dblclick':
        color = 'red' if item.itemcget(idx, 'fg') == 'green' else 'green'
        item.itemconfig(idx, fg=color)
    elif action in ['down', 'up']:
        if action == 'down' and idx == item.size() -1:
            return
        if action == 'up' and not idx:
            return
        color = item.itemcget(idx, 'fg')
        text = item.get(idx)
        new_idx = idx - 1 if action == 'up' else idx + 1
        item.delete(idx)
        item.insert(new_idx, text)
        item.itemconfig(new_idx, fg=color)
        item.selection_set(new_idx)

    config_panel_vars.update({varname: tk.StringVar(value=','.join([item.get(i) for i in range(item.size()) if item.itemcget(i, 'fg') == 'green']))})

def ollama_model_verify(event, item, varname) -> None:
    global config_panel_vars

    if event:
        pass

    url = config_panel_vars.get('ollama_url').get().rstrip('/') + '/api/tags'
    if not re.search(r'^https?://', url):
        return

    color = 'red'
    try:
        response = requests.get(url = url, timeout = 5)
        response.raise_for_status()
        for model in response.json().get('models', {}):
            if model.get('name', '').lower() == config_panel_vars.get(varname, '').get().lower():
                color = 'green'
                if not 'vision' in model.get('capabilities', []):
                    color = 'orange'
                break
    except Exception:
        pass

    item.configure(highlightbackground=color, highlightcolor=color)

def ollama_url_verify(event, item, varname) -> None:
    global config_panel_vars

    if event:
        pass

    url = config_panel_vars.get(varname).get().rstrip('/') + '/api/version'
    color = 'red'
    if re.search(r'^https?://', url):
        try:
            response = requests.get(url = url, timeout = 5)
            response.raise_for_status()
            version = response.json().get('version')
            m = re.search(r'^(\d+\.\d+\.\d+)$', version)
            if m:
                print(f'Ollama version {version} detected.\n')
                color = 'green'
        except Exception:
            pass

    item.configure(highlightbackground = color, highlightcolor = color)

def slider(tab, text, row, varname, min_val, max_val) -> None:
    global config_panel_vars

    label(text=text, row=row)
    config_panel_vars.update({varname: tk.DoubleVar(value=config.get(varname))})
    tk.Scale(tab, from_=min_val, to=max_val, orient=tk.HORIZONTAL, resolution=0.01, variable=config_panel_vars.get(varname)).grid(row=row, column=1, padx=5, pady=2, sticky='nsew')

config_load()
if __name__ == '__main__':
    config_page()