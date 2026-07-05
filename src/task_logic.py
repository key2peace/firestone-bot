"""
Task Logic Subroutines for Firestone Bot Gameplay Automation.

Provides alphabetically organized gameplay handlers dispatched dynamically
via the main automation loop. All visual state checks, hardware inputs,
and lifecycle guards are handled natively through the custom core framework.
"""
import os
import time

from custom_core import (
    capture,
    click,
    color_at,
    CONFIG,
    Debug,
    dragDrop,
    duration_text,
    Region,
    sleep
)

def run_arcane_crystal() -> None:
    """
    Execute the Arcane Crystal interface routing subroutine.

    Acts as a transient navigational bridge, firing defensive exit
    triggers to return the bot execution path back to the main canvas.
    """
    click((1840, 55))


def run_arena_of_kings() -> None:
    """
    Execute the Arena of Kings navigational cleanup subroutine.

    Clears the active arena viewport context by firing hardware inputs
    at the global exit anchors to restore primary dashboard visibility.
    """
    click((1855, 115))


def run_campaign() ->None:
    """Perform Campaign Task"""

    # Check if we can claim loot
    if color_at(80, 1000) == 'green':
        click((80, 1000))
    next_loot = Region(230, 830, 200, 40).text()
    if next_loot:
        Debug.info("Next Campaign loot in: %s", str(next_loot))

    # Check for daily missions
    if color_at(1870, 990) == 'red':
        Debug.history("[Campaign] Heading for daily missions")
        click((1770, 1000))
        sleep(1)
        capture('campaign_dm.png')

        Debug.history("[Campaign] Opening Liberation")
        click((685, 820))
        sleep(1)

        # Loop through available liberations
        winning = True
        while winning and color_at(200, 800) == 'green':
            Debug.history("[Campaign] Select Liberation")
            click((200, 800))

            # Liberation moving on, waiting for finish
            start_ts = time.time_ns()
            while True:
                if color_at(870, 770) == 'green' and color_at(960, 720) == 'blue_liberation_won':
                    Debug.history("[Campaign] Liberation successfully finished in %s", duration_text(start_ts))
                    click((870, 770))
                    break
                if color_at(870, 770) == 'green' and color_at(960, 720) == 'blue_liberation_lost':
                    Debug.history("[Campaign] Liberation successfully finished in %s", duration_text(start_ts))
                    winning = False
                    click((870, 770))
                    break
                sleep(5)
            if winning:
                # drag the screen 420 pixels to the left
                dragDrop((1000,430), (580,430))
        click((1820, 70))
    click((1510, 90))
    click((1840, 60))

def run_check_upgrade() -> None:
    """
    Validate and enforce the global hero upgrade multiplier mode via OCR.

    Scans the primary upgrade interaction canvas text and sequentially clicks
    the selector until the screen state matches the target configuration mode.
    """

    # Establish the precise viewport bounds for the primary upgrade button canvas
    main_upgrade = Region(1661, 910, 259, 170)
    target_mode = str(CONFIG['upgrade_mode']).lower()

    # Cycle selector modes inline until text configuration criteria are met
    while target_mode not in main_upgrade.text().lower():
        Debug.info(main_upgrade.text())
        main_upgrade.click()
        main_upgrade.moveMouseAway()


def run_engineer() -> None:
    """
    Execute the Engineer resource allocation routine.

    Interacts with the localized production interface before firing
    global exit anchors to restore primary canvas visibility.
    """

    click((1620, 730))
    click((1840, 55))


def run_firestone_collect() -> None:
    """
    Execute the Firestone collection interface clearing routing.

    Fires a precise exit input to clear the localized inventory
    overlay and return execution context back to the central loop.
    """

    click((1840, 55))


def run_firestone_research() -> None:
    """
    Manage the Firestone research pipeline lifecycle in two distinct phases.

    Phase 1 monitors and collects completed research projects utilizing rapid
    pixel color scans. Phase 2 processes active template research bubbles and
    executes screen drag operations to initialize new available projects.
    """
    _screen = Region(0, 0, 1920, 1080)
    task_firestone_research_bubble = 'images/tasks/firestone/research_bubble.png'

    if color_at(1215, 980) == 'green':
        click((1215, 980))
    if color_at(520, 980) == 'green':
        click((520, 980))

    while True:
        no_bubbles = 0
        img = _screen.exists(task_firestone_research_bubble)
        if img:
            Debug.error("[Firestone Research] Selecting Research")
            img.click()
            sleep(1)
            click((790, 720))
        else:
            dragDrop((1130, 430), (730, 430))
            no_bubbles += 1

        if no_bubbles == 10:
            break

        if color_at(970, 660) == 'lightbrown_research_full':
            Debug.error("[Firestone Research] Research slots full")
            click((1400, 350))
            sleep(1)
            click((1250, 200))
            break
    click((1840, 55))

# Static UI region boundaries for the War Machine Garage interface
# Modify these coordinates to match your active Chrome browser resolution
MACHINE_NAME_REGION = Region(800, 150, 300, 50)   # Viewport framing the text header
BIG_IMAGE_REGION = Region(400, 300, 500, 400)    # Bounding box of the central vehicle sprite
CAROUSEL_FIRST_SLOT = (450, 850)                 # Active X/Y anchor of the leftmost icon slot

# Explicit spatial width of a single carousel item icon including spacing margins
SWIPE_DISTANCE_X = 120

