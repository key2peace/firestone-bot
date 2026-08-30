"""
Task Logic Subroutines for Firestone Bot Gameplay Automation.

Provides alphabetically organized gameplay handlers dispatched dynamically
via the main automation loop. All visual state checks, hardware inputs,
and lifecycle guards are handled natively through the custom core framework.
"""
import os
import random
import re
import time

from custom_core import (
    click,
    color_at,
    color_name,
    colormap,
    config,
    #dailies,
    Debug,
    drag_drop,
    duration_text,
    get_next_reset,
    get_pixel_color,
    #get_suffix_rank,
    get_timeout,
    grab_screen_to_mat,
    main_finished,
    mouse_down,
    mouse_up,
    move_to,
    my_round,
    parse_ui_timeout,
    pause_off,
    pause_on,
    press_key,
    Region,
    screen,
    sleep,
    timeouts
)

from page_logic import (
    page_wait
)

flipper: bool = True
party_coords = {}

def alchemist(trigger: bool = False) -> int:
    """
    Execute the Alchemist navigational cleanup subroutine.
    """
    timestamps = []
    if trigger:
        press_key('a')

    if not page_wait('alchemist'):
        return -1

    # experiments
    coords = {
        'Dragon blood': (800, config['alchemist_dragon_blood']),
        'Strange Dust': (1170, config['alchemist_strange_dust']),
        'Exotic coin': (1540, config['alchemist_exotic_coin'])
    }

    for name, (x, upgrade) in coords.items():
        ts = Region(x, 675, 280, 30).text('', colormap['white'])
        if ts == 'Completed':
            Debug.history(f'Completed {name} Experiment')
            click((x + 50, 800))
            sleep(1)
        elif color_at(x + 50, 780) == 'yellow':
            Debug.history(f'Completed {name} Experiment for free')
            click((x + 50, 780))
            sleep(1)
        elif re.search(r'(\d{2})?:?(\d{1,2}):(\d{2})', ts.lower()):
            ts = parse_ui_timeout(ts)
            if ts:
                timestamps.append(ts)

        if upgrade and color_at(x + 50, 780) == 'green':
            Debug.history(f'Starting {name} Experiment')
            click((x + 50, 800))
            sleep(1)
            ts = Region(x, 675, 280, 30).text('', colormap['white'])
            if re.search(r'(\d{2})?:?(\d{1,2}):(\d{2})', ts.lower()):
                ts = parse_ui_timeout(ts)
                if ts:
                    timestamps.append(ts)

    # transmute
    if config['transmute_legendary'] or config['transmute_epic'] or config['transmute_rare'] or config['transmute_uncommon']:
        click((1400, 130))
        coords = {
            'legendary': (520, config['transmute_legendary']),
            'epic':      (680, config['transmute_epic']),
            'rare':      (840, config['transmute_rare']),
            'uncommon':  (1000, config['transmute_uncommon'])
        }

        for name, (y, obtain) in coords.items():
            if obtain:
                while color_at(1800, y) == 'green':
                    sleep(0.5)
                    Debug.history(f'Transmuting a {name} chest')
                    click((1800, y))
                    move_to((1840, y))

    click((1840, 55))
    if timestamps:
        return min(timestamps) - 180
    return get_timeout(1800)

def arena_of_kings(trigger: bool = False) -> int:
    """
    Execute the Arena of Kings navigational cleanup subroutine.
    """
    if trigger:
        press_key('k')

    if not page_wait('arena_of_kings'):
        return -1

    click((1855, 115))
    return 0

def bag(trigger: bool = False) -> int:
    """
    Cleanup the bag
    """
    if trigger:
        pass

    press_key('b')
    if not page_wait('bag'):
        return -1

    if config['bag_open_chests']:
        click((1460, 300)) # Chests
        sleep(1)

        # save first chests for dailies
        x = 1700 if trigger else 1570

        while not get_pixel_color(x, 200) == (158, 128, 103):
            Debug.history('Opening bag')
            click((x, 200))
            sleep(1)

            for x2 in range(1400, 500, -225):
                if color_at(x2, 850) == 'green':
                    click((x2, 850))
                    break
                if color_at(x2, 960) == 'green':
                    click((x2, 960))
                    break

            while not color_at(1840, 55) in ['white', 'white_overlayed']:
                pass
            sleep(1)
            if color_at(1040, 890) == 'green':
                Debug.info("Picked up new items in chests")
                click((1040, 890))

            click((1840, 55))
            sleep(1)
    click((1870, 70))
    return get_timeout(3600)

def battle_pass(trigger: bool = False) -> int:
    """
    Check if we got a baatle pass to claim
    """
    if trigger:
        pass

    if color_at(1890, 800) == 'red':
        click((1860, 814))
        sleep(1)
        click((1110, 60))

        for x in range(390, 1820, 10):
            if color_at(x, 560) == 'green':
                Debug.history('Picking up golden battle pass reward')
                sleep(0.3)
                click((x, 560))
            if color_at(x, 1000) == 'green':
                Debug.history('Picking up battle pass reward')
                sleep(0.3)
                click((x, 1000))
        sleep(0.3)

        click((1840, 55))

    return get_timeout(3600)

def character_quests(trigger: bool = False) -> int:
    """
    Execute the quest completion and collection protocol.

    Navigates through multiple quest category tabs and sequentially triggers
    claim buttons using fixed index ranges to collect accumulated rewards.
    """
    if trigger:
        press_key('q')
        sleep(2)
        click((1500, 40))

    if not page_wait('character_quests'):
        return -1

    for x in [760, 1170]:
        quest_type = 'daily' if x == 760 else 'weekly'
        if quest_type == 'weekly' and not color_at(1360, 90) == 'red':
            break

        click((x, 130))
        sleep(0.3)
        while color_at(1560, 300) == 'green':
            Debug.history(f'Claiming {quest_type} quest')
            click((1560, 300))
            move_to((1620, 300))
            sleep(1)
            if color_at(1260, 730) == 'green':
                click((1260, 730))
                sleep(1)

    click((1850, 76))
    if trigger:
        return get_timeout(60)
    return 0

