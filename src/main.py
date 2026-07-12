"""
Main Entry Point and Workflow Runner for Firestone Bot.

Acts as the central orchestrator, executing modular gameplay subroutines
while monitoring the application lifecycle and emergency shutdown signals.
"""
import os
import time
import task_logic

from custom_core import (
    color_at,
    Debug,
    drag_drop,
    duration_text,
    move_to,
    pause_check,
    Region,
    reload_file,
    tasks
)

_screen = Region(0, 0, 1920, 1080)
main_finished = Region(0, 0, 160, 750)

def crazygames_check() -> None:
    """
    Check for crazygames specific elements
    """
    # Crazygames maximize game screen button
    img = _screen.exists('images/misc/gamebar_maximize.png')
    if img:
        Debug.info("[Crazygames] Going fullscreen")
        img.click()
        img.waitVanish()

    # Crazygames gamebar
    img = _screen.exists('images/misc/gamebar.png')
    if img:
        Debug.info("[Crazygames] Disabling bottom gamebar")
        img.click()
        img.waitVanish()

def main() -> None:
    """
    Execute the primary automation lifecycle loop in local scope.

    Coordinates sequential execution of task routines and ensures safe
    termination handling when lifecycle interrupt thresholds are breached.
    """
    global tasks

    pause_check()

    Debug.info("[system] Firestone Bot engine active.")
    crazygames_check()

    try:
        Debug.info("[Main] Entering main loop")
        flipper = True
        while True:
            pause_check()

            if os.path.exists(reload_file):
                os.remove(reload_file)
                Debug.info('Initianting reload')
                crazygames_check()
                tasks['check_upgrade'] = ('', 'run_check_upgrade', 0)

            # loop through tasks
            #start_tasks = time.time_ns()
            for name, (pattern, task_function_name, timeout) in tasks.items():
                friendly_name = name.replace('_', ' ').title()

                if timeout and timeout >= time.time():
                    continue

                pause_check()

                if pattern:
                    match = None
                    match_count = 0
                    thearea = main_finished
                    for _ in range(1, 5):
                        match = thearea.exists(pattern)
                        if match:
                            thearea = match
                            match_count += 1
                    if not match or match_count < 2:
                        continue

                    Debug.history("[Tasks] %s detected", friendly_name)
                    match.highlight(1)
                    match.click()
                    match.move_mouse_away()
                    time.sleep(1)

                if hasattr(task_logic, task_function_name):
                    start_task = time.time_ns()
                    actual_function = getattr(task_logic, task_function_name)

                    Debug.history("[Task] %s - Launching %s", friendly_name, task_function_name)
                    timeout_return = int(actual_function()) # pylint: disable=assignment-from-no-return
                    if timeout_return:
                        tasks[name] = (pattern, task_function_name, int(timeout_return))
                        timeout_return = duration_text(time.time_ns(), timeout_return*1000000000)
                    Debug.history("[Task] %s - Finished in %s (return: %s)", friendly_name, duration_text(start_task), str(timeout_return))
                else:
                    Debug.history("[Task] %s - Missing handler %s", friendly_name, task_function_name)

                if color_at(1777, 87) == 'white':
                    click((1777, 87))
            #Debug.history("[Tasks] Finished in %s", duration_text(start_tasks))

            task_count = Region(90, 160, 50, 38).get_number()
            if int(task_count) > 3:
                # drag around the area to reveal task images
                flipper = not flipper
                x = main_finished.get_x()+50
                y1 = main_finished.get_y()+250
                y2 = y1 + main_finished.get_h()
                for _ in range(0, 2):
                    if flipper:
                        drag_drop((x, y1), (x, y2))
                    else:
                        drag_drop((x, y2), (x, y1))
                move_to((x - 60, y1 - 60))

    except KeyboardInterrupt as e:
        Debug.info("[Main] Received Exception\n%s", str(e))

if __name__ == "__main__":
    # Ensure top-level entry point isolation for compiled binary stability
    main()
