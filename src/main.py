"""
Main Entry Point and Workflow Runner for Firestone Bot.

Acts as the central orchestrator, executing modular gameplay subroutines
while monitoring the application lifecycle and emergency shutdown signals.
"""
import os
import sys
import time
import task_logic

from custom_core import (
    Debug,
    duration_text,
    main_finished,
    pause_check,
    platform,
    reload_event,
    timeouts
)

# name: (pattern, callable, reset_on_reload, max_runtime)
tasks = {
    # starting with these
    '_crazygames_check':    ('',                                'crazygames_check', 1, 5),
    '_check_party':         ('',                                'check_party', 1, 5),


    # alchemist
    'alchemist':            ('alchemist/alchemist.png',         'alchemist', 0, 0),

    # arena of kings
    'arena_of_kings':       ('arena_of_kings.png',              'arena_of_kings', 0, 0),

    #character
    'quests':               ('character/quests.png',            'character_quests', 0, 0),
    'talents':              ('character/talents_upgrade.png',   'character_talents', 0, 0),

    # engineer
    'engineer':             ('engineer/engineer.png',           'engineer', 0, 0),
    'garage':               ('engineer/garage.png',             'engineer_garage', 0, 0),
    #'garage_rarity':        ('engineer/garage_rarity.png',      'engineer_garage', 0, 0),
    'new_warmachine':       ('engineer/new_warmachine.png',     'engineer_garage', 0, 0),

    # guild
    'pickaxe':              ('guild/pickaxe.png',               'guild_shop_pickaxe', 0, 0),
    'arcane_crystal':       ('guild/arcane_crystal.png',        'guild_arcanecrystal', 0, 0),
    'awakening':            ('guild/awakening.png',             'guild_awakening', 0, 0),
    'chaos_rift_supplies':  ('guild/chaos_rift_supplies.png',   'guild_chaos_rift_supplies', 0, 0),
    'chaos_rift':           ('guild/chaos_rift.png',            'guild_chaos_rift', 0, 60),
    'expeditions':          ('guild/expeditions.png',           'guild_expeditions', 0, 0),
    'forbidden_knowledge':  ('guild/forbidden_knowledge.png',   'guild_forbidden_knowledge', 0, 0),
    'new_application':      ('guild/application.png',           'guild_new_application', 0, 0),

    # library
    'firestone_research':   ('library/firestone_research.png',  'library_firestone_research', 0, 0),
    'meteorite_research':   ('library/meteorite_research.png',  'library_meteorite_research', 0, 0),

    # map
    'campaign':             ('map/campaign.png',                'map_campaign', 0, 0),
    'map':                  ('map/map.png',                     'map_map', 0, 0),

    # oracle
    'oracle_gift':          ('oracle/gift.png',                 'oracle_gift', 0, 0),
    'oracle_rituals':       ('oracle/rituals.png',              'oracle', 0, 0),
    'oracle_blessing':      ('oracle/blessing.png',             'oracle', 0, 0),

    # pirate ship
    'pirates_price':        ('pirate_ship/pirates_price.png',   'pirates_price', 0, 0), #rework pickup method

    # shop
    'sign_in':              ('shop/sign_in.png',                'shop', 0, 300),

    # tavern
    'pharaos_vault':        ('tavern/pharaos_vault.png',        'tavern_pharaos_vault', 0, 0),
    'scarab_token':         ('tavern/scarab_token.png',         'tavern_scarab_token', 0, 0),
    'scarab_game':          ('tavern/scarab_game.png',          'tavern_scarab_game', 0, 0),
    'scarab_beast':         ('tavern/scarab_beast.png',         'tavern_scarab_game', 0, 0),
    'scarab_milestone':     ('tavern/scarab_milestone.png',     'tavern_scarab_milestone', 0, 0),
    'tavern_collect':       ('tavern/tavern_pickup.png',        'tavern_tavern_collect', 0, 0),

    # temple of eternals
    'temple_of_eternals':   ('temple_of_eternals.png',          'temple_of_eternals', 0, 0),

    # others on the end
    '_battle_pass':         ('',                                'battle_pass', 1, 0), # add golden pass purchase
    '_events':              ('',                                'events', 0, 0),
    '_alchemist':           ('',                                'alchemist', 0, 10),
    '_firestone_research':  ('',                                'library_firestone_research', 0, 0),
    'check_mail':           ('',                                'check_mail', 0, 0),
    'bag':                  ('',                                'bag', 0, 0),
    '_check_heroes':        ('',                                'check_heroes', 1, 60),
    '_guild':               ('',                                'guild', 0, 0),
    '_map':                 ('',                                'map_map', 0, 0),
    '_crazygames_error':    ('',                                'crazygames_error', 1, 0)
}