def character_talents(trigger: bool = False) -> int:
    """
    Upgrade talents
    """
    if trigger:
        press_key('q')
        sleep(2)
        click((680, 40))

    if not page_wait('character_talents'):
        return -1

    bubble = 'images/tasks/character/talents_bubble.png'
    _area = Region(470, 170, 1340, 860)
    counter = 0
    clicked = False
    while True:
        match = _area.exists(bubble)
        if match:
            Debug.history('Selecting talent')
            match.click()
            match.wait_vanish()
            while color_at(1032, 853) == 'green_talents':
                Debug.history('Upgrading talent')
                click((1020, 866))
                move_to((1100, 866))
                clicked = True
                sleep(1)
            click((1250, 320))
            break
        drag_drop((950, 990), (950, 590))
        sleep(1)
        counter += 1
        if counter > 10:
            for _ in range(1, counter):
                drag_drop((950, 590), (950, 990))
            break
    if clicked:
        click((1650, 980))

    click((1850, 80))
    return 0

def check_heroes(trigger: bool = False) -> int:
    """
    Execute sequential hero upgrades
    """
    if trigger:
        pass

    clicked: bool = False
    x: int = 960
    upgraded: int = 1
    while upgraded > 0:
        upgraded = 0
        for slot, name in enumerate(party_coords):
            if name=='upgrade':
                continue
            elif name=='guardian':
                if not config['upgrade_guardian']:
                    continue
            elif name=='specials':
                if not config['upgrade_specials']:
                    continue
            else:
                if slot < 5 and not config[f'upgrade_slot{slot + 1}']:
                    continue

            x, y = party_coords[name]
            if color_at(x, y + 60) != 'yellow':
                continue

            Debug.history(f'Upgrading {name}')
            move_to((x, y + 70))
            mouse_down()
            while color_at(x, y + 60) != 'grey':
                pass
            mouse_up()
            upgraded += 1
            clicked = True
    if clicked:
        move_to((x, 1080))
    return get_timeout(5)

def check_mail(trigger: bool = False) -> int:
    """
    Check if we got mail
    """
    if trigger:
        pass

    if color_at(110, 590) == 'red':
        click((60, 620))
        sleep(1)
        while not color_at(1600, 980) == 'lightbrown':
            if color_at(1320, 830) == 'green':
                Debug.history('Claiming reward from mail')
                click((1320, 840))
                sleep(0.3)
                click((1190, 720))
                sleep(0.3)
            click((1600, 980))
            sleep(0.3)
        click((1650, 40))

    return get_timeout(300)

def check_party(trigger: bool = False) -> int:
    """
    Check the setup of the party
    """
    global party_coords

    if trigger:
        pass

    area = Region(10, 910, 1900, 160)
    max_x: int = 0
    coords = {}

    for root, _, files in os.walk('images/heroes'):
        files = [f for f in files if f.lower().endswith('.png')]
        if not files:
            continue
        for filename in files:
            filepath = os.path.join(root, filename)
            name = filename.split('.')[0].split('_')[0]
            if name in ['armor', 'damage', 'gold', 'health']:
                name = 'specials'
            elif name in ['ankaa', 'azhar', 'grace', 'vermilion']:
                name = 'guardian'
            m = area.exists(filepath)
            if m:
                x = m.get_x() + m.get_w() + 10
                y = m.get_y()
                max_x = x if x > max_x else max_x
                coords[name] = (x, y)

    coords['upgrade'] = (max_x + 80, y)
    party_coords = dict(sorted(coords.items(), key=lambda item: item[1][0]))
    Debug.info(f'{party_coords}')
    return time.time() * 2

def check_taskcount(trigger: bool = False) -> int:
    """
    Check amount of tasks, scroll to check if we can find more non timeouted ones in the list
    """
    global flipper

    if trigger:
        pass

    if color_at(110, 190) == 'red':
        task_count = Region(90, 160, 50, 38).get_number()
        if int(task_count) > 3:
            # drag around the area to reveal task images
            x = main_finished.get_x()+50
            y1 = main_finished.get_y()+200
            y2 = y1 + 320

            if flipper:
                drag_drop((x, y1), (x, y2))
                move_to((x + 160, y2))
            else:
                drag_drop((x, y2), (x, y1))
                move_to((x + 160, y1))

            flipper = not flipper

    return get_timeout(120)

def check_upgrade(trigger: bool = False) -> int:
    """
    Validate and enforce the global hero upgrade multiplier mode via OCR.

    Scans the primary upgrade interaction canvas text and sequentially clicks
    the selector until the screen state matches the target configuration mode.
    """
    if trigger:
        pass

    target_mode = str(config['upgrade_mode']).lower()
    x, y = party_coords['upgrade']
    area = Region(x, y, 250, 160)

    # Cycle selector modes inline until text configuration criteria are met
    while target_mode not in area.text('', colormap['white']).lower():
        area.click()
        move_to((area.get_center().get_x(), 1080))

    return time.time() * 2

def crazygames_check(trigger: bool = False) -> int:
    """
    Check for crazygames specific elements
    """
    if trigger:
        pass

    # Crazygames maximize game screen button
    img = screen.exists('images/misc/gamebar_maximize.png')
    if img:
        Debug.history('[Crazygames] Going fullscreen')
        img.click()
        img.wait_vanish()

    # Crazygames gamebar
    if color_at(735, 1060) == 'gamebar':
        Debug.history('[Crazygames] Disabling bottom gamebar')
        click((960, 1050))

    return get_timeout(time.time())

