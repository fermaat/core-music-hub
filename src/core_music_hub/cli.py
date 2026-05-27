"""Ad-hoc smoke testing CLI.

Usage:
    python -m core_music_hub.cli list
    python -m core_music_hub.cli play <alias>
    python -m core_music_hub.cli stop
    python -m core_music_hub.cli status
"""

import argparse

from core_music_hub.client.client import MusicHubClient


def main() -> int:
    parser = argparse.ArgumentParser(prog="core_music_hub.cli")
    parser.add_argument("--server", default="http://127.0.0.1:8600", help="Server base URL")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    p_play = sub.add_parser("play")
    p_play.add_argument("alias")
    sub.add_parser("stop")
    sub.add_parser("status")

    args = parser.parse_args()
    client = MusicHubClient(base_url=args.server)

    if args.cmd == "list":
        for song in client.catalog():
            print(f"- {song['id']}: {song['title']} (moods: {song['moods']})")
    elif args.cmd == "play":
        result = client.play(alias=args.alias)
        print(f"Playing: {result['title']}")
    elif args.cmd == "stop":
        client.stop()
        print("Stopped.")
    elif args.cmd == "status":
        print(client.status())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
