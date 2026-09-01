"""
Configuration related stuff
"""
import json
import os
import tkinter as tk
from tkinter import ttk

from typing import Any, ClassVar, Dict, List, Optional, Tuple, Union

import mss
import mss.tools

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
    'upgrade_slot1':                    True,                       # Upgrade leader
    'upgrade_slot2':                    True,                       # Upgrade hero in slot 2
    'upgrade_slot3':                    True,                       # Upgrade hero in slot 3
    'upgrade_slot4':                    True,                       # Upgrade hero in slot 4
    'upgrade_slot5':                    True,                       # Upgrade hero in slot 5
    'upgrade_guardian':                 True,                       # Upgrade guardian
    'upgrade_specials':                 True,                       # Upgrade specials
    'upgrade_mode':                     2,                          # check_upgrade: set upgrade amount for heroes

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

    'dummy':                            0                           # dummy on the end
}
config_file: str = 'bot_settings.json'
config_panel_vars = {}
config_comboboxes = {}

def checkbox(tab, text, row, varname, column_start:int = 0) -> None:
    global config_panel_vars

    label(tab, text, row, column_start)
    config_panel_vars.update({varname: tk.IntVar(value=config[varname])})
    tk.Checkbutton(tab, variable=config_panel_vars[varname], onvalue=True, offvalue=False).grid(row=row, column=column_start + 1, padx=5, pady=2, sticky='nsw')

def combobox(tab, text, row, varname, values) -> None:
    global config_comboboxes

    label(tab, text, row)
    config_panel_vars.update({varname: tk.IntVar(value=config[varname])})
    config_comboboxes.update({varname: ttk.Combobox(tab, state='readonly', values=values)})
    config_comboboxes[varname].grid(row=row, column=1, columnspan=20, padx=5, pady=5, sticky='nsew', ipadx=5)
    config_comboboxes[varname].current(config[varname])
    config_comboboxes[varname].bind('<<ComboboxSelected>>', lambda e: combobox_event(e, varname))

def combobox_event(event, varname) -> None:
    global config_comboboxes, config_panel_vars

    if event:
        pass

    config_panel_vars.update({varname: tk.IntVar(value=config_comboboxes[varname].current())})

def config_load() -> None:
    """ Load config """
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                config.update(loaded_config)
        except Exception as e:
            Debug.error(f'[Core] Unable to load configuration\n{e}')
    else:
        config_save()

