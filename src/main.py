"""
Main Entry Point and Workflow Runner for Firestone Bot.

Acts as the central orchestrator, executing modular gameplay subroutines
while monitoring the application lifecycle and emergency shutdown signals.
"""
import os
import time
import task_logic

from custom_core import (
    capture,
    Debug,
    duration_text,
    LOCKFILE,
    moveTo, 
    Region,
    sleep
)

from bot_helper import (
    tasks
)

def main() -> None:
    """
    Execute the primary automation lifecycle loop in local scope.

    Coordinates sequential execution of task routines and ensures safe
    termination handling when lifecycle interrupt thresholds are breached.
    """
    global tasks

    _screen = Region(0, 0, 1920, 1080)
    main_finished = Region(0, 200, 130, 290)

    while not os.path.exists(LOCKFILE):
        sleep(1)

    Debug.info("[system] Firestone Bot engine active.")

    # Crazygames dutch gamebar
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

    try:
        Debug.info("[Main] Entering main loop")
        while True:
            # Enforce execution suspension if the core state drops into fallback
            while not os.path.exists(LOCKFILE):
                sleep(1)
            for name, (pattern, task_function_name, timeout) in tasks.items():
                friendly_name = name.replace('_', ' ').title()

                if timeout and timeout >= time.time():
                    continue

                #start_tasks = time.time_ns()
                if len(pattern):
                    match = main_finished.exists(pattern)
                    if not match:
                        continue

                    Debug.history("[Tasks] %s detected", friendly_name)
                    match.highlight()
                    match.click()
                    moveTo((0,540))
                    sleep(2)
                    capture(name+'.png')

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
                    Debug.history("[Task] %s\nMissing handler %s", friendly_name, task_function_name)

                #Debug.history("[Tasks] Finished in %s", duration_text(start_tasks))

    except KeyboardInterrupt as e:
        Debug.info("[Main] Received Exception\n%s", str(e))

if __name__ == "__main__":
    # Ensure top-level entry point isolation for compiled binary stability
    main()
