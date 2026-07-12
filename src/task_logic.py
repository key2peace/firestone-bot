"""
Task Logic Subroutines for Firestone Bot Gameplay Automation.

Provides alphabetically organized gameplay handlers dispatched dynamically
via the main automation loop. All visual state checks, hardware inputs,
and lifecycle guards are handled natively through the custom core framework.
"""
import os
import random
import time
import cv2

from custom_core import (
    #dailies,
    get_next_reset,
    #get_suffix_rank,
    get_timeout,
    parse_ui_timeout,
    tasks,
    click,
    color_at,
    colormap,
    config,
    Debug,
    drag_drop,
    duration_text,
    grab_screen_to_mat,
    mouse_down,
    mouse_up,
    move_to,
    press_key,
    Region
)

_screen = Region(0, 0, 1920, 1080)

def run_arcane_crystal() -> int:
    """
    Execute the Arcane Crystal interface routing subroutine.
    """
    for _ in range(1, 5):
        if color_at(1050, 970) == 'green':
            click((1670, 1020))
            move_to((1120, 1020))
            start_loop = time.time()
            while time.time() - start_loop < 5 and not color_at(1050, 970) == 'green':
                time.sleep(1)

    score = Region(1590, 20, 110, 30).get_number()
    print(score)
    if score and int(score) > 500:
        click((1800, 370))
        time.sleep(1)
        return run_awakening()
    click((1840, 55))
    return 0

def run_arena_of_kings() -> int:
    """
    Execute the Arena of Kings navigational cleanup subroutine.
    """
    click((1855, 115))
    return 0

def run_awakening() -> int:
    """
    Process awakening screen
    """
    while color_at(1670, 1030) == 'green':
        click((1050, 970))
        move_to((1320, 970))
        while not color_at(1670, 1030) == 'green':
            time.sleep(0.5)
    click((1840, 55))
    return 0

def run_campaign() ->int:
    """Perform Campaign Task"""
    timestamps = []

    # Check if we can claim loot
    if color_at(80, 1000) == 'green':
        click((80, 1000))
        timestamps.append(int(time.time()) + 21600)

    # Check for daily missions
    if color_at(1870, 990) == 'red':
        Debug.history("[Campaign] Heading for daily missions")
        click((1770, 1000))
        time.sleep(1)

        Debug.history("[Campaign] Opening Liberation")
        click((685, 820))
        time.sleep(1)

        # Loop through available liberations
        winning = True
        attempts = 0
        drag_count = 0
        while winning and attempts < 5:
            if  color_at(200, 800) == 'green':
                Debug.history("[Campaign] Select Liberation")
                click((200, 800))

                # Liberation moving on, waiting for finish
                start_ts = time.time_ns()
                while True:
                    if color_at(870, 770) == 'green' and color_at(960, 690) == 'brown_liberation_won':
                        Debug.history("[Campaign] Liberation successfully finished in %s", duration_text(start_ts))
                        click((870, 770))
                        break
                    if color_at(870, 770) == 'green' and color_at(960, 720) == 'blue_liberation_lost':
                        Debug.history("[Campaign] Liberation successfully finished in %s", duration_text(start_ts))
                        winning = False
                        click((870, 770))
                        break
                    time.sleep(5)
            else:
                attempts += 1
            if winning:
                #drag the screen 400 pixels to the left
                drag_drop((1000,430), (600,430))
                drag_count += 1

        if drag_count:
            #drag the screen back to the beginning
            for _ in range(1, drag_count):
                drag_drop((100,430), (1000,430))
        click((1820, 70))
    click((1840, 60))
    if timestamps:
        return min(timestamps)
    return 0

def run_chaos_rift() -> int:
    """
    Run chaos rift challenge.
    """
    while color_at(1050, 970) == 'green':
        click((1050, 970))
        move_to((1200, 970))
        start_loop = time.time()
        while time.time() - start_loop < 10 and not color_at(1050, 970) == 'green':
            time.sleep(1)

    click((1840, 55))
    return 0

def run_check_upgrade() -> int:
    """
    Validate and enforce the global hero upgrade multiplier mode via OCR.

    Scans the primary upgrade interaction canvas text and sequentially clicks
    the selector until the screen state matches the target configuration mode.
    """
    main_upgrade = Region(1661, 910, 259, 170)
    target_mode = str(config['upgrade_mode']).lower()

    # Cycle selector modes inline until text configuration criteria are met
    while target_mode not in main_upgrade.text().lower():
        main_upgrade.click()
        main_upgrade.move_mouse_away()
    return time.time() * 2

