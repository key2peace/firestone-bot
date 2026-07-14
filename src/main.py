"""
Main Entry Point and Workflow Runner for Firestone Bot.

Acts as the central orchestrator, executing modular gameplay subroutines
while monitoring the application lifecycle and emergency shutdown signals.
"""
import os
import time
import task_logic

from custom_core import (
    click,
    color_at,
    Debug,
    drag_drop,
    duration_text,
    move_to,
    pause_check,
    Region,
    reload_file,
    tasks,
    timeouts
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
        Debug.history("[Crazygames] Going fullscreen")
        img.click()
        img.waitVanish()

    # Crazygames gamebar
    if color_at(735, 1060) == "gamebar":
        Debug.history("[Crazygames] Disabling bottom gamebar")
        click((960, 1050))

def timeout_reinit() -> None:
    """
    Clean some timeouts
    """
    global timeouts

    for _, (_, task_function_name, reset_on_reload) in tasks.items():
        if reset_on_reload and task_function_name in timeouts:
            del timeouts[task_function_name]

def main() -> None:
    """
    Execute the primary automation lifecycle loop in local scope.

    Coordinates sequential execution of task routines and ensures safe
    termination handling when lifecycle interrupt thresholds are breached.
    """
    global tasks, timeouts

    pause_check()

    Debug.info("[system] Firestone Bot engine active.")
    crazygames_check()

    try:
        flipper = True
        while True:
            pause_check()

            if os.path.exists(reload_file):
                os.remove(reload_file)
                crazygames_check()
                timeout_reinit()

            # loop through tasks
            for name, (pattern, task_function_name, _) in tasks.items():
                friendly_name = name.replace('_', ' ').title()

                if task_function_name in timeouts and timeouts[task_function_name] >= time.time():
                    continue

                pause_check()

                if pattern:
                    match = None
                    match_count = 0
                    thearea = main_finished
                    for _ in range(1, 5):
                        match = thearea.exists('images/tasks/' + pattern)
                        if match:
                            thearea = match
                            match_count += 1
                    if not match or match_count < 2:
                        continue

                    Debug.history(f"[Tasks] {friendly_name} detected")
                    match.click()
                    match.move_mouse_away()
                    time.sleep(2)

                if hasattr(task_logic, task_function_name):
                    start_task = time.time_ns()
                    actual_function = getattr(task_logic, task_function_name)

                    Debug.history(f"[Task] {friendly_name} - Launching {task_function_name}")
                    if pattern:
                        timeout_return = int(actual_function()) # pylint: disable=assignment-from-no-return
                    else:
                        timeout_return = int(actual_function(True)) # pylint: disable=assignment-from-no-return
                    if timeout_return:
                        timeouts[task_function_name] = int(timeout_return)
                        timeout_return = duration_text(time.time_ns(), timeout_return*1000000000)
                    if color_at(1777, 87) == 'white':
                        click((1777, 87))
                    duration = duration_text(start_task)
                    Debug.history(f"[Task] {friendly_name} - Finished in {duration} (return: {timeout_return})")
                else:
                    Debug.history(f"[Task] {friendly_name} - Missing handler '{task_function_name}'")

            #check amount of tasks, scroll to check if we can find more non timeouted ones in the list
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

            # check if we got mail
            mail_count = Region(100, 570, 50, 38).get_number()
            if mail_count:
                click((60, 620))
                time.sleep(1)
                while not color_at(1600, 980) == 'lightbrown':
                    if color_at(1320, 830) == 'green':
                        click((1320, 840))
                        time.sleep(0.3)
                        click((1190, 720))
                        time.sleep(0.3)
                    click((1600, 980))
                    time.sleep(0.3)
                click((1650, 40))

    except KeyboardInterrupt as e:
        Debug.error(f"Received Exception\n{e}")

if __name__ == "__main__":
    # Ensure top-level entry point isolation for compiled binary stability
    main()