def config_page() -> None:
    """
    Settings dialog
    """
    global config_panel_vars

    c = tk.Tk()
    c.title('Firestone Bot Configuration')
    style = ttk.Style()
    style.configure('LeftTabs.TNotebook', tabposition='wn')
    style.configure('LeftTabs.TNotebook.Tab', width=-20, anchor='e', padding=(10, 8))
    style.configure('TFrame', background='white')

    menu_frame = ttk.Frame(c, padding=10)
    menu_frame.pack(side=tk.LEFT, fill=tk.Y)
    tabs = ttk.Notebook(menu_frame, style='LeftTabs.TNotebook')
    tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
    button_frame = ttk.Frame(menu_frame, padding=(0, 5, 0, 0))
    button_frame.pack(side=tk.BOTTOM, fill=tk.X)
    tk.Button(button_frame, text='Save', command=config_save, bg='green', fg='white').pack(side=tk.LEFT, padx=(10,5), fill=tk.X, expand=True)
    tk.Button(button_frame, text='Exit', command=c.destroy, bg='red', fg='white').pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)

    tab1 = ttk.Frame(tabs, padding=10)
    tab2 = ttk.Frame(tabs, padding=10)
    tab3 = ttk.Frame(tabs, padding=10)
    tab4 = ttk.Frame(tabs, padding=10)
    tab5 = ttk.Frame(tabs, padding=10)
    tab6 = ttk.Frame(tabs, padding=10)
    tab7 = ttk.Frame(tabs, padding=10)
    tab8 = ttk.Frame(tabs, padding=10)
    tab9 = ttk.Frame(tabs, padding=10)
    tab10 = ttk.Frame(tabs, padding=10)

    tabs.add(tab1, text='System')
    tab1.grid_columnconfigure(1, minsize=400, weight=0)
    input_text(tab1, 'Logfile', 0, 'logfile')
    input_text(tab1, 'Ollama URL', 1, 'ollama_url')
    input_text(tab1, 'Ollama Model', 2, 'ollama_model')
    input_text(tab1, 'Tracker file', 3, 'tracker_file')
    input_number(tab1, 'Page Wait Time', 4, 'wait_page', 1, 30, 0.01)
    slider(tab1, 'Min match score', 5, 'min_score', 0.8, 1)

    values = []
    monitors = mss.MSS().monitors[1::]
    for idx, monitor in enumerate(monitors):
        text = f'Display {idx + 1}: {monitor['name']} @ {monitor['width']}x{monitor['height']}'
        if monitor['is_primary']:
            text += ' (primary)'
        values.append(text)
    combobox(tab1, 'Monitor', 6, 'monitor', values)

    tabs.add(tab2, text='Alchemist')
    label(tab2, 'Experiments', 0)
    checkbox(tab2, 'Dragon Blood', 1,'alchemist_dragon_blood')
    checkbox(tab2, 'Strange Dust', 1,'alchemist_strange_dust', 2)
    checkbox(tab2, 'Exotic Coin', 1,'alchemist_exotic_coin', 4)

    label(tab2, 'Transmute Chests', 2)
    checkbox(tab2, 'Legendary', 3,'transmute_legendary')
    checkbox(tab2, 'Epic', 3,'transmute_epic', 2)
    checkbox(tab2, 'Rare', 3,'transmute_rare', 4)
    checkbox(tab2, 'Uncommon', 3,'transmute_uncommon', 8)

    tabs.add(tab3, text='Battle Screen')
    values = ['Upgrade x1','Upgrade x10','Upgrade x100','Next milestone','Upgrade max']
    combobox(tab3, 'Upgrade mode', 0, 'upgrade_mode', values)
    checkbox(tab3, 'Upgrade slot 1', 1,'upgrade_slot1')
    checkbox(tab3, 'Upgrade slot 2', 1,'upgrade_slot2', 2)
    checkbox(tab3, 'Upgrade slot 3', 1,'upgrade_slot3', 4)
    checkbox(tab3, 'Upgrade slot 4', 1,'upgrade_slot4', 6)
    checkbox(tab3, 'Upgrade slot 5', 2,'upgrade_slot5')
    checkbox(tab3, 'Upgrade guardian', 2,'upgrade_guardian', 2)
    checkbox(tab3, 'Upgrade specials', 2,'upgrade_specials', 4)

    tabs.add(tab4, text='Exotic Merchant')
    idx = 0
    offset = 0
    for name, _ in config.items():
        if name.startswith('sell_'):
            text = name.replace('_', ' ').capitalize()
            checkbox(tab4, text, idx, name, offset)
            offset += 2
            if offset == 6:
                idx += 1
                offset = 0

    tabs.add(tab5, text='Garage')
    machines = ['aegis', 'cloudfist', 'curator', 'earthshatterer', 'firecracker', 'fortress', 'goliath', 'harvester', 'hunter', 'judgement', 'sentinel', 'talos', 'thunderclap']
    for idx, machine in enumerate(machines):
        label(tab5, machine.capitalize(), idx)
        for offset, item in enumerate(['upgrade', 'blueprints', 'rarity']):
            varname = f'wm_{machine}_{item}'
            value = tk.IntVar(value=config[varname])
            config_panel_vars.update({varname: value})
            tk.Checkbutton(tab5, text=item.capitalize(), variable=config_panel_vars[varname], onvalue=1, offvalue=0).grid(row=idx, column=1+offset, padx=5, pady=2, sticky='nsw')

    tabs.add(tab6, text='Guild')
    checkbox(tab6, 'Visit guild bank', 0, 'guild_bank')
    checkbox(tab6, 'Donate guild tokens', 1, 'guild_bank_donate')
    checkbox(tab6, 'Visit guild hall', 2, 'guild_hall')

    tabs.add(tab7, text='Magic Quarter')
    guardians = ['vermilion', 'grace', 'ankaa', 'azhar']
    for idx, guardian in enumerate(guardians):
        label(tab7, guardian.capitalize(), idx)
        for offset, item in enumerate(['train', 'enlighten', 'evolve', 'chaosrift', 'rarity']):
            varname = f'guardian_{guardian}_{item}'
            value = tk.IntVar(value=config[varname])
            config_panel_vars.update({varname: value})
            item = 'chaos rift' if item=='chaosrift' else item
            config_panel_vars.update({varname: value})
            tk.Checkbutton(tab7, text=item.capitalize(), variable=config_panel_vars[varname], onvalue=1, offvalue=0).grid(row=idx, column=1+offset, padx=5, pady=2, sticky='nsw')

    tabs.add(tab8, text='Map')
    mission_types = ['adventure', 'dragon', 'monster', 'mystery', 'naval', 'scout', 'titan', 'war']
    missions_current = config['map_order'].split(',')
    label(tab8, 'Mission map order', 0)
    tk.Button(tab8, text="Up    ", command=lambda: listbox_event(None, map_list, 'up', 'map_order')).grid(row=3, column=0, padx=5, pady=2, sticky='nsew')
    tk.Button(tab8, text="Toggle", command=lambda: listbox_event(None, map_list, 'dblclick', 'map_order')).grid(row=4, column=0, padx=5, pady=2, sticky='nsew')
    tk.Button(tab8, text="Down  ", command=lambda: listbox_event(None, map_list, 'down', 'map_order')).grid(row=5, column=0, padx=5, pady=2, sticky='nsew')

    map_list = tk.Listbox(tab8, selectmode=tk.SINGLE, activestyle='none', exportselection=0, height=len(mission_types))
    map_list.grid(row=0, column=1, rowspan=len(mission_types), padx=5, pady=2, sticky='nsw')
    idx = 0
    for m in missions_current:
        name = m.strip().lower()
        if name not in mission_types:
            continue
        mission_types.remove(name)
        map_list.insert(idx, name)
        map_list.itemconfig(idx, fg='green')
        idx += 1
    for mission in mission_types:
        map_list.insert(idx, mission)
        map_list.itemconfig(idx, fg='red')
        idx += 1
    map_list.bind("<Double-1>", lambda e: listbox_event(e, map_list, 'dblclick', 'map_order'))

    tabs.add(tab9, text='Shop')
    idx = 0
    offset = 0
    for name, _ in config.items():
        if name.startswith('buy_'):
            text = name[3::].replace('_', ' ').strip().capitalize()
            checkbox(tab9, text, idx, name, offset)
            offset += 2
            if offset == 6:
                idx += 1
                offset = 0

    tabs.add(tab10, text='Temple of eternals')
    tab10.grid_columnconfigure(1, minsize=400, weight=0)
    input_number(tab10, 'Jump percentage', 0, 'jump_percentage', 0, 100000000000)
    input_number(tab10, 'Use temple token at', 1, 'jump_temple_token', 0, 100000000000)

    c.mainloop()