def crazygames_error(trigger: bool = False) -> int:
    """
    Check for crazygames error screen
    """
    if trigger:
        pass

    if color_at(1080, 670) == 'purple':
        if Region(875, 650, 170, 40).text('', colormap['white']) == 'Reload game':
            Debug.warn('Gamecrash detected. Preparing for web reload.')
            pause_on(True)
            press_key('f5')
            sleep(20)
            pause_off()

    return get_timeout(300)

def engineer(trigger: bool = False) -> int:
    """
    Execute the Engineer resource allocation routine.

    Interacts with the localized production interface before firing
    global exit anchors to restore primary canvas visibility.
    """
    if trigger:
        press_key('t')
        sleep(2)
        click((1280, 820))
        sleep(1)
        click((590, 520))

    if not page_wait('engineer'):
        return -1

    if color_at(1710, 740) == 'green':
        Debug.history('Picking up tools')
        click((1710, 740))

    click((1840, 55))
    return get_timeout(21600)

def engineer_garage(trigger: bool = False) -> int:
    """
    Process the garage page
    """
    if trigger:
        press_key('t')
        sleep(2)
        click((1280, 820))
        sleep(1)
        click((940, 520))

    if not page_wait('engineer_garage'):
        return -1

    machines = [
        'fortress',
        'thunderclap',
        'firecracker',
        'aegis',
        'harvester',
        'cloudfist',
        'hunter',
        'goliath',
        'judgement',
        'curator',
        'sentinel',
        'talos',
        'earthshatterer'
    ]

    items = {
        # name      x, amount
        'upgrade': (1290, 0),
        'blueprints': (1450, 0),
        'rarity': (1620, 0)
    }

    for item, (x, _) in items.items():
        for machine in machines:
            if config[f'wm_{machine}_{item}']:
                click((x, 150))
                sleep(1)
                amount = Region(1580, 20, 116, 36).get_number()
                if amount:
                    items[item] = (x, amount)
                    break

    Debug.info(f'{items}')

    area = Region(0, 900, 1920, 180)
    tmp = {}
    min_level = 999
    for machine in machines:
        found = False
        for item, (_, _) in items.items():
            if config[f'wm_{machine}_{item}']:
                found = True
                break
        if not found:
            continue

        img = f'images/tasks/engineer/war_machines/{machine}.png'
        if not os.path.exists(img):
            continue
        m = area.exists(img)
        if m:
            level = Region(m.get_x() + 70, m.get_y() + m.get_h(), 64, 32).get_number()
            min_level = level if level < min_level else min_level
            Debug.info(f'{machine} ({level}) {m.get_score()}')
            tmp[machine] = level

    Debug.info(f'{tmp}')

    click((1840, 55))
    return get_next_reset()

def events(trigger: bool = False) -> int:
    """ Events handler """
    if trigger:
        pass

    if color_at(1900, 650) == 'white':
        click((1860, 690))

        if not page_wait('events'):
            return -1

        eventlist = {
            # mini events
            'stardust': 'mini',
            'primordial elements': 'mini',
            'ethereal miners': 'mini',
            'team effort': 'mini',
            'mechanical superiority': 'mini',
            'world domination': 'mini',
            'guardians of destiny': 'mini',
            'blessing of the eternals': 'mini',
            'champions of alandria': 'mini',
            'mass production': 'mini',
            'sigils of prophecy': 'mini',

            # calendar events
            'decorated heroes': 'calendar',
            'love is in the air': 'calendar',
            'nature\'s dance': 'calendar',
            'tropicana': 'calendar',
            'astral alignment': 'calendar',
            'trick or treat': 'calendar',
            'winter festival': 'calendar'
        }

        for y in [295, 480]:
            if not color_at(1470, y) == 'white':
                continue

            text = Region(530, y + 15, 890, 80).text('', colormap['yellow']).lower()
            if text not in eventlist:
                Debug.warn(f'\'{text}\' not defined in eventlist')
                continue

            click((950, y + 65))
            sleep(2)

            if color_at(1330, 25) == 'white':
                Debug.history(f'Checking {text} event')
                click((1150, 50))
                sleep(1)

                event_type = eventlist[text]
                if event_type == 'mini':
                    for y2 in [390, 640, 890]:
                        if color_at(1640, y2) == 'green':
                            Debug.history('Claiming reward')
                            click((1640, y2))
                elif event_type == 'calenda':
                    # these just collect stuff maybe setup preffered items to cash in
                    pass
                else:
                    Debug.warn('unsupported event type')

            click((1765, 100))
            sleep(1)

        click((1530, 50))

    return get_timeout(900)

def exotic_merchant(trigger: bool = False) -> int:
    """"
    Exotic Merchant
    """
    if trigger:
        pass

    press_key('x')
    if not page_wait('exotic_merchant'):
        return -1

    area = Region(790, 280, 1000, 795)

    # Sell items
    click((1120, 160))
    while not Region(1750, 220, 110, 42).text('x015', colormap['white']) == 'x50':
        click((1855, 240))

    drag_count = 0
    while drag_count < 2:
        for root, _, files in os.walk('images/tasks/exotic_merchant'):
            files = [f for f in files if f.lower().endswith('.png')]
            if not files:
                continue
            for filename in files:
                filepath = os.path.join(root, filename)
                name = filename[:-4]
                if not config[f'sell_{name}']:
                    continue
                m = area.exists(filepath)
                if not m:
                    continue
                x = m.get_x() + 140
                y = m.get_y() + 200
                while color_at(x, y) == 'green':
                    Debug.history(f'Selling {name}')
                    click((x + 10, y))
                    sleep(1)
        drag_drop((1690, 940), (1690, 380))
        drag_count += 1
        sleep(2)

    for _ in range(0, drag_count):
        drag_drop((1690, 380), (1690, 940))

    # Exotic upgrades
    click((1300, 160))
    while not Region(1750, 220, 110, 42).text('x015', colormap['white']) == 'x1':
        click((1855, 240))

    drag_count = 0
    while drag_count < 3:
        while True:
            pixels = grab_screen_to_mat(area)
            found = False
            for y in range(0, pixels.shape[0], 10):
                for x in [30, 400, 800]:
                    b_ch, g_ch, r_ch = pixels[y, x]
                    if color_name((r_ch, g_ch, b_ch)) == 'green':
                        found = True
                        break
                if found:
                    break
            if not found:
                break
            while color_at(x + 790, y + 280) == 'green':
                click((x + 790, y + 280))
                sleep(1)

        drag_drop((1690, 940), (1690, 380))
        drag_count += 1
        sleep(2)

    for _ in range(0, drag_count):
        drag_drop((1690, 380), (1690, 940))

    # Emblem market
    if color_at(1540, 125) == 'white':
        click((1470, 160))
        sleep(1)
        for y in [390, 560, 730]:
            if not color_at(627, y) == 'white':
                continue
            click((650, y +20))
            sleep(1)
            if not color_at(1250, 630) == 'green':
                continue
            click((1250, 630))

    click((1840, 55))
    return get_next_reset()

