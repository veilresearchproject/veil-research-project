"""Optional offline setup readiness report; does not start a model or capture audio."""
import json
import signal_core
import signal_diagnostics


def main():
    print('SIGNAL v0.17 LOCAL READINESS CHECK — no downloads, speech or microphone capture')
    r = signal_diagnostics.run_checks(signal_core.MODEL, signal_core.signal_voice.WindowsVoice())
    for label, key in [('Ollama local model', 'ollama'), ('Windows speech output', 'voice'), ('Offline speech input', 'microphone')]:
        item = r[key]
        print(f'[{item["status"].upper()}] {label}: {item["message"]}')
    print('\nNEXT STEPS:', r['next_steps'])
    print('LIMITS:', r['notes'])
    print('A READY model listing does not prove the PC can run a full conversation.')

if __name__ == '__main__':
    main()