def run_daylies() -> int:
    """
    Run daylie tasks
    """
    return get_next_reset()

def run_engineer() -> int:
    """
    Execute the Engineer resource allocation routine.

    Interacts with the localized production interface before firing
    global exit anchors to restore primary canvas visibility.
    """
    click((1620, 730))
    click((1840, 55))
    return get_timeout(21600)

def trigger_firestone_collect() -> bool:
    """
    Open the Temple of Eternals and trigger the handling
    """
    press_key('e')
    time.sleep(1)
    return run_firestone_collect()

def run_firestone_collect() -> int:
    """
    Execute the Firestone collection interface clearing routing.

    Fires a precise exit input to clear the localized inventory
    overlay and return execution context back to the central loop.
    """
    global tasks

    percentage = Region(1300, 417, 400, 40).get_number('green')
    jump_require = int(config['jump_percentage'])
    if percentage >= jump_require:
        Debug.info(f"[Firestone Collect] Time to jump! {percentage}%/{jump_require}%")
        tasks['check_upgrade'] = ('', 'run_check_upgrade', 0)
        click((1360 ,510))
        time.sleep(0.5)
        click((960, 660))
        time.sleep(0.5)
        click((1100, 720))
        time.sleep(5)
        click((950, 740))
    else:
        click((1840, 55))
    return get_timeout(1800)

def run_firestone_research() -> int:
    """
    Manage the Firestone research pipeline lifecycle in two distinct phases.

    Phase 1 monitors and collects completed research projects utilizing rapid
    pixel color scans. Phase 2 processes active template research bubbles and
    executes screen drag operations to initialize new available projects.
    """
    task_firestone_research_bubble = 'images/tasks/firestone/research_bubble.png'

    for x_coords in [1220, 520]:
        if color_at(x_coords, 980) == 'green':
            click((x_coords, 980))

    drag_count = 0
    while drag_count <= 10:
        img = _screen.exists(task_firestone_research_bubble)
        if img:
            Debug.history("[Firestone Research] Selecting Research")
            img.click()
            time.sleep(1)
            click((790, 720))
            if color_at(970, 660) == 'lightbrown_research_full':
                Debug.warn("[Firestone Research] Research slots full")
                click((1400, 350))
                click((1250, 200))
                break
        else:
            drag_drop((1130, 430), (730, 430))
            drag_count += 1

    if drag_count:
        for _ in range(1, drag_count):
            drag_drop((530, 430), (1130, 430))

    click((1840, 55))
    return 0

def run_forbidden_knowledge() -> int:
    """
    Run forbidden knowledge circle
    """
    for y_coords, name in [(350, 'Ledra'), (540, 'Yanamoth'), (700, 'Kramatak')]:
        click((1800, y_coords))
        amount = Region(1600, 20, 100, 36).get_number()
        Debug.info(f"Amount for {name}: {amount}")
        if not amount:
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
            color = 'blue'
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
            color = 'brown'
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

        for x, y, stat in coords:
            Region(x - 5, y - 5, 10, 10).highlight(3)
            if not amount:
                continue
            if color_at(x, y) == color:
                click((x, y))
                cost = Region(970, 730, 120, 50).get_number()
                while cost and cost <= amount and color_at(1046, 750) == 'green':
                    Debug.info(f"Upgrading {stat}")
                    click((1046, 750))
                    move_to((1120, 750))
                    amount -= cost
                click((1260, 270))
        click((220, 900))
        if color_at(960, 890) == 'green':
            cost = Region(960, 900, 130, 50).get_number()
            if cost and amount >= cost:
                Debug.info(f"Recruiting {name}")
                click((960, 890))
                amount -= cost

    click((1840, 55))
    return 0


def run_garage() -> int:
    """
    Process the garage page
    """
    click((1840, 55))
    return get_next_reset()

# Static UI region boundaries for the War Machine Garage interface
# Modify these coordinates to match your active Chrome browser resolution
MACHINE_NAME_REGION = Region(800, 150, 300, 50)   # Viewport framing the text header
BIG_IMAGE_REGION = Region(400, 300, 500, 400)    # Bounding box of the central vehicle sprite
CAROUSEL_FIRST_SLOT = (450, 850)                 # Active X/Y anchor of the leftmost icon slot

