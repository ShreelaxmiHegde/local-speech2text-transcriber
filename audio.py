import sys
import msvcrt
from transcriber import AudioTranscriber


def run_cli():
    transcriber = AudioTranscriber()
    print("\033[93mStarting microphone...\033[0m")

    ok, msg = transcriber.start()
    if not ok:
        print(f"\033[91mError starting microphone: {msg}\033[0m")
        return

    print("Controls:")
    print("  [p]     - Pause")
    print("  [r]     - Resume")
    print("  [Enter] - Stop & Transcribe\n")

    try:
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()

                # p - pause
                if key == b'p':
                    ok, _ = transcriber.pause()
                    if ok:
                        print("\033[95mPAUSED\033[0m")

                # r - resume
                elif key == b'r':
                    ok, _ = transcriber.resume()
                    if ok:
                        print("\033[96mRESUMED\033[0m")

                # enter - finalize
                elif key == b'\r':
                    print("\033[94mRECORDED\033[0m")
                    break
    except KeyboardInterrupt:
        print("\n\033[93mInterrupted by user.\033[0m")

    result = transcriber.stop_and_transcribe()
    if result.get("success"):
        if result.get("text"):
            print("\n\033[92mTranscription complete and saved to storage.\033[0m")
        else:
            print("\n\033[93mNo audio/speech detected.\033[0m")
    else:
        print(f"\n\033[91mTranscription failed: {result.get('error')}\033[0m")


if __name__ == "__main__":
    if "--server" in sys.argv:
        from server import run_server
        run_server()
    else:
        run_cli()