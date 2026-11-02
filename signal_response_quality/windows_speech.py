"""Optional Windows SAPI speech adapter; blocking completion != audible proof."""
import sys
from typing import Callable

def speak_windows_blocking(text: str, *, speaker_factory: Callable | None = None) -> bool:
    """Use synchronous SAPI Speak via optional pywin32; fail closed.

    True means the synchronous engine call completed, not that audio was heard.
    No recording, network access, or software installation occurs.
    """
    if not text or not text.strip():
        return False
    if speaker_factory is None:
        if sys.platform != 'win32':
            raise RuntimeError('Windows SAPI is only available on Windows')
        try:
            from win32com.client import Dispatch
        except ImportError as exc:
            raise RuntimeError('Optional pywin32 is not installed') from exc
        speaker_factory = lambda: Dispatch('SAPI.SpVoice')
    speaker = speaker_factory()
    speaker.Speak(text, 0)
    return True