# Explicit spatial width of a single carousel item icon including spacing margins
SWIPE_DISTANCE_X = 120

def run_garage_asset_scraper() -> None:
    """
    Execute a linear drag_drop carousel scraper within the War Machine Garage.

    Iterates through the vehicle carousel using fixed-distance spatial swipes,
    capturing visual assets and compiling an inventory database via live OCR.
    Stops automatically once a duplicate machine name sequence is detected.
    """
    Debug.info("Initializing automated Garage asset scraper workflow...")
    scanned_machines: list[str] = []

    # Calculate static start and end vectors for the horizontal drag_drop timeline
    start_x, start_y = CAROUSEL_FIRST_SLOT
    end_x = start_x - SWIPE_DISTANCE_X
    end_y = start_y  # Maintain perfect horizontal trajectory during the swipe motion

    # Ensure output asset target destination directory exists to prevent I/O traps
    os.makedirs("capture/war_machines", exist_ok=True)

    while True:
        # Give the Unity WASM interface a brief window to settle pre-inference
        time.sleep(0.5)

        # Extract and sanitize the active vehicle name via outline-dissolving OCR
        raw_name = MACHINE_NAME_REGION.text()
        machine_name = "".join(c for c in raw_name if c.isalnum()).strip()

        # Dynamic fallback signature if OCR encounters a temporary visual occlusion
        if not machine_name:
            machine_name = f"unknown_machine_{int(time.time())}"

        # Loop termination engine: stop once the carousels wrap-around index hits a duplicate
        if machine_name in scanned_machines:
            Debug.info(f"Scraper sequence completed. Wrapped to existing target: '{machine_name}'")
            break

        Debug.info(f"Target machine identified: '{machine_name}'. Capturing assets...")
        scanned_machines.append(machine_name)

        # Slice a clean template matrix crop of the current vehicle sprite
        # Saved unignored to fuel background context validation on subsequent repository pushes
        output_path = f"capture/war_machines/{machine_name.lower()}.png"
        cv2.imwrite(output_path, grab_screen_to_mat(BIG_IMAGE_REGION))

        # Execute linear shift transition to pull the adjacent asset into focus
        drag_drop((start_x, start_y), (end_x, end_y))

        # Grant the Unity rendering engine ample headroom to clear scroll inertial animations
        time.sleep(0.8)

    Debug.info(f"Garage scraper cycle finished cleanly. Total unique assets mapped: {len(scanned_machines)}")

def run_guild_expeditions() -> int:
    """
    Execute sequentially coordinated inputs inside the Guild Expeditions panel.

    Processes an ordered array of screen coordinate nodes to advance active
    expedition pipelines with minimal state tracking.
    """
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

def run_hero_upgrade() -> int:
    """
    Execute sequential hero upgrades based on real-time RAM pixel color scans.

    Evaluates specific coordinate anchors across the character bar for active
    gold indicators and fires hardware clicks on available slots dynamically.
    """
    while True:
        inactive_slots = 0
        clicked = False

        # Exact horizontal pixel anchors for the hero upgrade triggers
        for x_coord in [120, 620, 820, 1020, 1220, 1420, 1620]:
            if color_at(x_coord, 930) == 'yellow':
                move_to((x_coord, 980))
                mouse_down()
                while color_at(x_coord, 930) == 'yellow':
                    time.sleep(1)
                mouse_up()
                clicked = True
            else:
                inactive_slots += 1
        if clicked:
            move_to((x_coord, 1080))

        # Break the lifecycle loop once all monitored slots report depletion
        if inactive_slots == 7:
            return get_timeout(10)
    return 0

def run_ledra_supplies() -> int:
    """
    Process ledra supplies
    """
    while color_at(560, 820) == 'yellow':
        click((560, 820))
        move_to((480, 820))
    click((1840, 55))
    click((1840, 55))
    return 0

def run_mailbox() -> int:
    """
    Check mailbox
    """
    while not Region(720, 240, 470, 70).text('Themailboxspty.'):
        if color_at(1130, 840) == 'green':
            click((1130, 840))
            click((1600, 980))
            time.sleep(0.5)
        click((1600, 980))

    click((1650, 40))
    return get_timeout(3600)

