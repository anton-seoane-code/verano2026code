import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Study Assistant - Generate summaries, mind maps, and quizzes from text files and PDFs.")
    parser.add_argument("--dir", required=True, help="Directory with text files and PDFs")
    parser.add_argument("--output", default="output", help="Output directory (default: output)")
    parser.add_argument("--summaries", action="store_true", help="Generate summaries")
    parser.add_argument("--mindmaps", action="store_true", help="Generate mind maps")
    parser.add_argument("--quizzes", action="store_true", help="Generate quizzes")
    parser.add_argument("--all", action="store_true", help="Generate all output types")
    args = parser.parse_args()

    if not any([args.summaries, args.mindmaps, args.quizzes, args.all]):
        print("Error: specify at least one of --summaries, --mindmaps, --quizzes, or --all")
        sys.exit(1)

    print(f"Study Assistant")
    print(f"  Input dir:  {args.dir}")
    print(f"  Output dir: {args.output}")
    print("Not yet implemented.")


if __name__ == "__main__":
    main()
