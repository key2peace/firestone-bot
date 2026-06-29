import bot_helper as bh

from custom_core import *
from org.sikuli.basics import Debug as JDebug


def run_arcane_crystal(match):
    """Perform Arcane Crystal Task"""
    click((1840, 55))

def run_arena_of_kings(match):
    """Perform Arena of Kings Task"""
    click((1855, 115))

def run_campaign(match):
    """Perform Campaign Task"""
    _screen = Region(0, 0, 1920, 1080)
    task_campaign_dm = 'images/tasks/campaign/daily_missions.png'
    task_campaign_liberate = 'images/tasks/campaign/liberate.png'
    task_campaign_liberate_ok = 'images/tasks/campaign/liberate_ok.png'
    click((115, 1000))
    try:
        img = _screen.exists(task_campaign_dm)
        if img:
            JDebug.history("[Campaign] Heading for daily missions")
            img.click()
            img.waitVanish(img, task_campaign_dm)
            bh.do_capture('campaign_dm.png')
            JDebug.history("[Campaign] Heading for Liberations")
            click((685, 820))
            sleep(1)
            bh.do_capture('campaign_liberation.png')
            try:
                #todo rewrite to use colors
                img2 = find(task_campaign_liberate)
                if img2:
                    JDebug.history("[Campaign] Select Liberation")
                    img2.click()
                    img3 = _screen.wait(task_campaign_liberate_ok, 300)
                    if img3:
                        JDebug.history("[Campaign] Finished Liberation?")
                        bh.do_capture('campaign_liberate_done.png')
                        img3.click()
                        img3.waitVanish()
                dragDrop((1130,430), (730,430))
            except Exception as e:
                JDebug.error("[Campaign] Liberation\n%s", str(e))
            click((1820, 70))
        click((1510, 90))
        click((1840, 60))
    except Exception as e:
        pass

def run_check_upgrade():
    """Check if hero's can be upgraded"""
    main_upgrade = Region(1661, 910, 259, 170)

    target_mode = str(bh.CONFIG['upgrade_mode']).lower()
    while starget_mode not in main_upgrade.text().lower():
        main_upgrade.click()
        main_upgrade.moveMouseAway()

def run_engineer(match):
    """Perform Engineer Task"""
    click((1620, 730))
    click((1840, 55))

def run_firestone_collect(match):
    """Perform Firestone Collection Task"""
    click((1840, 55))

def run_firestone_research(match):
    """Perform Firestone Research Task"""
    task_firestone_research_bubble = 'images/tasks/firestone/research_bubble.png'
    task_firestone_research_slotsfull = 'images/tasks/firestone/research_slotsfull.png'
    while bh.BOT_RUNNING and bh.color_at(540, 970) == 'green':
        click((540, 970))
        sleep(1)
    while bh.BOT_RUNNING:
        x = 0
        try:
            img = exists(task_firestone_research_bubble)
            if img:
                JDebug.error("[Firestone Research] Selecting Research")
                bh.doDebug(img, 'Firestone Research - Bubble')
                img.click()
                sleep(1)
                click((790, 720))
        except Exception as e:
            dragDrop((1130,430), (730,430))
            x = x + 1
        if x == 10:
            break
        try:
            img = exists(task_firestone_research_slotsfull)
            if img:
                JDebug.error("[Firestone Research] Research slots full")
                click((1400, 350))
                sleep(1)
                click((1250, 200))
                break
            click((1840, 55))
        except Exception as e:
            pass

def run_guild_expeditions(match):
    """Perform Guild Expeditions Task"""
    for c in [(1290, 330), (1290, 330), (1510, 70)]:
        sleep(0.5)
        click((c))

def run_hero_upgrade():
    """Ensure the upgrade multiplier is set to the configured setting"""
    while bh.BOT_RUNNING:
        x = 0
        for m in [115, 640, 810, 1010, 1200, 1380, 1600]:
            if bh.color_at(m, 930) == 'yellow':
                click((m, 950))
                sleep(0.5)
            else:
                x = x + 1
        if x == 7:
            break

def run_map(match):
    """Perform Map Task"""
    task_map_okay = 'images/tasks/map/okay.png'
    task_map_zoom = 'images/tasks/map/zoom.png'
    while bh.color_at(170, 320) == 'green':
        click((170, 320))
        sleep(1)
        click((950, 650))
        sleep(0.5)
    try:
        zoom_match = exists(task_map_zoom)
        if zoom_match:
            dragDrop(zoom_match, (1290,1040))
    except Exception as e:
        JDebug.error("[Map] Unable to zoom\n%s", str(e))
    for type in ['scout','adventure', 'war', 'monster']:
        missions = findAllList('images/tasks/map/mission/'+type+'.png')
        if missions:
            for m in missions:
                m.click()
                m.waitVanish()
                if bh.color_at(1090, 870) == 'green':
                    click((1090, 870))
                    sleep(0.5)
    click((1840, 55))

def run_meteorite(match):
    """Perform Meteorite Research Task"""
    click((1840, 55))

def run_pickaxe(match):
    """Perform Pickaxes Task"""
    click((690, 660))
    click((1840, 55))

def run_quests(match):
    """Perform Quests Task"""
    click((760, 130))
    for n in range(0, 5):
        click((1450, 300))
        sleep(1)
    click((1170, 130))
    for n in range(0, 5):
        click((1450, 300))
        sleep(1)
    click((1840, 55))

def run_tavern(match):
    """Perform Tavern Task"""
    while bh.BOT_RUNNING:
        if bh.color_at(400, 640) == 'yellow':
            click((400,640))
            sleep(0.5)
        else:
            click((1670,270))
            break
    click((1840,55))