def guild(trigger: bool = False) -> int:
    """
    Walk the guild map
    """
    if trigger:
        pass

    click((1860, 430))      # Guild icon on main screen
    if not page_wait('guild_map'):
        return -1

    # guild bank
    if config['guild_bank'] and color_at(400, 875) == 'red':
        click((300, 700))       # Bank on guild map
        if not page_wait('guild_bank'):
            return -1
        if config['guild_bank_donate'] and color_at(1200, 750) == 'green':
            click((1130, 750))  # Max donation
        click((180, 450))       # Treasury
        click((180, 600))       # Bank log
        click((180, 800))       # Locker
        sleep(1)
        if color_at(1100, 840) == 'green':
            click((950, 940))   # Claim rewards
        click((1670, 50))

    # guild hall
    if config['guild_hall'] and color_at(1210, 585) == 'red':
        click((1070, 500))      # Guild hall
        if not page_wait('guild_hall'):
            return -1

        #guild_level = Region(400, 160, 300, 36).text('', colormap['white'])
        #members = Region(400, 260, 300, 36).text('', colormap['white'])

        click((180, 800))       # Guild log
        click((1670, 50))

    click((1840, 55))
    return get_timeout(7200)

def guild_arcanecrystal(trigger: bool = False) -> int:
    """
    Execute the Arcane Crystal interface routing subroutine.
    """
    if trigger:
        click((1860, 430))      # Guild icon on main screen
        if not page_wait('guild_map'):
            return -1

        click((1670, 890))
        sleep(2)

        amount = Region(1580, 20, 117, 37).get_number()
        amount = int(min(amount, 5))

        for _ in range(0, amount):
            if color_at(960, 960) == 'green':
                click((960, 960))
                move_to((1120, 960))
                start_loop = time.time()
                while time.time() - start_loop < 10 and not color_at(1050, 970) == 'green':
                    sleep(1)
            else:
                break

        click((1840, 55))
        sleep(1)

    click((1840, 55))
    return 0

def guild_awakening(trigger: bool = False) -> int:
    """
    Process awakening screen
    """
    if trigger:
        pass

    while color_at(1600, 600) == 'yellow':
        click((1800, 600))
        move_to((1880, 600))
        time_start = time.time()
        while time.time() - time_start < 6 and not color_at(1600, 600) == 'yellow':
            sleep(0.5)

    click((1840, 55))
    return 0

def guild_chaos_rift(trigger: bool = False) -> int:
    """
    Run chaos rift challenge.
    """
    if trigger:
        pass

    while color_at(1050, 970) == 'green':
        click((1050, 970))
        move_to((1200, 970))
        start_loop = time.time()
        while time.time() - start_loop < 5 and not color_at(1050, 970) == 'green':
            pass

    click((1840, 55))
    return 0

def guild_chaos_rift_supplies(trigger: bool = False) -> int:
    """
    Process ledra supplies
    """
    if trigger:
        pass

    while color_at(560, 820) == 'green':
        click((560, 820))
        move_to((480, 820))
        if color_at(1000, 680) == 'green':
            click((1000, 680))
            break

    click((1840, 55))
    return 0

def guild_expeditions(trigger: bool = False) -> int:
    """
    Execute sequentially coordinated inputs inside the Guild Expeditions panel.

    Processes an ordered array of screen coordinate nodes to advance active
    expedition pipelines with minimal state tracking.
    """
    if trigger:
        pass

    if not page_wait('guild_expeditions'):
        return -1

    timestamps = []
    click((1250,330))
    ts = Region(720, 320, 220, 50).text('1234567890:', colormap['white'])
    if ts:
        timeout = parse_ui_timeout(ts)
        if timeout:
            timestamps.append(timeout)
    click((1290, 330))
    click((1510, 70))
    if timestamps:
        return min(timestamps)
    return 0

