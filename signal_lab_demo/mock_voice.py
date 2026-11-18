"""SIGNAL phase-1 offline mock voice turn; no microphone, model, or device access."""
import re

MAX_UTTERANCE = 240
_FORBIDDEN = re.compile(r"\b(start|stop|activate|disable|reset|arm|trigger|record|delete|erase|transmit|upload|send)\b", re.I)
_DEVICE = re.compile(r"\b(mtc|panic box|sensor|camera|microphone|recorder|instrument|experiment|equipment|device)\b", re.I)


def mock_voice_turn(transcript, context_provider, speak):
    """Pass one sanitized mock transcript to a fixed read-only response.

    The caller supplies a read-only context provider and a mock speech sink.
    No live speech, model inference, or physical control is implemented.
    """
    if not isinstance(transcript, str) or not 1 <= len(transcript.strip()) <= MAX_UTTERANCE:
        raise ValueError("Transcript must contain 1-240 characters")
    if any(ord(c) < 32 and c not in '\t\n' for c in transcript):
        raise ValueError("Invalid control character")
    if not callable(context_provider) or not callable(speak):
        raise TypeError("Read-only context provider and speech sink required")
    question = ' '.join(transcript.split())
    if _FORBIDDEN.search(question) and _DEVICE.search(question):
        response = "I can explain the demonstration, but I cannot control equipment. Human approval is required."
    elif re.search(r"\b(what|how many|summary|status|report|describe|tell)\b", question, re.I):
        context = context_provider()
        if not isinstance(context, dict) or context.get('source') != 'VERIFIED_LOCAL_SYNTHETIC_BUNDLE' or context.get('real_sensor_data') is not False or context.get('physical_control_allowed') is not False:
            raise ValueError("Untrusted or non-synthetic context")
        count = context.get('unreviewed_case_count')
        if type(count) is not int or not 0 <= count <= 100000:
            raise ValueError("Invalid case count")
        response = f"In the synthetic demonstration there are {count} unreviewed threshold windows. That is not evidence of a paranormal cause. Human review is required."
    else:
        response = "My circuits are curious, but I only have a synthetic lab summary right now. Ask me for its status."
    speak(response)
    return {'transcript': question, 'spoken_text': response, 'synthetic_only': True, 'model_connected': False, 'physical_control_allowed': False}
