import sys

from teacher_match.src.process_file import process_file


def main(args):
    if len(args) != 3:
        print(f"Usage: {args[0]} <input_file_path> <output_file_path>")
        exit(1)
    process_file(args[1], args[2])


if __name__ == '__main__':
    main(sys.argv)
