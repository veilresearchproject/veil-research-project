"""Manual Windows voice smoke-test: local TTS only, no Ollama or internet."""
import signal_voice


def main():
    v = signal_voice.WindowsVoice()
    try:
        voices = v.list_voices()
        print('Installed Windows voices:', ', '.join(voices) if voices else '(none)')
        if not voices:
            print('No installed voice is enabled. Check Windows Speech settings.')
            return 2
        v.enable()
        line = 'Hello! I am SIGNAL. Today we are testing my local voice. The door remains unreasonably ordinary.'
        print('Speaking:', line)
        v.speak(line)
        input('Press Enter to stop the test (or allow the phrase to finish)...')
        return 0
    except (OSError, RuntimeError) as exc:
        print('Voice test could not run:', exc)
        return 1
    finally:
        v.disable()


if __name__ == '__main__':
    raise SystemExit(main())
