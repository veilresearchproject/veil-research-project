"""Text-only, offline-first rehearsal; live conversation requires installed Ollama."""
import argparse
from cristal_reveal import CUES
from live_conversation import LiveConversation
from ollama_bridge import OllamaBridge
from voice_pipeline import VoicePipeline
from playback_adapter import play_remaining

def prepare_line(text):
    """Return a validated speech plan without playing audio."""
    return VoicePipeline(text)

def run_rehearsal(*, generate=None, question=None):
    """No microphone, network, or audio in this routine unless caller supplies a generator."""
    scripted = []
    for cue in CUES:
        plan = prepare_line(cue.spoken)
        scripted.append((cue.key, plan.plan.original))
    answer = None
    if question is not None:
        if generate is None:
            raise ValueError('An actual generator is required for unscripted questions')
        answer = LiveConversation(generate).ask(question)
        prepare_line(answer)
    return scripted, answer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help='Installed Ollama model; only needed with --question')
    parser.add_argument('--question', help='Ask a real local model instead of scripted dialogue')
    args = parser.parse_args()
    if args.question and not args.model:
        parser.error('--question requires --model')
    generator = OllamaBridge(args.model) if args.question else None
    scripted, answer = run_rehearsal(generate=generator, question=args.question)
    print('TEXT-ONLY REHEARSAL. No speech or facial animation.')
    for key, text in scripted:
        print(f'{key.upper()}: {text}')
    if answer is not None:
        print('LOCAL MODEL RESPONSE:', answer)

if __name__ == '__main__':
    main()
