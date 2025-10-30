from threading import Thread
from typing import Callable, Any, List, Optional
from pm4py.util import constants


class Pm4pyThreadManager:
    """
    A lightweight manager to optionally run submitted callables in threads.

    Args:
        is_threaded (bool): If True, `submit` runs the function in a new thread
                            and `join` waits for all threads to finish.
                            If False, `submit` runs synchronously and `join` does nothing.
    """
    def __init__(self, is_threaded: Optional[bool] = None) -> None:
        if is_threaded is None:
            is_threaded = constants.DEFAULT_IS_THREADING_MANAGEMENT_ENABLED
        self.is_threaded = is_threaded
        self._threads: List[Thread] = []

    def submit(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Optional[Any]:
        """
        Submit a function to run with the provided args/kwargs.

        - If `is_threaded` is True, starts a thread and returns None immediately.
        - If `is_threaded` is False, runs synchronously and returns the function's result.
        """
        if self.is_threaded:
            t = Thread(target=func, args=args, kwargs=kwargs)
            self._threads.append(t)
            t.start()
            return None
        else:
            return func(*args, **kwargs)

    def join(self) -> None:
        """
        Wait for all threads to complete when `is_threaded` is True.
        Does nothing when `is_threaded` is False.
        """
        if not self.is_threaded:
            return
        for t in self._threads:
            t.join()
        self._threads.clear()