def run_map() -> None:
    """
    Manage world map operations including reward claiming and dynamic deployment.

    Phase 1 harvests finished missions using rapid pixel color scans. Phase 2
    normalizes the map viewport scale via drag-and-drop zoom controls to align
    icon dimensions. Phase 3 scans and dispatches type-specific campaigns.
    """
    _area = Region(140, 60, 1630, 950)
    task_map_zoom = 'images/tasks/map/zoom.png'
    timestamps = []

    base_y = 320
    while base_y < 1080:
        if color_at(110, base_y) == 'green':
            click((110, base_y))
            time.sleep(0.5)
            click((950, 650))
            time.sleep(0.5)
        else:
            ts = Region(100, 300, 60, 32).text('1234567890:', colormap['white'])
            if ts:
                timeout = parse_ui_timeout(ts)
                if timeout:
                    timestamps.append(timeout)
            base_y += 150

    zoom_match = _screen.exists(task_map_zoom)
    if zoom_match:
        drag_drop(zoom_match, (1290, zoom_match.get_y()))

    slots_full = False
    for mission_type in ['mystery', 'scout', 'adventure', 'war', 'monster', 'dragon']:
        missions = _area.find_all('images/tasks/map/mission/' + mission_type + '.png')
        if missions:
            for m in missions:
                m.click()
                m.waitVanish()
                if color_at(1090, 870) == 'green':
                    ts = Region(1000, 790, 200, 36).text('1234567890:', colormap['green'])
                    if ts:
                        timeout = parse_ui_timeout(ts)
                        if timeout:
                            timestamps.append(timeout)
                    click((1090, 870))
                    time.sleep(0.5)
                else:
                    txt = Region(960, 870, 560, 50).text('Youdnthavegsq', colormap['red'])
                    if txt and len(txt) > 5:
                        slots_full = True
                    click((1530, 220))
                    break

        if slots_full:
            break

    click((1840, 55))
    #if timestamps:
    #    return min(timestamps)
    return 0

def run_meteorite() -> int:
    """
    Execute the Meteorite Research.
    """
    click((1840, 55))
    return 0

def run_new_hero() -> int:
    """
    Execute New Hero Screen
    """
    click((1840, 55))
    return get_timeout(604800)

def run_pickaxe() -> int:
    """
    Execute the Pickaxe tool allocation and interaction routine.

    Interacts with the localized mining area coordinates before triggering
    global exit anchors to return execution back to the primary canvas.
    """
    click((690, 660))
    click((1840, 55))
    return 0

def run_pirates_price() -> int:
    """
    Execute the Pirates Price tool allocation and interaction routine.

    Interacts with the localized mining area coordinates before triggering
    global exit anchors to return execution back to the primary canvas.
    """
    claimed = False
    trials = 0
    while not claimed and trials < 6:
        for x in [483, 790, 1097, 1404]:
            if color_at(x, 910) == 'green':
                click((x, 910))
                claimed = True

        drag_drop((1500, 800), (272, 800))
        time.sleep(2)
        trials += 1

    click((1840, 55))
    return 0

def run_quests() -> int:
    """
    Execute the quest completion and collection protocol.

    Navigates through multiple quest category tabs and sequentially triggers
    claim buttons using fixed index ranges to collect accumulated rewards.
    """
    for x in [760, 1170]:
        click((x, 130))
        time.sleep(1)
        while color_at(1380, 300) == 'green':
            click((1560, 300))
            move_to((1620, 300))

    click((1840, 55))
    return 0

def run_scarab_game() -> int:
    """
    Play scarab game
    """
    while color_at(1024, 1000) == 'green':
        click((1024,1000))
        move_to((800, 1000))
        start_loop = time.time()
        while time.time() - start_loop < 10 and not color_at(1024, 1000) == 'green':
            time.sleep(1)

    score = Region(177, 33, 125, 38).get_number()
    if score > 5000:
        click((1800, 220))
        time.sleep(1)
        return run_scarab_vault()

    click((1840, 55))
    return 0

def run_scarab_vault() -> int:
    """
    Process Pharao's Vault
    """
    while color_at(1010, 1010) == 'green':
        click((1010,1010))
        move_to((940, 1010))
        start_loop = time.time()
        while time.time() - start_loop < 10 and not color_at(1010, 1010) == 'green':
            time.sleep(1)

    click((1840, 55))
    time.sleep(1)
    return run_scarab_game()