# Add magic quarter upgrades to the tasks
for tasks_root, _, tasks_files in os.walk('images/tasks/magic_quarter'):
    task_files = [f for f in tasks_files if f.lower().endswith('.png')]
    if not task_files:
        continue
    for task_filename in task_files:
        tasks_filepath = os.path.join('magic_quarter', task_filename)
        tasks.update({f'guardian_{task_filename[:-4]}': (tasks_filepath, 'magic_quarter', 0, 0)})

class SequentialTaskTimeout:
    """ Task checker."""
    def __init__(self, seconds: float):
        self.deadline = time.time() + seconds

    def __enter__(self):
        sys.settrace(self._trace_callback)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.settrace(None)

    def _trace_callback(self, frame, event, arg):
        if frame or arg:
            pass

        if event == 'line':
            if time.time() > self.deadline:
                raise TimeoutError('Task time limit exceeded')
        return self._trace_callback

def main() -> None:
    """ Execute the primary automation loop. """
    global timeouts

    pause_check()
    Debug.info(f'[system] Firestone Bot engine active. {platform}')

    stats_file = '.bot-stats'

    try:
        while True:
            pause_check()

            if reload_event.is_set():
                reload_event.clear()
                for _, (_, task_function_name, reset_on_reload, _) in tasks.items():
                    if reset_on_reload and task_function_name in timeouts:
                        timeouts.pop(task_function_name)

            # loop through tasks
            for name, (pattern, task_function_name, _, max_runtime) in tasks.items():
                friendly_name = name.replace('_', ' ').title()

                if task_function_name in timeouts and timeouts[task_function_name] >= time.time():
                    if not pattern or (pattern and name not in ['alchemist', 'firestone_research', 'map']):
                        continue

                pause_check()
                if reload_event.is_set():
                    break

                task_logic.go_home()

                last_m = 0
                if pattern:
                    m = None
                    match_count = 0
                    area = main_finished
                    for _ in range(1, 5):
                        m = area.exists('images/tasks/' + pattern)
                        if m:
                            area = m
                            last_m = m
                            match_count += 1
                    if match_count < 2:
                        continue
                    Debug.history(f'[Tasks] {friendly_name} detected (Score: {round(last_m.get_score(), 3)})')

                if hasattr(task_logic, task_function_name):
                    Debug.history(f'[Task] {friendly_name} - Launching {task_function_name}')

                    if last_m:
                        last_m.click()
                        #last_m.move_mouse_away()
                        last_m.wait_vanish()
                        time.sleep(1)

                    start_task = time.time_ns()
                    try:
                        runtime = max_runtime if max_runtime else 300
                        with SequentialTaskTimeout(runtime):
                            actual_function = getattr(task_logic, task_function_name)
                            arg = False if pattern else True
                            timeout_return = int(actual_function(arg)) # pylint: disable=assignment-from-no-return
                    except TimeoutError:
                        timeout_return = -2
                    duration = duration_text(start_task)

                    if timeout_return:
                        if timeout_return == -2:
                            Debug.warn(f'[Task] {friendly_name} timed out after {runtime} seconds')
                        elif timeout_return == -1:
                            Debug.warn(f'[Task] {friendly_name} failed after {duration}')
                        else:
                            timeouts.update({task_function_name: int(timeout_return)})
                            timeout_return = duration_text(time.time_ns(), timeout_return*1000000000)
                            Debug.history(f'[Task] {friendly_name} finished in {duration} (timeout: {timeout_return})')
                    else:
                        Debug.history(f'[Task] {friendly_name} finished in {duration}')
                        with open(stats_file, mode='at', encoding='utf-8') as fp:
                            if not os.path.isfile(stats_file):
                                fp.write('Function\tDuration\n')
                            fp.write(f'{task_function_name}\t{time.time_ns() - start_task // 1000000000}\n')
                else:
                    Debug.warn(f'[Task] {friendly_name} is missing the handler \'{task_function_name}\'')

    except KeyboardInterrupt as error:
        Debug.error(f'Received KeyboardInterrupt\n{error}')
    except OSError as error:
        Debug.error(f'Received OSError\n{error}')
    finally:
        if task_logic.mainscreen_thread.is_alive():
            task_logic.mainscreen_thread.join(1)

if __name__ == '__main__':
    main()
