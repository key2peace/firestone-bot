"""
Main Entry Point and Workflow Runner for Firestone Bot.

Acts as the central orchestrator, executing modular gameplay subroutines
while monitoring the application lifecycle and emergency shutdown signals.
"""
import os
import re
import sys
import time
import task_logic

from custom_core import (
    color_at,
    colormap,
    Debug,
    duration_text,
    main_finished,
    pause_check,
    Region,
    reload_file,
    screen,
    tasks,
    timeouts
)

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
        if event == "line":
            if time.time() > self.deadline:
                raise TimeoutError("Task time limit exceeded")
        return self._trace_callback

def main() -> None:
    """
    Execute the primary automation lifecycle loop in local scope.
    """
    global timeouts

    pause_check()
    Debug.info('[system] Firestone Bot engine active.')

    stats_fp = False
    try:
        stats_file = '.bot-stats'
        stats_fp = open(stats_file, mode='at', encoding='utf-8')
        if not os.path.isfile(stats_file):
            stats_fp.write('Timestamp\tFunction\tDuration\n')
    except OSError as e:
        Debug.error(f'[Main] error occured opening stats file\n{e}')

    try:
        while True:
            pause_check()

            if os.path.exists(reload_file):
                os.remove(reload_file)
                for _, (_, task_function_name, reset_on_reload, _) in tasks.items():
                    if reset_on_reload and task_function_name in timeouts:
                        del timeouts[task_function_name]

            # loop through tasks
            for name, (pattern, task_function_name, _, max_runtime) in tasks.items():
                friendly_name = name.replace('_', ' ').title()

                if task_function_name in timeouts and timeouts[task_function_name] >= time.time():
                    if not pattern or (pattern and name not in ['alchemist', 'firestone_research', 'map']):
                        continue

                pause_check()

                # Ensure we end up on mainscreen
                while True:
                    m = screen.exists('images/misc/close.png')
                    if not m:
                        break
                    m.click()
                    m.wait_vanish()

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

                    Debug.history(f'[Tasks] {friendly_name} detected (Score: {match.get_score()})')
                    match.click()
                    match.move_mouse_away()
                    match.wait_vanish()
                    time.sleep(1)

                if hasattr(task_logic, task_function_name):
                    start_task = time.time_ns()
                    actual_function = getattr(task_logic, task_function_name)
                    runtime = max_runtime if max_runtime else 300

                    Debug.history(f'[Task] {friendly_name} - Launching {task_function_name}')
                    try:
                        with SequentialTaskTimeout(runtime):
                            if pattern:
                                timeout_return = int(actual_function()) # pylint: disable=assignment-from-no-return
                            else:
                                timeout_return = int(actual_function(True)) # pylint: disable=assignment-from-no-return
                    except TimeoutError:
                        Debug.warn(f'[Task] {friendly_name} aborted')
                        pass

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
                    if stats_fp:
                        stats_fp.write(f'{time.time_ns()}\t{task_function_name}\t{time.time_ns() - start_task}\n')
                else:
                    Debug.history(f'[Task] {friendly_name} is missing the handler \'{task_function_name}\'')

            if color_at(1186, 90) == 'red':
                hp = Region(840, 76, 310, 28).text('', colormap['white'])
                Debug.info(f'Enemy HP: {hp}')
                match = re.search(r'^([\d,]+)([a-zBKMT]+) HP$', hp)
                if match:
                    numeric, suffix = match.groups()
                    Debug.info(f'Numeric: {numeric} Suffix: {suffix}')

    except KeyboardInterrupt as error:
        Debug.error(f'Received KeyboardInterrupt\n{error}')
    except OSError as error:
        Debug.error(f'Received OSError\n{error}')
    finally:
        if stats_fp:
            stats_fp.close()

if __name__ == '__main__':
    main()
