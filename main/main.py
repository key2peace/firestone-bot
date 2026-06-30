"""
Main Entry Point and Workflow Runner for Firestone Bot.

Acts as the central orchestrator, executing modular gameplay subroutines
while monitoring the application lifecycle and emergency shutdown signals.
"""
import time
import task_logic

from custom_core import *


def main() -> None:
    """
    Execute the primary automation lifecycle loop in local scope.
    
    Coordinates sequential execution of task routines and ensures safe
    termination handling when lifecycle interrupt thresholds are breached.
    """
    sleep(10)
    Debug.info("[system] Firestone Bot engine active. Starting main loop.")

    # Crazygames dutch gamebar
    try:
        img = exists('images/misc/gamebar_maximize.png')
        if img:
            Debug.info("[Crazygames] Going fullscreen")
            img.click()
            img.waitVanish()
    except Exception as e:
        pass

    # Crazygames gamebar
    try:
        img = exists('images/misc/gamebar.png')
        if img:
            Debug.info("[Crazygames] Disabling bottom gamebar")
            img.click()
            img.waitVanish()
    except Exception as e:
        pass

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
    
    try:
        task_logic.run_check_upgrade()
        Debug.info("[Main] Entering main loop")
        while check_emergency_stop():
            task_logic.run_hero_upgrade()
            for name, (pattern, task_function_name) in tasks.items():
                friendly_name = name.replace('_', ' ').title()

                match = main_finished.exists(pattern)
                if match:
                    Debug.history("[Tasks] %s detected", friendly_name)
                    match.highlight()
                    match.click()
                    match.waitVanish()
                    capture(name+'.png')
                    if hasattr(task_logic, task_function_name):
                        start = time.time_ns()
                        Debug.history("[Tasks] %s - Launching %s", friendly_name, task_function_name)
                        actual_function = getattr(task_logic, task_function_name)
                        actual_function(match)
                        Debug.history("[Tasks] %s - Finished in %s", friendly_name, duration(start))
                    else:
                        Debug.history("[Tasks] %s\nMissing handler %s", friendly_name, task_function_name)

    except (KeyboardInterrupt, RuntimeError) as e:
        Debug.info("[Main] Received Exception\n%s", str(e))

if __name__ == "__main__":
    # Ensure top-level entry point isolation for compiled binary stability
    main()