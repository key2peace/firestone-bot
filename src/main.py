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
    duration_text,
    main_finished,
    pause_check,
    reload_file,
    tasks,
    timeouts
)

def main() -> None:
    """
    Execute the primary automation lifecycle loop in local scope.

    Coordinates sequential execution of task routines and ensures safe
    termination handling when lifecycle interrupt thresholds are breached.
    """
    global tasks, timeouts

    pause_check()

    Debug.info('[system] Firestone Bot engine active.')

    try:
        while True:
            pause_check()

            if os.path.exists(reload_file):
                os.remove(reload_file)
                timeout_reinit()

            # loop through tasks
            #start_tasks = time.time_ns()
            for name, (pattern, task_function_name, _) in tasks.items():
                friendly_name = name.replace('_', ' ').title()

                if task_function_name in timeouts and timeouts[task_function_name] >= time.time():
                    continue

                pause_check()

                if color_at(1777, 87) == 'white':
                    click((1777, 87))
                    time.sleep(2)

                if pattern and not color_at(110, 190) == 'red':
                    continue

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

                    Debug.history(f'[Tasks] {friendly_name} detected')
                    match.click()
                    match.move_mouse_away()
                    time.sleep(2)

                if hasattr(task_logic, task_function_name):
                    start_task = time.time_ns()
                    actual_function = getattr(task_logic, task_function_name)

                    Debug.history(f'[Task] {friendly_name} - Launching {task_function_name}')
                    if pattern:
                        timeout_return = int(actual_function()) # pylint: disable=assignment-from-no-return
                    else:
                        timeout_return = int(actual_function(True)) # pylint: disable=assignment-from-no-return

                    duration = duration_text(start_task)
                    if timeout_return:
                        if timeout_return == -1:
                            Debug.warn(f'[Task] {friendly_name} failed after {duration}')
                        else:
                            timeouts[task_function_name] = int(timeout_return)
                            timeout_return = duration_text(time.time_ns(), timeout_return*1000000000)
                            Debug.history(f'[Task] {friendly_name} finished in {duration} (timeout: {timeout_return})')
                    else:
                        Debug.history(f'[Task] {friendly_name} finished in {duration}')
                else:
                    Debug.history(f'[Task] {friendly_name} is missing the handler \'{task_function_name}\'')
            #Debug.history(f'[Tasks] Duration {duration_text(start_tasks)}')

    except KeyboardInterrupt as error:
        Debug.error(f'Received KeyboardInterrupt\n{error}')

def timeout_reinit() -> None:
    """
    Clean some timeouts
    """
    global timeouts

    for _, (_, task_function_name, reset_on_reload) in tasks.items():
        if reset_on_reload and task_function_name in timeouts:
            del timeouts[task_function_name]

if __name__ == '__main__':
    # Ensure top-level entry point isolation for compiled binary stability
    main()