def run_garage_asset_scraper() -> None:
    """
    Execute a linear dragDrop carousel scraper within the War Machine Garage.

    Iterates through the vehicle carousel using fixed-distance spatial swipes,
    capturing visual assets and compiling an inventory database via live OCR.
    Stops automatically once a duplicate machine name sequence is detected.
    """
    Debug.info("Initializing automated Garage asset scraper workflow...")
    scanned_machines: list[str] = []

    # Calculate static start and end vectors for the horizontal dragDrop timeline
    start_x, start_y = CAROUSEL_FIRST_SLOT
    end_x = start_x - SWIPE_DISTANCE_X
    end_y = start_y  # Maintain perfect horizontal trajectory during the swipe motion

    # Ensure output asset target destination directory exists to prevent I/O traps
    os.makedirs("src/images/war_machines", exist_ok=True)

    while True:
        # Give the Unity WASM interface a brief window to settle pre-inference
        sleep(0.5)

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
        output_path = f"src/images/war_machines/{machine_name.lower()}.png"
        BIG_IMAGE_REGION.capture(output_path)

        # Execute linear shift transition to pull the adjacent asset into focus
        Debug.info(f"Executing dragDrop swipe from X:{start_x} to X:{end_x}...")
        dragDrop(start_x, start_y, end_x, end_y)

        # Grant the Unity rendering engine ample headroom to clear scroll inertial animations
        sleep(0.8)

    Debug.info(f"Garage scraper cycle finished cleanly. Total unique assets mapped: {len(scanned_machines)}")



def run_guild_expeditions() -> None:
    """
    Execute sequentially coordinated inputs inside the Guild Expeditions panel.

    Processes an ordered array of screen coordinate nodes to advance active
    expedition pipelines with minimal state tracking.
    """

    for coords in [(1290, 330), (1290, 330), (1510, 70)]:
        sleep(0.5)
        click(coords)


def run_hero_upgrade() -> None:
    """
    Execute sequential hero upgrades based on real-time RAM pixel color scans.

    Evaluates specific coordinate anchors across the character bar for active
    gold indicators and fires hardware clicks on available slots dynamically.
    """
    while True:
        inactive_slots = 0

        # Exact horizontal pixel anchors for the hero upgrade triggers
        for x_coord in [115, 640, 810, 1010, 1200, 1380, 1600]:
            if color_at(x_coord, 930) == 'yellow':
                click((x_coord + 10, 960))
            else:
                inactive_slots += 1

        # Break the lifecycle loop once all monitored slots report depletion
        if inactive_slots == 7:
            break

def run_map() -> None:
    """
    Manage world map operations including reward claiming and dynamic deployment.

    Phase 1 harvests finished missions using rapid pixel color scans. Phase 2
    normalizes the map viewport scale via drag-and-drop zoom controls to align
    icon dimensions. Phase 3 scans and dispatches type-specific campaigns.
    """
    _screen = Region(0, 0, 1920, 1080)
    task_map_zoom = 'images/tasks/map/zoom.png'

    for y in [470, 320]:
        if color_at(110, y) == 'green':
            click((110, y))
            sleep(1)
            click((950, 650))
            sleep(0.5)

    zoom_match = _screen.exists(task_map_zoom)
    if zoom_match:
        dragDrop(zoom_match, (1290, 1040))

    for mission_type in ['scout', 'adventure', 'war', 'monster']:
        missions = _screen.findAllList('images/tasks/map/mission/' + mission_type + '.png')
        if missions:
            for m in missions:
                m.click()
                m.waitVanish()
                if color_at(1090, 870) == 'green':
                    click((1090, 870))
                    sleep(0.5)
                else:
                    break

    click((1840, 55))


def run_meteorite() -> None:
    """
    Execute the Meteorite Research navigational cleanup subroutine.

    Clears the active research panel viewport context by firing hardware
    inputs at the global exit anchors to restore primary dashboard visibility.
    """

    click((1840, 55))


def run_pickaxe() -> None:
    """
    Execute the Pickaxe tool allocation and interaction routine.

    Interacts with the localized mining area coordinates before triggering
    global exit anchors to return execution back to the primary canvas.
    """

    click((690, 660))
    click((1840, 55))

def run_pirates_price() -> None:
    """
    Execute the Pirates Price tool allocation and interaction routine.

    Interacts with the localized mining area coordinates before triggering
    global exit anchors to return execution back to the primary canvas.
    """
    claimed = False
    while not claimed:
        for x in [483, 790, 1097, 1404]:
            if color_at(x, 910) == 'green':
                click((x, 910))
                claimed = True
        dragDrop((1500, 800), (272, 800))
        sleep(2)
    click((1840, 55))

def run_quests() -> None:
    """
    Execute the quest completion and collection protocol.

    Navigates through multiple quest category tabs and sequentially triggers
    claim buttons using fixed index ranges to collect accumulated rewards.
    """

    click((760, 130))
    for _ in range(5):
        click((1450, 300))
        sleep(1)

    click((1170, 130))
    for _ in range(5):
        click((1450, 300))
        sleep(1)

    click((1840, 55))


def run_tavern() -> None:
    """
    Manage the tavern dispatch queue and resource accumulation.

    Phase 1 checks for active ready indicators using pixel color validation
    and deploys available assets. Phase 2 exits the subsystem once depletion holds.
    """
    while True:
        if color_at(400, 640) == 'yellow':
            click((400, 640))
            sleep(0.5)
        else:
            click((1670, 270))
            break

    click((1840, 55))