def config_save() -> None:
    """ Save config """
    global config

    try:
        if config_panel_vars:
            for name, value in config_panel_vars.items():
                config.update({name: value.get()})

        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(config, indent=4))
    except Exception as e:
        Debug.error(f'[Core] Unable to write configuration\n{e}')

def input_number(tab, text, row, varname, min_val, max_val, increment = 1) -> None:
    global config_panel_vars

    label(tab, text, row)
    config_panel_vars.update({varname: tk.DoubleVar(value=config[varname])})
    tk.Spinbox(tab, from_=min_val, to=max_val, increment=increment, textvariable=config_panel_vars[varname], width=6).grid(row=row, column=1, padx=5, pady=2, sticky='nsew')

def input_text(tab, text, row, varname) -> None:
    global config_panel_vars

    label(tab, text, row)
    config_panel_vars.update({varname: tk.StringVar(value=config[varname])})
    tk.Entry(tab, textvariable=config_panel_vars[varname]).grid(row=row, column=1, padx=5, pady=2, sticky='nsew')

def label(tab, text, row, column = 0, columnspan = 1) -> None:
    tk.Label(tab, text=text, bg='black', fg='white').grid(row=row, column=column, columnspan=columnspan, pady=5, sticky='nsew', ipadx=5)

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

def slider(tab, text, row, varname, min_val, max_val) -> None:
    global config_panel_vars

    label(tab, text, row)
    config_panel_vars.update({varname: tk.DoubleVar(value=config[varname])})
    tk.Scale(tab, from_=min_val, to=max_val, orient=tk.HORIZONTAL, resolution=0.01, variable=config_panel_vars[varname]).grid(row=row, column=1, padx=5, pady=2, sticky='nsew')

config_load()
if __name__ == '__main__':
    config_page()