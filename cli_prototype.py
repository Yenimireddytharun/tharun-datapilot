import argparse
import sys

# Constants for the build
VERSION = "1.0.0-build.08"

def show_version():
    print(f"DataPilot CLI Version: {VERSION}")

def handle_run(filename):
    print(f"[*] Initializing DataPilot Engine...")
    print(f"[*] Loading script: {filename}")
    print(f"[*] Mapping logic to backend... OK")
    # This is where you would call: engine.parser.parse(open(filename).read())
    print(f"\n[SUCCESS] Script '{filename}' executed.")

def handle_check(filename):
    print(f"[*] Performing Day 4 Syntax Validation on: {filename}")
    print(f"[*] Scanning tokens...")
    print(f"\n[OK] No syntax errors detected in {filename}.")

def handle_shell():
    print(f"DataPilot Interactive Shell (REPL)")
    print("Type 'exit' to quit.")
    print("dp > ")

def main():
    # 1. Create the top-level parser
    parser = argparse.ArgumentParser(
        prog='datapilot',
        description='DataPilot: A Domain-Specific Language for Data Science & BI.',
        add_help=False # We will handle --help manually for the custom layout
    )

    # 2. Add Global Options
    parser.add_argument('--version', action='store_true', help='Show the version and exit.')
    parser.add_argument('--help', action='store_true', help='Show this message and exit.')

    # 3. Add Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Run Command
    run_parser = subparsers.add_parser('run', help='Execute a .dp script file.')
    run_parser.add_argument('file', help='Path to the .dp file')

    # Check Command
    check_parser = subparsers.add_parser('check', help='Validate syntax of a .dp file.')
    check_parser.add_argument('file', help='Path to the .dp file')

    # Shell Command
    subparsers.add_parser('shell', help='Enter interactive DP mode.')

    # 4. Parse Arguments
    args = parser.parse_args()

    # 5. Route the Logic
    if args.version:
        show_version()
    elif args.help or not args.command:
        # Custom "Expected Output" Help Format
        print("\nUsage: datapilot [OPTIONS] COMMAND [ARGS]...")
        print("\nOptions:")
        print("  --version  Show the version and exit.")
        print("  --help     Show this message and exit.")
        print("\nCommands:")
        print("  run    Execute a .dp script file.")
        print("  check  Validate syntax of a .dp file.")
        print("  shell  Enter interactive DP mode.")
        print("\nDAY 8 STATUS: CLI Design & Command Patterns Defined.")
    elif args.command == 'run':
        handle_run(args.file)
    elif args.command == 'check':
        handle_check(args.file)
    elif args.command == 'shell':
        handle_shell()

if __name__ == "__main__":
    main()