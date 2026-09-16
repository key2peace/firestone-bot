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

config = {
    # System settings
    'logfile':                          'logs/firestone-bot.log',   # location of the logfile
    'ollama_url':                       'http://localhost:11434',   # url voor ollama
    'ollama_model':                     'llama3.2:latest',          # model to use for ollama, llama3.2(-vision) should be optimal
    'tracker_file':                     'index.json',               # name of the filetracker index files
    'wait_page':                        5,                          # float or int value for the timeout waiting for a page to appear
    'min_score':                        0.95,                       # minimal match score
    'monitor':                          0,                          # monitor to use for capturing

    # Alchemist
    'alchemist_dragon_blood':           True,                       # alchemist: do dragon blood experiments
    'alchemist_strange_dust':           True,                       # alchemist: do strange dust experiments
    'alchemist_exotic_coin':            True,                       # alchemist: do exotic coin experiments
    'transmute_legendary':              True,                       # alchemist: transmute legendary chests
    'transmute_epic':                   True,                       # alchemist: transmute epic chests
    'transmute_rare':                   True,                       # alchemist: transmute rare chests
    'transmute_uncommon':               True,                       # alchemist: transmute uncommon chests

    # Battle screen
    'bag_open_chests':                  True,                       # bag: open chests
    'upgrade_order':                    'slot 1,slot 2,slot 3,slot 4,slot 5, guardian, specials',
    'upgrade_mode':                     2,                          # set upgrade amount for heroes
    'battle_boss_retry':                5,                          # set minimum battle duration before retrying boss

    # Exotic Merchant
    'sell_scroll_of_speed':             True,                       # 80 exotic coins
    'sell_scroll_of_damage':            True,                       # 80 exotic coins
    'sell_scroll_of_health':            True,                       # 80 exotic coins
    'sell_midas_touch':                 True,                       # 70 exotic coins
    'sell_pouch_of_gold':               True,                       # 10 exotic coins
    'sell_bucket_of_gold':              True,                       # 35 exotic coins
    'sell_crate_of_gold':               True,                       # 65 exotic coins
    'sell_barrel_of_gold':              True,                       # 130 exotic coins
    'sell_drums_of_war':                True,                       # 270 exotic coins
    'sell_dragon_armor':                True,                       # 180 exotic coins
    'sell_guardians_rune':              True,                       # 50 exotic coins
    'sell_totem_of_agony':              True,                       # 150 exotic coins
    'sell_totem_of_annihilation':       True,                       # 240 exotic coins

    # Garage
    'wm_fortress_upgrade':              True,
    'wm_fortress_blueprints':           True,
    'wm_fortress_rarity':               True,
    'wm_thunderclap_upgrade':           True,
    'wm_thunderclap_blueprints':        True,
    'wm_thunderclap_rarity':            True,
    'wm_firecracker_upgrade':           True,
    'wm_firecracker_blueprints':        True,
    'wm_firecracker_rarity':            True,
    'wm_aegis_upgrade':                 True,
    'wm_aegis_blueprints':              True,
    'wm_aegis_rarity':                  True,
    'wm_harvester_upgrade':             True,
    'wm_harvester_blueprints':          True,
    'wm_harvester_rarity':              True,
    'wm_cloudfist_upgrade':             True,
    'wm_cloudfist_blueprints':          True,
    'wm_cloudfist_rarity':              True,
    'wm_hunter_upgrade':                True,
    'wm_hunter_blueprints':             True,
    'wm_hunter_rarity':                 True,
    'wm_goliath_upgrade':               True,
    'wm_goliath_blueprints':            True,
    'wm_goliath_rarity':                True,
    'wm_judgement_upgrade':             True,
    'wm_judgement_blueprints':          True,
    'wm_judgement_rarity':              True,
    'wm_curator_upgrade':               True,
    'wm_curator_blueprints':            True,
    'wm_curator_rarity':                True,
    'wm_sentinel_upgrade':              True,
    'wm_sentinel_blueprints':           True,
    'wm_sentinel_rarity':               True,
    'wm_talos_upgrade':                 True,
    'wm_talos_blueprints':              True,
    'wm_talos_rarity':                  True,
    'wm_earthshatterer_upgrade':        True,
    'wm_earthshatterer_blueprints':     True,
    'wm_earthshatterer_rarity':         True,

    # Guild
    'guild_bank':                       True,                       # visit guild bank
    'guild_bank_donate':                True,                       # donate leftover guild coins to guild bank
    'guild_hall':                       True,                       # visit guild hall
    'guild_autoaccept':                 True,                       # auto accept guild applications

    # Magic Quarter
    'guardian_vermilion_train':         True,                       # enlighten vermilion (uses dust)
    'guardian_vermilion_enlighten':     True,                       # enlighten vermilion (uses dust)
    'guardian_vermilion_evolve':        True,                       # evolve vermilion (uses dust)
    'guardian_vermilion_chaosrift':     True,                       # increase vermilion holy damage (uses orbs of light)
    'guardian_vermilion_rarity':        True,                       # increase vermilion rarity (uses contracts)
    'guardian_grace_train':             True,                       # enlighten grace (uses dust)
    'guardian_grace_enlighten':         True,                       # enlighten grace (uses dust)
    'guardian_grace_evolve':            True,                       # evolve grace (uses dust)
    'guardian_grace_chaosrift':         True,                       # increase grace holy damage (uses orbs of light)
    'guardian_grace_rarity':            True,                       # increase grace rarity (uses contracts)
    'guardian_ankaa_train':             True,                       # enlighten ankaa (uses dust)
    'guardian_ankaa_enlighten':         True,                       # enlighten ankaa (uses dust)
    'guardian_ankaa_evolve':            True,                       # evolve ankaa (uses dust)
    'guardian_ankaa_chaosrift':         True,                       # increase ankaa holy damage (uses orbs of light)
    'guardian_ankaa_rarity':            True,                       # increase ankaa rarity (uses contracts)
    'guardian_azhar_train':             True,                       # enlighten azhar (uses dust)
    'guardian_azhar_enlighten':         True,                       # enlighten azhar (uses dust)
    'guardian_azhar_evolve':            True,                       # evolve azhar (uses dust)
    'guardian_azhar_chaosrift':         True,                       # increase azhar holy damage (uses orbs of light)
    'guardian_azhar_rarity':            True,                       # increase azhar rarity (uses contracts)

    # Map
    'map_order':                        'mystery,dragon,monster,naval,scout,war,adventure', # the order to play map missions

    # Shop
    'buy_amulet_of_conquest':           False,
    'buy_amulet_of_the_sky':            False,
    'buy_amulet_of_knowledge':          False,
    'buy_amulet_of_war':                False,
    'buy_amulet_of_power':              False,
    'buy_amulet_of_midas':              False,
    'buy_amulet_of_alchemy':            False,
    'buy_amulet_of_cartography':        False,
    'buy_amulet_of_exploration':        False,
    'buy_amulet_of_greed':              False,
    'buy_amulet_of_the_quartermaster':  False,
    'buy_amulet_of_the_pioneers':       False,
    'buy_amulet_of_liberation':         False,
    'buy_amulet_of_production':         False,
    'buy_amulet_of_clarity':            False,
    'buy_amulet_of_astrology':          False,
    'buy_amulet_of_the_seven':          False,
    'buy_amulet_of_tinkering':          False,
    'buy_amulet_of_insight':            False,
    'buy_amulet_of_luck':               False,
    'buy_amulet_of_the_king':           False,
    'buy_amulet_of_the_queen':          False,
    'buy_amulet_of_speed':              False,
    'buy_amulet_of_damage':             False,
    'buy_amulet_of_health':             False,

    # Temple of eternals
    'jump_percentage':                  400,                        # temple of eternals: jump percentage
    'jump_temple_token':                800,                        # temple of eternals: percentage to use temple tokens

    'version':                          1                           # config version on the end
}
config_file: str = 'bot_settings.json'
config_panel_vars = {}
config_comboboxes = {}
current_tab = None

