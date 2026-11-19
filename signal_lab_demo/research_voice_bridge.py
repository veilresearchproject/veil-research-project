"""Connect SIGNAL's verified synthetic context to its offline mock voice turn.

No model, audio device, network, hardware control, or file mutation is performed.
"""
from pathlib import Path

from brain_context import build_brain_context
from mock_voice import mock_voice_turn


def research_voice_turn(transcript, bundle_directory, speak):
    """Provide an on-demand verified, read-only snapshot to a mock spoken turn.

    The existing mock voice parser decides whether a context lookup is needed.
    It never accepts text supplied by the casebook as instructions.
    """
    if not isinstance(bundle_directory, (str, Path)):
        raise TypeError("Local synthetic bundle path required")
    if not callable(speak):
        raise TypeError("Speech sink must be callable")
    # The provider is lazy: greeting and equipment-control refusals do not
    # open the research bundle. Queries invoke the existing integrity gate.
    def verified_context():
        return build_brain_context(bundle_directory)

    result = mock_voice_turn(transcript, verified_context, speak)
    if result.get("synthetic_only") is not True or result.get("physical_control_allowed") is not False:
        raise ValueError("Unsafe mock voice response")
    return result
