"""
Task Logic Subroutines for Firestone Bot Gameplay Automation.

Provides alphabetically organized gameplay handlers dispatched dynamically 
via the main automation loop. All visual state checks, hardware inputs, 
and lifecycle guards are handled natively through the custom core framework.
"""

from custom_core import *

def run_arcane_crystal(match: Match) -> None:
    """
    Execute the Arcane Crystal interface routing subroutine.
    
    Acts as a transient navigational bridge, firing defensive exit 
    triggers to return the bot execution path back to the main canvas.

    Args:
        match (Match): The detected visual anchor triggering this task execution.
    """
    check_emergency_stop()
    click((1840, 55))


def run_arena_of_kings(match: Match) -> None:
    """
    Execute the Arena of Kings navigational cleanup subroutine.
    
    Clears the active arena viewport context by firing hardware inputs 
    at the global exit anchors to restore primary dashboard visibility.

    Args:
        match (Match): The detected visual anchor triggering this task execution.
    """
    check_emergency_stop()
    click((1855, 115))


def run_campaign(match: Match) ->None:
    """Perform Campaign Task"""
    _screen = Region(0, 0, 1920, 1080)
    task_campaign_dm = 'images/tasks/campaign/daily_missions.png'
    task_campaign_liberate = 'images/tasks/campaign/liberate.png'
    task_campaign_liberate_ok = 'images/tasks/campaign/liberate_ok.png'
    click((115, 1000))
    try:
        img = _screen.exists(task_campaign_dm)
        if img:
            Debug.history("[Campaign] Heading for daily missions")
            img.click()
            img.waitVanish(img, task_campaign_dm)
            capture('campaign_dm.png')
            Debug.history("[Campaign] Heading for Liberations")
            click((685, 820))
            sleep(1)
            capture('campaign_liberation.png')
            try:
                #todo rewrite to use colors
                img2 = find(task_campaign_liberate)
                if img2:
                    Debug.history("[Campaign] Select Liberation")
                    img2.click()
                    img3 = _screen.wait(task_campaign_liberate_ok, 300)
                    if img3:
                        Debug.history("[Campaign] Finished Liberation?")
                        capture('campaign_liberate_done.png')
                        img3.click()
                        img3.waitVanish()
                dragDrop((1130,430), (730,430))
            except Exception as e:
                Debug.error("[Campaign] Liberation\n%s", str(e))
            click((1820, 70))
        click((1510, 90))
        click((1840, 60))
    except Exception as e:
        pass

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
    while check_emergency_stop() and target_mode not in main_upgrade.text().lower():
        main_upgrade.click()
        main_upgrade.moveMouseAway()


def run_engineer(match: Match) -> None:
    """
    Execute the Engineer resource allocation routine.

    Interacts with the localized production interface before firing
    global exit anchors to restore primary canvas visibility.

    Args:
        match (Match): The detected visual anchor triggering this task execution.
    """
    check_emergency_stop()
    click((1620, 730))
    click((1840, 55))


def run_firestone_collect(match: Match) -> None:
    """
    Execute the Firestone collection interface clearing routing.

    Fires a precise exit input to clear the localized inventory
    overlay and return execution context back to the central loop.

    Args:
        match (Match): The detected visual anchor triggering this task execution.
    """
    check_emergency_stop()
    click((1840, 55))


def run_firestone_research(match: Match) -> None:
    """
    Manage the Firestone research pipeline lifecycle in two distinct phases.

    Phase 1 monitors and collects completed research projects utilizing rapid 
    pixel color scans. Phase 2 processes active template research bubbles and 
    executes screen drag operations to initialize new available projects.

    Args:
        match (Match): The detected visual anchor triggering this task execution.
    """
    task_firestone_research_bubble = 'images/tasks/firestone/research_bubble.png'
    task_firestone_research_slotsfull = 'images/tasks/firestone/research_slotsfull.png'

    while check_emergency_stop() and color_at(540, 970) == 'green':
        click((540, 970))
        sleep(1)

    while check_emergency_stop():
        no_bubbles = 0
        img = exists(task_firestone_research_bubble)
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

        img = exists(task_firestone_research_slotsfull)
        if img:
            Debug.error("[Firestone Research] Research slots full")
            click((1400, 350))
            sleep(1)
            click((1250, 200))
            break
        click((1840, 55))


