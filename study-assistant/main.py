import argparse
import os
import sys

from core.reader import scan_directory, read_file
from core.summarizer import generate_summary
from core.mindmap_gen import generate_mindmap
from core.quiz_gen import generate_quiz, format_quiz_markdown


def main():
    parser = argparse.ArgumentParser(
        description="Study Assistant - Generate summaries, mind maps, and quizzes from text files and PDFs."
    )
    parser.add_argument("--dir", required=True, help="Directory with text files and PDFs")
    parser.add_argument("--output", default=None, help="Output base directory (default: output/ next to the script)")
    parser.add_argument("--summaries", action="store_true", help="Generate summaries")
    parser.add_argument("--mindmaps", action="store_true", help="Generate mind maps")
    parser.add_argument("--quizzes", action="store_true", help="Generate quizzes")
    parser.add_argument("--all", action="store_true", help="Generate all output types")
    args = parser.parse_args()

    if not any([args.summaries, args.mindmaps, args.quizzes, args.all]):
        print("Error: specify at least one of --summaries, --mindmaps, --quizzes, or --all", file=sys.stderr)
        sys.exit(1)

    if args.all:
        args.summaries = True
        args.mindmaps = True
        args.quizzes = True

    output_base = args.output or os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

    files = scan_directory(args.dir)
    if not files:
        print("No .txt or .pdf files found in", args.dir, file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(files)} file(s) in {args.dir}")
    for f in files:
        print(f"  {f['name']} ({f['size']} bytes)")
    print()

    for f in files:
        print(f"Processing: {f['name']}")
        try:
            text = read_file(f["path"])
        except Exception as e:
            print(f"  Error reading file: {e}", file=sys.stderr)
            continue

        base = f["name"].rsplit(".", 1)[0]

        if args.summaries:
            outdir = os.path.join(output_base, "summaries")
            os.makedirs(outdir, exist_ok=True)
            summary = generate_summary(text)
            outpath = os.path.join(outdir, f"{base}_summary.md")
            with open(outpath, "w", encoding="utf-8") as fout:
                fout.write(f"# Summary: {f['name']}\n\n{summary}\n")
            print(f"  Summary -> {outpath}")

        if args.mindmaps:
            outdir = os.path.join(output_base, "mindmaps")
            os.makedirs(outdir, exist_ok=True)
            mindmap = generate_mindmap(text, title=f["name"])
            outpath = os.path.join(outdir, f"{base}_mindmap.md")
            with open(outpath, "w", encoding="utf-8") as fout:
                fout.write(mindmap)
            print(f"  Mind map -> {outpath}")

        if args.quizzes:
            outdir = os.path.join(output_base, "quizzes")
            os.makedirs(outdir, exist_ok=True)
            questions = generate_quiz(text)
            quiz = format_quiz_markdown(questions, title=f"{f['name']} Quiz")
            outpath = os.path.join(outdir, f"{base}_quiz.md")
            with open(outpath, "w", encoding="utf-8") as fout:
                fout.write(quiz)
            print(f"  Quiz -> {outpath}")

    print("\nDone.")


if __name__ == "__main__":
    main()
