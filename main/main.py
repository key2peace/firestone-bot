# Dynamically purge all local workspace modules from the memory cache before loading
try:
    import os
    import sys
    from org.sikuli.script import ImagePath
    from org.sikuli.basics import Debug as JDebug

    workspace_dir = str(ImagePath.getBundlePath())
    local_modules = [os.path.splitext(f)[0] for f in os.listdir(workspace_dir) if f.lower().endswith('.py') and f.lower() != 'main.py']

    for module_name in local_modules:
        if module_name in sys.modules:
            sys.modules.pop(module_name, None)

except Exception as e:
    JDebug.error("[ImportCacheClean] Failed dynamic module eviction:\n " + str(e))

import java.lang.System as JSystem
import task_logic
import bot_helper as bh

from custom_core import *

sleep(10)

# Crazygames dutch gamebar
try:
    img = exists('images/misc/gamebar_maximize.png')
    if img:
        JDebug.info("[Crazygames] Going fullscreen")
        img.click()
        img.waitVanish()
except:
    pass

# Crazygames gamebar
try:
    img = exists('images/misc/gamebar.png')
    if img:
        JDebug.info("[Crazygames] Disabling bottom gamebar")
        img.click()
        img.waitVanish()
except:
    pass

try:
    # Patterns
    main_finished = Region(0, 200, 130, 290)
    tasks = {
        'arcane_crystal': ('images/tasks/arcane_crystal.png', 'run_arcane_crystal'),
        'arena_of_kings': ('images/tasks/arena_of_kings.png', 'run_arena_of_kings'),
        'campaign':       ('images/tasks/campaign.png',       'run_campaign'),
        'engineer':       ('images/tasks/engineer.png',       'run_engineer'),
        'firestone_collect': ('images/tasks/firestone/collect.png', 'run_firestone_collect'),
        'firestone_research': ('images/tasks/firestone/research.png', 'run_firestone_research'),
        'guild_expeditions': ('images/tasks/guild_expeditions.png', 'run_guild_expeditions'),
        'map':            ('images/tasks/map.png',            'run_map'),
        'meteorite':      ('images/tasks/meteorite.png',      'run_meteorite'),
        'pickaxe':        ('images/tasks/pickaxe.png',        'run_pickaxe'),
        'quests':         ('images/tasks/quests.png',         'run_quests'),
        'tavern':         ('images/tasks/tavern.png',         'run_tavern')
    }
    task_logic.run_check_upgrade()
    JDebug.info("[Main] Entering main loop")
    while bh.BOT_RUNNING:
        task_logic.run_hero_upgrade()
        for name, (pattern, task_function_name) in tasks.items():
            friendly_name = name.replace('_', ' ').title()

            try:
                match = main_finished.exists(pattern)
                if match:
                    JDebug.history("[Tasks] %s detected", friendly_name)
                    match.highlight()
                    match.click()
                    match.waitVanish()
                    bh.doCapture(name+'.png')
                    if hasattr(task_logic, task_function_name):
                        start = JSystem.currentTimeMillis()
                        JDebug.history("[Tasks] %s - Launching %s", friendly_name, task_function_name)
                        actual_function = getattr(task_logic, task_function_name)
                        actual_function(match)
                        JDebug.history("[Tasks] %s - Finished in %s", friendly_name, bh.duration(start))
                    else:
                        JDebug.history("[Tasks] %s\nMissing handler %s", friendly_name, task_function_name)
            except Exception as e:
                JDebug.error("[Tasks] %s\n%s", friendly_name, str(e))

except KeyboardInterrupt as e:
    JDebug.info("[Main] Received KeyboardInterrupt\n%s", str(e))
except RuntimeError as e:
    JDebug.info("[Main] Received KeyboardInterrupt\n%s", str(e))