def run_scarab_token() -> int:
    """
    Get daily scarab token
    """
    click((610,800))
    click((1840, 55))
    time.sleep(1)
    return run_scarab_game()

def run_signin() -> int:
    """
    Collect Sign-In Bonus
    """
    # Loop through possible positions
    for y_coords in [870, 920]:
        click((1360, y_coords))

    click((1840, 55))
    return get_next_reset()

def run_talents() -> int:
    """
    Upgrade talents
    """
    bubble = 'images/tasks/talents/bubble.png'
    _area = Region(470, 170, 1340, 860)
    counter = 0
    clicked = False
    while True:
        match = _area.exists(bubble)
        if match:
            match.click()
            time.sleep(1)
            while color_at(1032, 853) == 'green_talents':
                click((1020, 866))
                move_to((1100, 866))
                clicked = True
            click((1250, 320))
            break
        drag_drop((950, 990), (950, 188))
        counter += 1
        if counter > 10:
            for _ in range(1, counter):
                drag_drop((950, 188), (950, 990))
            break

    if clicked:
        click((1650, 980))

    click((1850, 80))
    return 0

def run_tavern() -> int:
    """
    Manage the tavern dispatch queue and resource accumulation.

    Phase 1 checks for active ready indicators using pixel color validation
    and deploys available assets. Phase 2 exits the subsystem once depletion holds.
    """
    while True:
        if color_at(400, 640) == 'yellow':
            click((400, 640))
            time.sleep(0.5)
        else:
            click((1670, 270))
            break

    click((1840, 55))
    time.sleep(1)
    return run_tavern_game()

def run_tavern_game() -> int:
    """
    Run the tavern game
    """
    amount = Region(1585, 30, 110, 35).get_number()
    if not amount:
        click((1840, 55))
        return 0
    amount = min(amount, 10)

    for _ in range(1, int(amount)):
        click((960, 1020))
        time.sleep(1)
        click((random.choice([660, 960, 1260]) , random.choice([330, 760])))
        time.sleep(5)

    click((1840, 55))
    return 0

def run_upgrade_guardian() -> int:
    """
    Guardian Upgrade
    """
    pos = {
        'vermilion': (740, 1000),
        'grace': (890, 1000),
        'ankaa': (1040, 1000),
        'azhar': (1200, 1000)
    }
    dust = Region(1590, 20, 110, 32).get_number()

    while True:
        current = Region(250, 830, 300, 60).text('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', colormap['brown']).lower()
        if current and current in pos:
            del pos[current]

            click((1050, 150)) # General
            time.sleep(1)
            if color_at(1090, 800) == 'green':
                Debug.history(f"Training {current}")
                click((1090,800))
            amount, _ = divmod(dust, 20)
            if amount:
                Debug.history(f"Enlightening {current} {amount} times")
                for _ in range(1, int(amount)):
                    if color_at(1590, 800) == 'green':
                        click((1590, 800))
                        move_to((1590, 880))
                        dust -= 20
                    else:
                        break

            click((1210, 150)) #Evolution
            time.sleep(1)
            cost = Region(1100, 767, 150, 40).get_number('brown')
            Debug.info(f"Evolution costs: {cost}")
            if cost >= dust and color_at(1220, 780) == 'green':
                Debug.history(f"Evolving {current}")
                click((1220, 780))
                dust -= int(cost)
                time.sleep(3)

            click((1400, 150)) #Chaos Rift
            time.sleep(1)
            amount = Region(1564, 20, 160, 30).get_number()
            Debug.info(f"Chaos rift amount: {amount}")
            while True:
                cost = Region(1460, 630, 130, 40).get_number()
                Debug.info(f"Chaos rift costs: {cost}")
                if cost and cost >= dust:
                    Debug.history(f"Increase {current}'s holy damage")
                    click((1720, 760))
                    time.sleep(1)
                    amount -= cost

            click((1560, 150)) #Guardian rarity
            time.sleep(1)
            if color_at(1365, 630) == 'green':
                click((1365, 630))

            if not pos:
                break

            for name, (x, y) in pos.items():
                x, y = next(iter(pos))
                click((x, y))
                break

    click((1840, 55))
    return 120