def guild_forbidden_knowledge(trigger: bool = False) -> int:
    """
    Run forbidden knowledge circle
    """
    if trigger:
        pass

    for y_coords, name in [(350, 'Ledra'), (520, 'Yanamoth'), (680, 'Kramatak')]:
        click((1800, y_coords))

        available = Region(1600, 20, 100, 36).get_number()
        if not available:
            continue
        if name == 'Ledra': # Circle setup
            coords = [
                (1090, 75, 'Firestone finder'),
                (1320, 240, 'Guardian power'),
                (1090, 920, 'Attribute damage'),
                (600, 760, 'Team bonus'),
                (820, 920, 'Leadership'),
                (1320, 760, 'Attribute armor'),
                (1400, 500, 'Attribute health'),
                (540, 500, 'Rage heroes'),
                (600, 240, 'Mana heroes'),
                (820, 75, 'Energy heroes')
            ]
            color = 'blue_forbidden_knowledge'
        elif name == 'Yanamoth': # Triangle setup
            coords = [
                (960, 30, 'Raining gold'),
                (1120, 295, 'Guardian power'),
                (1200, 900, 'Attribute damage'),
                (710, 900, 'Team bonus'),
                (960, 900, 'Leadership'),
                (617, 566, 'Precision'),
                (1450, 900, 'Attribute armor'),
                (1300, 566, 'Attribute health'),
                (780, 295, 'Magic spells'),
                (460, 900, 'Fist fight')
            ]
            color = 'brown_forbidden_knowledge'
        elif name == 'Kramatak': # Square setup
            coords = [
                (710, 130, 'All main attribute'),
                (960, 130, 'Guardian power'),
                (1390, 605, 'Attribute damage'),
                (960, 835, 'Team bonus'),
                (1210, 835, 'Leadership'),
                (1390, 370, 'Attribute armor'),
                (1210, 130, 'Attribute health'),
                (520, 370, 'Tank specialization'),
                (520, 605, 'Healer specialization'),
                (710, 835, 'Damage specialization')
            ]
            color = 'blue'
        else:
            # for niceness of code
            continue

        while available:
            if available >= 50 and color_at(350, 910) == 'yellow':
                click((220, 910))
                sleep(0.3)
                if color_at(960, 890) == 'green':
                    Debug.history(f'- Recruiting {name}')
                    click((960, 890))
                    available -= 50

            for x, y, stat in coords:
                if not available:
                    break
                if color_at(x, y) == color:
                    click((x, y))
                    if color_at(1046, 750) == 'green':
                        Debug.history(f'- Upgrading {stat}')
                        click((1046, 750))
                        available -= 1
                    click((1260, 270))

    click((1840, 55))
    return 0

def guild_shop_pickaxe(trigger: bool = False) -> int:
    """
    Execute the Pickaxe tool allocation and interaction routine.

    Interacts with the localized mining area coordinates before triggering
    global exit anchors to return execution back to the primary canvas.
    """
    if trigger:
        pass

    if color_at(780, 770) == 'green':
        click((780, 770))

    click((1840, 55))
    return 0

def library_firestone_research(trigger: bool = False) -> int:
    """
    Manage the Firestone research pipeline lifecycle in two distinct phases.

    Phase 1 monitors and collects completed research projects utilizing rapid
    pixel color scans. Phase 2 processes active template research bubbles and
    executes screen drag operations to initialize new available projects.
    """
    if trigger:
        press_key('l')
        sleep(2)
        click((1810, 640))
        sleep(2)

    if not page_wait('library_firestone_research'):
        return -1

    available = 0
    timestamps = []

    for x_coords in [1280, 590]:
        color = color_at(x_coords, 965)
        if color in ['green', 'yellow']:
            available += 1
            click((x_coords, 980))
        elif color == 'lightbrown_research_nonfree':
            ts_area = Region(x_coords - 440, 1000, 300, 32)
            ts = ts_area.text('', colormap['white'])
            if re.search(r'^[\d:]+$', ts):
                timeout = parse_ui_timeout(ts)
                if timeout:
                    timestamps.append(timeout)
        else:
            available += 1

    drag_count = 0
    area = Region(0, 130, 1700, 770)
    while drag_count <= 3 and available:
        pixels = grab_screen_to_mat(area)
        found = False
        for x in range(0, pixels.shape[1], 10):
            count = 0
            for y in range(0, pixels.shape[0], 10):
                b_ch, g_ch, r_ch = pixels[y, x]
                if b_ch == 222 and g_ch == 73 and r_ch == 13:
                    count += 1
                    if count > 2:
                        found = True
                        break
            if found:
                break
        if found:
            click((x, y + 130))
            sleep(1)
            ts = Region(1050, 610, 300, 32).text('', colormap['green'])
            timeout = 0
            if re.search(r'^[\d:]+$', ts):
                timeout = parse_ui_timeout(ts)

            click((790, 720))
            if color_at(970, 660) == 'lightbrown_research_full':
                Debug.warn('[Firestone Research] Research slots full')
                click((1400, 350))
                click((1250, 200))
                break

            if timeout:
                timestamps.append(timeout)
            available -= 1
        else:
            drag_drop((800, 430), (200, 430))
            drag_count += 1
            sleep(1)

    if drag_count:
        for _ in range(1, drag_count):
            drag_drop((200, 430), (800, 430))

    click((1840, 55))
    if timestamps:
        return min(timestamps) - 181

    return get_timeout(600)

def library_meteorite_research(trigger: bool = False) -> int:
    """
    Execute the Meteorite Research.
    """
    if trigger:
        press_key('l')
        sleep(2)
        click((1810, 460))
        sleep(2)

    if not page_wait('library_meteorite_research'):
        return -1

    _area = Region(0, 130, 1600, 890)
    clicked = []
    items = _area.find_all('images/tasks/library/meteorite_circle.png')
    if items:
        for m in items:
            x = my_round(m.get_x())
            y = my_round(m.get_y())
            if (x,y) in clicked:
                continue
            clicked.append((x,y))
            m.click()
            m.wait_vanish()
            if color_at(1060, 770) == 'green':
                Debug.history('Performing research')
                click((1060, 770))
            click((1260, 280))

    click((1840, 55))
    return 0