def checkbox(**args) -> None:
    global config_panel_vars

    column = args.get('column', 0)
    row = args.get('row', 0)
    tab = args.get('tab', current_tab)
    text = args.get('text', None)
    varname = args.get('varname', None)
    if not tab or not text or not varname:
        return

    config_panel_vars.update({varname: tk.IntVar(value=config.get(varname, 0))})
    tk.Checkbutton(tab, text=text, variable=config_panel_vars.get(varname, 0), onvalue=True, offvalue=False).grid(row=row, column=column, padx=5, pady=2, sticky='nsw')

def combobox(**args) -> None:
    global config_comboboxes

    row = args.get('row', 0)
    tab = args.get('tab', current_tab)
    text = args.get('text', None)
    values = args.get('values', None)
    varname = args.get('varname', None)
    if not tab or not text or not values or not varname:
        return

    label(text=text, row=row)
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

        if conf_version != file_version:
            config_page()
    else:
        config_save()

def config_page() -> None:
    """
    Settings dialog
    """
    global config_panel_vars, current_tab

    c = tk.Tk()
    c.title('Firestone Bot Configuration')
    c.wm_attributes('-topmost', True)

    style = ttk.Style()
    style.theme_use('xpnative')
    style.configure('LeftTabs.TNotebook', tabposition='wn')
    style.configure('LeftTabs.TNotebook.Tab', width=-20, anchor='e', padding=(10, 8))
    #style.configure('TFrame', background='white')
    style.configure('TLabel', background='black', foreground='white')

    menu_frame = ttk.Frame(c, padding=10)
    menu_frame.pack(side=tk.LEFT, fill=tk.Y)
    tabs = ttk.Notebook(menu_frame, style='LeftTabs.TNotebook')
    tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
    button_frame = ttk.Frame(menu_frame, padding=(0, 5, 0, 0))
    button_frame.pack(side=tk.BOTTOM, fill=tk.X)
    tk.Button(button_frame, text='Save', command=config_save, bg='green', fg='white').pack(side=tk.LEFT, padx=(10,5), fill=tk.X, expand=True)
    tk.Button(button_frame, text='Exit', command=c.destroy, bg='red', fg='white').pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)

    current_tab = ttk.Frame(tabs, padding=10)
    tabs.add(current_tab, text='System')
    current_tab.grid_columnconfigure(1, minsize=400, weight=0)
    input_text(current_tab, 'Logfile', 0, 'logfile')
    input_text(current_tab, 'Ollama URL', 1, 'ollama_url', ('<Return>', 'ollama_url_verify'))
    input_text(current_tab, 'Ollama Model', 2, 'ollama_model', ('<Return>', 'ollama_model_verify'))
    input_text(current_tab, 'Tracker file', 3, 'tracker_file')
    input_number(current_tab, 'Page Wait Time', 4, 'wait_page', 1, 30, 0.01)
    slider(current_tab, 'Min match score', 5, 'min_score', 0.8, 1)

    values = []
    monitors = mss.MSS().monitors[1::]
    for idx, monitor in enumerate(monitors):
        text = f'Display {idx + 1}: {monitor['name']} @ {monitor['width']}x{monitor['height']}'
        if monitor['is_primary']:
            text += ' (primary)'
        values.append(text)
    combobox(text='Monitor', row=6, varname='monitor', values=values)

    current_tab = ttk.Frame(tabs, padding=10)
    tabs.add(current_tab, text='Alchemist')
    label(text='Experiments')
    checkbox(text='Dragon Blood', row=1, varname='alchemist_dragon_blood')
    checkbox(text='Strange Dust', row=1,varname='alchemist_strange_dust', column=2)
    checkbox(text='Exotic Coin', row=1, varname='alchemist_exotic_coin', column=4)

    label(text='Transmute Chests', row=2)
    checkbox(text='Legendary', row=3, varname='transmute_legendary')
    checkbox(text='Epic', row=3, varname='transmute_epic', column=2)
    checkbox(text='Rare', row=3, varname='transmute_rare', column=4)
    checkbox(text='Uncommon', row=3, varname='transmute_uncommon', column=8)

    current_tab = ttk.Frame(tabs, padding=10)
    tabs.add(current_tab, text='Battle Screen')
    values = ['Upgrade x1','Upgrade x10','Upgrade x100','Next milestone','Upgrade max']
    combobox(text='Upgrade mode', row=0, varname='upgrade_mode', values=values)

    upgrade_types = ['slot 1', 'slot 2', 'slot 3', 'slot 4', 'slot 5', 'guardian', 'specials']
    listbox(current_tab, 'Upgrade order', 1, 'upgrade_order', upgrade_types)
    input_number(current_tab, 'Boss retry', 20, 'battle_boss_retry', 0, 60, 0.1)

    current_tab = ttk.Frame(tabs, padding=10)
    tabs.add(current_tab, text='Exotic Merchant')
    label(text='Sell items')
    idx = 1
    offset = 0
    for name, _ in config.items():
        if name.startswith('sell_'):
            text = name[5::].replace('_', ' ').capitalize()
            checkbox(text=text, row=idx, varname=name, column=offset)
            offset += 2
            if offset == 6:
                idx += 1
                offset = 0

    current_tab = ttk.Frame(tabs, padding=10)
    tabs.add(current_tab, text='Garage')
    machines = ['aegis', 'cloudfist', 'curator', 'earthshatterer', 'firecracker', 'fortress', 'goliath', 'harvester', 'hunter', 'judgement', 'sentinel', 'talos', 'thunderclap']
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
    guardians = ['vermilion', 'grace', 'ankaa', 'azhar']
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
    mission_types = ['adventure', 'dragon', 'monster', 'mystery', 'naval', 'scout', 'titan', 'war']
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
    input_number(current_tab, 'Jump percentage', 0, 'jump_percentage', 0, 100000000000)
    input_number(current_tab, 'Use temple token at', 1, 'jump_temple_token', 0, 100000000000)

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

def input_text(tab, text:str, row: int, varname: str, on_update: Union[None, Tuple[str, str]] = None) -> None:
    global config_panel_vars

    label(text=text, row=row)
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
    if not tab or not text:
        return

    ttk.Label(tab, text=text).grid(row=row, column=column, columnspan=columnspan, pady=5, sticky='nsew', ipadx=5)

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

    url = f'{config_panel_vars.get('ollama_url').get().rstrip('/')}/api/tags'
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

    url = f'{config_panel_vars.get(varname).get().rstrip('/')}/api/version'
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