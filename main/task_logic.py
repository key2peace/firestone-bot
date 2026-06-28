import bot_helper as bh
import java.lang.System as JSystem

from custom_core import *
from org.sikuli.basics import Debug as JDebug

main_upgrade = Region(1661, 910, 259, 170)
_screen = Region(0, 0, 1920, 1080)

# Check if the upgrade amount equals default
def main_check_upgrade():
    global main_upgrade

    target_mode = str(bh.config['upgrade_mode']).lower()
    while not target_mode in main_upgrade.text().lower():
        main_upgrade.click()
        main_upgrade.moveMouseAway()

# Check if we can upgrade hero's or specials
def main_hero_upgrade(): 
    while bh.bot_running:
        x = 0
        for m in [115, 640, 810, 1010, 1200, 1380, 1600]:
            if bh.colorAt(m, 930) == 'yellow':
                click((m, 950))
                sleep(0.5)
            else:
                x = x + 1
        if x == 7:
            break

# Arcane Crystal
def run_arcane_crystal(match):
    click((1840, 55))

# Arena of Kings
def run_arena_of_kings(match):
    click((1855, 115))

# Campaign
task_campaign_dm = 'images/tasks/campaign/daily_missions.png'
task_campaign_liberate = 'images/tasks/campaign/liberate.png'
task_campaign_liberate_ok = 'images/tasks/campaign/liberate_ok.png'
def run_campaign(match):
    global task_campaign_dm, task_campaign_liberate, task_campaign_liberate_ok
    
    click((115, 1000))
    try:
        img = _screen.exists(task_campaign_dm)
        if img:
            JDebug.history("[Campaign] Heading for daily missions")
            img.click()
            img.waitVanish(img, task_campaign_dm)
            bh.doCapture('campaign_dm.png')
            JDebug.history("[Campaign] Heading for Liberations")
            click((685, 820))
            sleep(1)
            bh.doCapture('campaign_liberation.png')
            try:
                #todo rewrite to use colors
                img2 = find(task_campaign_liberate)
                if img2:
                    JDebug.history("[Campaign] Select Liberation")
                    img2.click()
                    img3 = _screen.wait(task_campaign_liberate_ok, 300)
                    if img3:
                        JDebug.history("[Campaign] Finished Liberation?")
                        bh.doCapture('campaign_liberate_done.png')
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

# Engineer
def run_engineer(match):
    click((1620, 730))
    click((1840, 55))

# Firestone collect
def run_firestone_collect(match):
    click((1840, 55))

# Firestone Research
task_firestone_research_bubble = 'images/tasks/firestone/research_bubble.png'
task_firestone_research_slotsfull = 'images/tasks/firestone/research_slotsfull.png'
def run_firestone_research(match):
    global task_firestone_research_bubble, task_firestone_research_slotsfull

    while bh.bot_running and bh.colorAt(540, 970) == 'green':
        click((540, 970))
        sleep(1)
        
    while bh.bot_running:
        x = 0
        try:
            img = exists(task_firestone_research_bubble)
            if img:
                bh.doDebug(img, 'Firestone Research - Bubble')
                img.click()
                sleep(1)
                click((790, 720))
        except:
            dragDrop((1130,430), (730,430))
            x = x + 1
        
        if x == 10:
            break

        try:
            img = exists(task_firestone_research_slotsfull)
            if img:
                click((1400, 350))
                sleep(1)
                click((1250, 200))
                break

            click((1840, 55))
        except:
            pass

# Guild Expeditions
def run_guild_expeditions(match):
    for c in [(1290, 330), (1290, 330), (1510, 70)]:
        sleep(0.5)
        click((c))

# Map
task_map_okay = 'images/tasks/map/okay.png'
task_map_zoom = 'images/tasks/map/zoom.png'
def run_map(match):
    global task_map_okay, task_map_zoom
    while bh.colorAt(170, 320) == 'green':
        click((170, 320))
        sleep(1)
        click((950, 650))
        sleep(0.5)

    try:
        zoom_match = exists(task_map_zoom)
        if zoom_match:
            dragDrop(zoom_match, (1290,1040))
    except Exception as e:
        bh.doError(e, 'Map - Zoom')

    for type in ['scout','adventure', 'war', 'monster']:
        missions = findAllList('images/tasks/map/mission/'+type+'.png')
        if missions:
            for m in missions:
                m.click()
                m.waitVanish()
                if bh.colorAt(1090, 870) == 'green':
                    click((1090, 870))
                    sleep(0.5)
    click((1840, 55))

# Meteorite Research
def run_meteorite(match):
    click((1840, 55))

# Pickaxes
def run_pickaxe(match):
    click((690, 660))
    click((1840, 55))

# Quests
def run_quests(match):
    click((760, 130))
    for n in range(0, 5):
        click((1450, 300))
        sleep(1)
    click((1170, 130))
    for n in range(0, 5):
        click((1450, 300))
        sleep(1)
    click((1840, 55))

# Tavern
def run_tavern(match):
    while bh.bot_running:
        if bh.colorAt(400, 640) == 'yellow':
            click((400,640))
            sleep(0.5)
        else:
            click((1670,270))
            break
    #for now just return after shopping
    click((1840,55))