def magic_quarter(trigger: bool = False) -> int:
    """
    Magic Quarter
    """
    if trigger:
        press_key('g')
        sleep(2)

    if not page_wait('magic_quarter'):
        return -1

    pos = {
        'vermilion': (735, 1000),
        'grace': (890, 1000),
        'ankaa': (1040, 1000),
        'azhar': (1190, 1000)
    }

    #dust = Region(1595, 20, 110, 36).get_number()
    tmp = {}
    for name, (x, y) in pos.items():
        if not color_at(x - 50, y - 50) == 'grey_magic_quarter':
            tmp[name] = (x, y)

    while True:
        current = Region(250, 830, 300, 60).text('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', colormap['brown']).lower()
        if current and current in pos:
            if current in tmp:
                del tmp[current]

            # General
            if config[f'guardian_{current}_train'] or config[f'guardian_{current}_enlighten']:
                click((1050, 150))
                sleep(0.3)
                if config[f'guardian_{current}_train'] and color_at(1090, 800) == 'green':
                    Debug.history(f'Training {current}')
                    click((1090,800))
                while config[f'guardian_{current}_enlighten'] and color_at(1590, 800) == 'green':
                    Debug.history(f'Enlightening {current}')
                    click((1590, 800))
                    move_to((1590, 900))
                    sleep(0.3)

            # Evolution - colorcheck disabled because of bug
            #if config[f'guardian_{current}_evolve'] and color_at(1265, 100) == 'white':
            click((1210, 150))
            sleep(0.3)
            if config[f'guardian_{current}_evolve'] and color_at(1220, 780) == 'green':
                Debug.history(f'Evolving {current}')
                click((1220, 780))
                sleep(10)

            # Chaos Rift
            if config[f'guardian_{current}_chaosrift'] and color_at(1435, 100) == 'white':
                click((1400, 150))
                sleep(0.3)
                while color_at(1630, 775) == 'green':
                    Debug.history(f'Increase {current}\'s holy damage')
                    click((1720, 760))
                    move_to((1720, 660))
                    sleep(0.3)

            # Guardian rarity
            if config[f'guardian_{current}_rarity'] and color_at(1600, 100) == 'white':
                click((1560, 150))
                sleep(0.3)
                if color_at(1365, 630) == 'green':
                    Debug.history(f'Increase {current}\'s rarity')
                    click((1365, 630))
                    sleep(10)

        if not tmp:
            break

        for _, (x, y) in tmp.items():
            click((x, y))
            break

    click((1840, 55))
    return 120

def map_campaign(trigger: bool = False) ->int:
    """
    Perform Campaign Task
    """
    if trigger:
        pass

    # Check if we can claim loot
    if color_at(80, 1000) == 'green':
        click((80, 1000))

    # Check for daily missions
    if color_at(1870, 990) == 'red':
        Debug.history('[Campaign] Heading for daily missions')
        click((1770, 1000))
        sleep(1)

        Debug.history('[Campaign] Opening Liberation')
        click((685, 820))
        sleep(1)

        # Loop through available liberations
        winning = True
        drag_count = 0
        while winning and drag_count < 3:
            for x in range(90, 1800, 10):
                if color_at(x, 800) == 'green':
                    Debug.history('[Campaign] Select Liberation')
                    click((x, 800))

                    # Liberation moving on, waiting for finish
                    start_ts = time.time_ns()
                    while True :
                        if color_at(870, 770) == 'green' and color_at(960, 690) == 'brown_liberation_won':
                            Debug.history(f'[Campaign] Liberation successfully finished in {duration_text(start_ts)}')
                            click((870, 770))
                            break
                        if color_at(870, 770) == 'green' and color_at(960, 720) == 'blue_liberation_lost':
                            Debug.warn(f'[Campaign] Liberation lost in {duration_text(start_ts)}')
                            winning = False
                            click((870, 770))
                            break
                        sleep(1)
                if not winning:
                    break
            if winning:
                #drag the screen 800 pixels to the left
                drag_drop((1000,430), (200,430))
                drag_count += 1

        if drag_count:
            #drag the screen back to the beginning
            for _ in range(0, drag_count):
                drag_drop((200,430), (1000,430))
        click((1820, 70))
        click((1510, 90))

    click((1840, 60))
    return 0