def run_guild_expeditions(match: Match) -> None:
    """
    Execute sequentially coordinated inputs inside the Guild Expeditions panel.

    Processes an ordered array of screen coordinate nodes to advance active
    expedition pipelines with minimal state tracking.

    Args:
        match (Match): The detected visual anchor triggering this task execution.
    """
    check_emergency_stop()
    for coords in [(1290, 330), (1290, 330), (1510, 70)]:
        sleep(0.5)
        click(coords)


def run_hero_upgrade() -> None:
    """
    Execute sequential hero upgrades based on real-time RAM pixel color scans.
    
    Evaluates specific coordinate anchors across the character bar for active 
    gold indicators and fires hardware clicks on available slots dynamically.
    """
    while check_emergency_stop():
        inactive_slots = 0
        
        # Exact horizontal pixel anchors for the hero upgrade triggers
        for x_coord in [115, 640, 810, 1010, 1200, 1380, 1600]:
            if color_at(x_coord, 930) == 'yellow':
                click((x_coord, 950))
                sleep(0.5)
            else:
                inactive_slots += 1
                
        # Break the lifecycle loop once all monitored slots report depletion
        if inactive_slots == 7:
            break

def run_map(match: Match) -> None:
    """
    Manage world map operations including reward claiming and dynamic deployment.

    Phase 1 harvests finished missions using rapid pixel color scans. Phase 2 
    normalizes the map viewport scale via drag-and-drop zoom controls to align 
    icon dimensions. Phase 3 scans and dispatches type-specific campaigns.

    Args:
        match (Match): The detected visual anchor triggering this task execution.
    """
    task_map_okay = 'images/tasks/map/okay.png'
    task_map_zoom = 'images/tasks/map/zoom.png'
    
    while check_emergency_stop() and color_at(170, 320) == 'green':
        click((170, 320))
        sleep(1)
        click((950, 650))
        sleep(0.5)

    zoom_match = exists(task_map_zoom)
    if zoom_match:
        check_emergency_stop()
        dragDrop(zoom_match, (1290, 1040))

    for mission_type in ['scout', 'adventure', 'war', 'monster']:
        check_emergency_stop()
        missions = findAllList('images/tasks/map/mission/' + mission_type + '.png')
        if missions:
            for m in missions:
                check_emergency_stop()
                m.click()
                m.waitVanish()
                if color_at(1090, 870) == 'green':
                    click((1090, 870))
                    sleep(0.5)
                    
    check_emergency_stop()
    click((1840, 55))


def run_meteorite(match: Match) -> None:
    """
    Execute the Meteorite Research navigational cleanup subroutine.

    Clears the active research panel viewport context by firing hardware
    inputs at the global exit anchors to restore primary dashboard visibility.

    Args:
        match (Match): The detected visual anchor triggering this task execution.
    """
    check_emergency_stop()
    click((1840, 55))


def run_pickaxe(match: Match) -> None:
    """
    Execute the Pickaxe tool allocation and interaction routine.

    Interacts with the localized mining area coordinates before triggering
    global exit anchors to return execution back to the primary canvas.

    Args:
        match (Match): The detected visual anchor triggering this task execution.
    """
    check_emergency_stop()
    click((690, 660))
    click((1840, 55))


def run_quests(match: Match) -> None:
    """
    Execute the quest completion and collection protocol.

    Navigates through multiple quest category tabs and sequentially triggers 
    claim buttons using fixed index ranges to collect accumulated rewards.

    Args:
        match (Match): The detected visual anchor triggering this task execution.
    """
    check_emergency_stop()
    click((760, 130))
    for _ in range(5):
        check_emergency_stop()
        click((1450, 300))
        sleep(1)
        
    check_emergency_stop()
    click((1170, 130))
    for _ in range(5):
        check_emergency_stop()
        click((1450, 300))
        sleep(1)
        
    check_emergency_stop()
    click((1840, 55))


def run_tavern(match: Match) -> None:
    """
    Manage the tavern dispatch queue and resource accumulation.

    Phase 1 checks for active ready indicators using pixel color validation 
    and deploys available assets. Phase 2 exits the subsystem once depletion holds.

    Args:
        match (Match): The detected visual anchor triggering this task execution.
    """
    while check_emergency_stop():
        if color_at(400, 640) == 'yellow':
            click((400, 640))
            sleep(0.5)
        else:
            click((1670, 270))
            break
            
    check_emergency_stop()
    click((1840, 55))