def map_map(trigger: bool = False, direction: int = 0) -> int:
    """
    Manage world map operations including reward claiming and dynamic deployment.

    Phase 1 harvests finished missions using rapid pixel color scans. Phase 2
    normalizes the map viewport scale via drag-and-drop zoom controls to align
    icon dimensions. Phase 3 scans and dispatches type-specific campaigns.
    """
    if trigger:
        press_key('m')

    if not page_wait('map_map'):
        return -1

    _area = Region(140, 60, 1630, 950)
    timestamps = []

    if not direction:
        if color_at(280, 945) == 'yellow':
            # refresh for free
            click((200, 950))
            sleep(3)
        else:
            # Get new missions time
            while True:
                ts = Region(260, 1020, 150, 40).text('', colormap['lightyellow']).lower()
                match = re.search(r':\s([\d:]+)$', ts)
                if match:
                    timeout = parse_ui_timeout(match.group(1))
                    if timeout < time.time() + 21600:
                        if timeout - time.time() > 180:
                            timestamps.append(timeout)
                        break
            # all done, nothing to do
            if color_at(280, 980) == 'yellow':
                if timestamps:
                    return min(timestamps) - 180
                return 0

        while True:
            clicked = False
            if color_at(91, 306) == 'green':
                click((160, 306))
                clicked = True
            else:
                ts = Region(85, 306 - 10, 180, 40).text('', colormap['white'])
                if re.search(r'^[\d:]+$', ts):
                    timeout = parse_ui_timeout(ts)
                    if timeout:
                        if abs(timeout - time.time()) < 181:
                            click((160, 306))
                            sleep(1)
                            if color_at(1450, 790) == 'yellow':
                                click((1400, 790))
                            clicked = True
                        else:
                            timestamps.append(timeout)
                    else:
                        timestamps.append(get_timeout(30))

            if clicked:
                sleep(1)
                if color_at(1450, 790) == 'yellow':
                    click((1400, 790))
                    sleep(0.5)
                if color_at(1060, 650) == 'green':
                    click((1060, 650))
            else:
                break

        # Set zoom to minimal
        click((1337, 1037))

    # Get available slots
    available: int = 0
    total: int = 0
    area = Region(1150, 20, 100, 36)
    attempts = 0
    while not total and attempts < 5:
        text = area.text('1234567890/', colormap['white'], 3)
        Debug.info(f'{text}')
        if text.startswith('/'):
            text = f'4{text}'
        current_text = re.search(r'(\d+)/(\d+)', text)
        if current_text:
            available = int(current_text.group(1))
            total = int(current_text.group(2))
        else:
            attempts += 1

    mission_types = {
        'mystery':  2,
        'scout': 1,
        'adventure': 1,
        'war': 1,
        'monster': 2,
        'dragon': 2,
        'naval': 2
    }

    for mission_type in config['map_order'].split(','):
        mission_type = mission_type.strip().lower()
        if not mission_type in mission_types:
            Debug.warn(f'Unknown mission type \'{mission_type}\' specified')
            continue

        required = mission_types[mission_type]
        if total and available < required:
            continue

        filename = 'images/tasks/map/mission/' + mission_type + '.png'
        if not os.path.exists(filename):
            Debug.warn(f'{filename} does not exist')
            continue

        missions = _area.find_all(filename)
        if missions:
            clicked = []
            for m in missions:
                if total and available < required:
                    break

                x = my_round(m.get_x())
                y = my_round(m.get_y())
                if [x, y] in clicked:
                    continue
                clicked.append([x, y])

                # check if running (scan for banner)
                found = False
                left = m.get_x()
                for x in range(left, left - 30, -1):
                    if color_at(x, m.get_y() + 10) == 'red':
                        right = m.get_x() + m.get_w()
                        for x in range(right, right + 30):
                            if color_at(x, m.get_y() + 10) == 'red':
                                found = True
                                break
                    if found:
                        break
                if found:
                    continue

                # check if silver mission (double requirement)
                silver = False
                x = m.get_center().get_x()
                for y in range(m.get_y(), m.get_y() - 30):
                    if color_at(x, y) == 'silver':
                        Debug.info('silver mission detected')
                        silver = True
                        break
                if silver and total and available < required * 2:
                    continue

                m.click()
                m.wait_vanish()
                if color_at(1090, 870) == 'green':
                    ts = Region(1000, 790, 200, 36).text('1234567890:', colormap['green'])
                    if ts:
                        timeout = parse_ui_timeout(ts)
                        if timeout:
                            timestamps.append(timeout)
                        else:
                            timestamps.append(get_timeout(30))

                    available -= required
                    if silver:
                        available -= required

                    click((1090, 870))
                    sleep(0.5)
                else:
                    txt = Region(960, 870, 560, 50).text('Youdnthavegsq', colormap['red'])
                    click((1530, 220))
                    if txt and len(txt) > 10:
                        available = 0
                        total = 1
                        break

    # we still got squads idling
    if total and available and color_at(640, 1020) == 'white':
        # we started with 0, drag the map up to check the lower part
        if direction == 0:
            drag_drop((960, 810), (960, 540))
            timestamps.append(map_map(False, 1))
        elif direction == 1:
            drag_drop((960, 270), (960, 810))
            timestamps.append(map_map(False, 2))
            drag_drop((960, 810), (960, 540))
    else:
        if direction == 1:
            drag_drop((960, 270), (960, 540))
            sleep(1)
            click((1840, 55))

    if not direction:
        click((1840, 55))

    if timestamps:
        return min(timestamps) - 180
    if direction:
        # return 24 hours in order to not get picked above if nothing was clicked
        return get_timeout(86400)
    return 0

def new_hero(trigger: bool = False) -> int:
    """
    Execute New Hero Screen
    """
    if trigger:
        pass

    click((1840, 55))
    return get_timeout(604800)

def oracle(trigger: bool = False) -> int:
    """
    Perform oracle tasks
    """
    if trigger:
        press_key('o')
        sleep(2)

    if not page_wait('oracle'):
        return -1

    # Rituals
    if color_at(885, 360) == 'white':
        click((820, 430))
        coords = {
            'harmony': (1280, 500),
            'serenity': (1710, 500),
            'obedience':  (1280, 870),
            'concentration': (1710, 870)
        }

        for _ in range (0, 2):
            for name, (x, y) in coords.items():
                if color_at(x, y) == 'green':
                    Debug.history(f'Performing/ claiming {name} ritual')
                    click((x, y))

    # blessings
    if color_at(885, 540) == 'white':
        click((820, 610))
        coords = {
            'Firestone Finder': (1465, 185),
            'Raining gold': (1640, 230),
            'Mana heroes': (1770, 360),
            'Rage heroes': (1820, 540),
            'Energy heroes': (1770, 715),
            'Tank specialization': (1640, 840),
            'Healer specialization': (1465, 890),
            'Damage specialization': (1290, 840),
            'Fist fight': (1160, 715),
            'Precision': (1115, 540),
            'Magic spells': (1160, 360),
            'Guardian power': (1290, 230),
            'Fate': (1480, 520),
        }

        # get current values
        amounts = []
        tmp = {}
        for name, (x, y) in coords.items():
            if color_at(x, y) != 'white':
                continue
            amount = Region(x - 90, y + 90, 64, 32).get_number('white')
            amounts.append(amount)
            tmp[name] = (x, y, amount)

        for _ in range(3):
            # now lets see what to upgrade
            for name, (x, y, current) in tmp.items():
                if not color_at(x, y) == 'white':
                    continue
                # skip if current is already the highest
                if name != 'Fate' and max(amounts) and min(amounts) != max(amounts) and current == max(amounts):
                    continue
                # select the item
                click((x - 60, y + 50))
                sleep(1)
                # check if we can bless this
                if color_at(1485, 850) == 'green':
                    Debug.history(f'Blessing {name}')
                    click((1485, 850))
                    tmp[name] = (x, y, current + 1)
                    amounts.append(current + 1)
                click((1710, 220))
                sleep(1)

    click((1840, 55))
    return 0

def oracle_gift(trigger: bool = False) -> int:
    """
    Obtain oracle gift
    """
    if trigger:
        pass

    if not page_wait('oracle_gift'):
        return -1

    if color_at(750, 820) == 'green':
        click((750, 820))

    click((1840, 55))
    return 0

def pirates_price(trigger: bool = False) -> int:
    """
    Execute the Pirates Price tool allocation and interaction routine.

    Interacts with the localized mining area coordinates before triggering
    global exit anchors to return execution back to the primary canvas.
    """
    if trigger:
        pass

    claimed = False
    trials = 0
    while not claimed and trials < 6:
        for x in [483, 790, 1097, 1404]:
            if color_at(x, 910) == 'green':
                click((x, 910))
                claimed = True

        drag_drop((1500, 800), (272, 800))
        sleep(2)
        trials += 1

    click((1840, 55))
    return 0

def shop_signin(trigger: bool = False) -> int:
    """
    Collect Sign-In Bonus
    """
    if trigger:
        pass

    # Loop through possible positions
    for y_coords in [870, 920]:
        click((1360, y_coords))

    # Check for the mystery box while here
    click((620, 100))
    sleep(1)
    if color_at(740, 900) == 'green':
        Debug.history('[shop_signin] Picked up mystery box')
        click((600, 900))

    sleep(1)
    click((1840, 55))

    # perfect opportunity to go for dailies
    bag()
    exotic_merchant()
    tavern_tavern_game(True)
    guild_arcanecrystal(True)
    return get_next_reset()

def tavern_scarab_game(trigger: bool = False) -> int:
    """
    Play scarab game
    """
    if trigger:
        pass

    # shop
    if color_at(1880, 710) == 'white':
        click((1810, 750))
        sleep(1)
        tavern_scarab_token()

    # the game itself
    while color_at(1024, 1000) == 'green':
        click((1024,1000))
        move_to((800, 1000))
        start_loop = time.time()
        while time.time() - start_loop < 5 and not color_at(1024, 1000) == 'green':
            sleep(1)

    # pharao's vault
    if color_at(1880, 180) == 'white':
        click((1810, 220))
        sleep(1)
        tavern_pharaos_vault()

    # release beast
    if color_at(400, 610) == 'white':
        click((300, 640))
        sleep(5)

    click((1840, 55))
    return 0

def tavern_scarab_milestone(trigger: bool = False) -> int:
    """
    Get daily scarab token
    """
    if trigger:
        pass

    sleep(1)
    drag_count = 0
    while drag_count < 3:
        for x_coords in range(130, 1700, 20):
            if color_at(x_coords, 825) == 'green':
                click((x_coords, 825))
        drag_drop((1700, 560), (240, 560))
        drag_count += 1

    if drag_count:
        for _ in range(1, drag_count):
            drag_drop((240, 560), (1700, 560))

    click((1800, 200))

    return tavern_pharaos_vault()

def tavern_scarab_token(trigger: bool = False) -> int:
    """
    Get daily scarab token
    """
    if trigger:
        pass

    click((610,800))
    click((1840, 55))
    sleep(1)
    return tavern_scarab_game()

def tavern_pharaos_vault(trigger: bool = False) -> int:
    """
    Process Pharao's Vault
    """
    if trigger:
        pass

    while color_at(1010, 1010) == 'green':
        click((1010,1010))
        move_to((940, 1010))
        start_loop = time.time()
        while time.time() - start_loop < config['wait_page'] and not color_at(1010, 1010) == 'green':
            sleep(1)

    if color_at(1870, 410) == 'red':
        click((1800, 450))
        sleep(2)
        tavern_scarab_token()

    click((1840, 55))
    sleep(1)
    return tavern_scarab_game()

def tavern_tavern_collect(trigger: bool = False) -> int:
    """
    Convert beer into game tokens
    """
    if trigger:
        pass


    while True:
        if color_at(400, 640) == 'green':
            click((400, 640))
            sleep(0.5)
        else:
            click((1670, 270))
            break

    click((1840, 55))
    return 0

def tavern_tavern_game(trigger: bool = False) -> int:
    """
    Run the tavern game
    """
    if not trigger:
        # save for dailies
        click((1840, 55))
        return 0

    press_key('t')
    sleep(1)
    click((690, 965))
    sleep(1)
    click((770, 550))
    sleep(2)
    amount = Region(1585, 30, 110, 35).get_number()

    amount = min(int(amount), 10)
    for _ in range(0, amount):
        if color_at(1060, 1000) == 'green':
            click((960, 1000))
            sleep(1)
            click((random.choice([660, 960, 1260]) , random.choice([330, 760])))
            while not color_at(1060, 1000) in ['green', 'grey']:
                pass

    click((1840, 55))
    return 0

def temple_of_eternals(trigger: bool = False) -> int:
    """
    Execute the Firestone collection interface clearing routing.

    Fires a precise exit input to clear the localized inventory
    overlay and return execution context back to the central loop.
    """
    global timeouts

    if trigger:
        press_key('e')

    if not page_wait('temple_of_eternals'):
        return -1

    percentage = Region(1430, 417, 180, 40).get_number('green')

    jump_require = int(config['jump_percentage'])
    if percentage >= jump_require:
        Debug.warn(f'[temple_of_eternals] Time to jump! {percentage}%/{jump_require}%')
        timeouts['check_upgrade'] = 0
        click((1360 ,510))
        sleep(0.5)
        if percentage >= int(config['jump_temple_token']) and color_at(1050, 990) == 'green':
            click((1050, 990))
        else:
            click((960, 660))
        sleep(0.5)
        click((1100, 720))
        sleep(5)
        click((950, 740))
    else:
        Debug.warn(f'[temple_of_eternals] Current percentage: {percentage}%/{jump_require}%')
        click((1840, 55))

    return 0
