#!/usr/bin/env python3
"""
Test runner for Project 06 (Hack Assembler).
It compiles all .asm files in the project 06 directories using both our custom
assembler and the official built-in course assembler, and verifies they are
identical line-for-line.
"""
import os
import subprocess
import sys

# Color codes for pretty printing
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def run_cmd(args: list, cwd: str = None) -> tuple:
    """Runs a shell command and returns (stdout, stderr, exit_code)."""
    try:
        res = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
        return res.stdout, res.stderr, res.returncode
    except Exception as e:
        return "", str(e), -1


def main():
    print(f"{BOLD}{CYAN}=================================================={RESET}")
    print(f"{BOLD}{CYAN}      NAND2TETRIS PROJECT 06 ASSEMBLER TESTER     {RESET}")
    print(f"{BOLD}{CYAN}=================================================={RESET}\n")

    project_dir = os.path.dirname(os.path.abspath(__file__))
    tools_dir = os.path.abspath(os.path.join(project_dir, "..", "..", "tools"))

    # Path to HackAssembler Java classpath
    classpath = (
        f"{tools_dir}/bin/classes:"
        f"{tools_dir}/bin/lib/Hack.jar:"
        f"{tools_dir}/bin/lib/HackGUI.jar:"
        f"{tools_dir}/bin/lib/Compilers.jar:"
        f"{tools_dir}/bin/lib/AssemblerGUI.jar:"
        f"{tools_dir}/bin/lib/TranslatorsGUI.jar"
    )

    # Subdirectories containing .asm files
    subdirs = ["add", "max", "pong", "rect", "shift"]

    test_files = []
    for subdir in subdirs:
        subdir_path = os.path.join(project_dir, subdir)
        if not os.path.isdir(subdir_path):
            continue
        for file in os.listdir(subdir_path):
            if file.lower().endswith(".asm"):
                test_files.append(os.path.join(subdir, file))

    test_files.sort()

    if not test_files:
        print(f"{RED}No .asm files found to test!{RESET}")
        sys.exit(1)

    print(f"Found {len(test_files)} assembly files to test.\n")
    print(f"{BOLD}{'Test Case':<30} | {'Status':<10}{RESET}")
    print("-" * 45)

    passed_count = 0
    failed_count = 0

    for test_rel_path in test_files:
        test_case_name = os.path.basename(test_rel_path)
        asm_path = os.path.join(project_dir, test_rel_path)
        base_path = os.path.splitext(asm_path)[0]
        hack_mine_path = base_path + ".hack.mine"
        hack_ref_path = base_path + ".hack"

        # 1. Run our assembler on the asm file
        # We invoke python3 Main.py <asm_path>
        our_assembler_args = ["python3", "Main.py", asm_path]
        _, err_mine, code_mine = run_cmd(our_assembler_args, cwd=project_dir)

        if code_mine != 0 or not os.path.exists(hack_ref_path):
            print(f"{test_case_name:<30} | {RED}FAILED{RESET} (Custom Assembler Error)")
            if err_mine:
                print(f"  Error: {err_mine.strip()}")
            failed_count += 1
            continue

        # Rename our output to .hack.mine
        if os.path.exists(hack_mine_path):
            os.remove(hack_mine_path)
        os.rename(hack_ref_path, hack_mine_path)

        # 2. Run the official assembler on the asm file
        official_assembler_args = [
            "java",
            "-classpath",
            classpath,
            "HackAssemblerMain",
            asm_path,
        ]
        _, err_ref, code_ref = run_cmd(official_assembler_args, cwd=project_dir)

        if code_ref != 0 or not os.path.exists(hack_ref_path):
            print(
                f"{test_case_name:<30} | {RED}FAILED{RESET} (Official Assembler Error)"
            )
            if err_ref:
                print(f"  Error: {err_ref.strip()}")
            # Clean up
            if os.path.exists(hack_mine_path):
                os.rename(hack_mine_path, hack_ref_path)
            failed_count += 1
            continue

        # 3. Compare the files line by line
        try:
            with open(hack_mine_path, "r") as f1, open(hack_ref_path, "r") as f2:
                lines_mine = [line.strip() for line in f1 if line.strip()]
                lines_ref = [line.strip() for line in f2 if line.strip()]

            if lines_mine == lines_ref:
                print(f"{test_case_name:<30} | {GREEN}PASSED{RESET}")
                passed_count += 1
            else:
                print(f"{test_case_name:<30} | {RED}FAILED{RESET} (Binary Discrepancy)")
                # Print the first mismatch
                min_len = min(len(lines_mine), len(lines_ref))
                mismatch_found = False
                for idx in range(min_len):
                    if lines_mine[idx] != lines_ref[idx]:
                        print(f"  Mismatch at instruction index {idx}:")
                        print(f"    Custom:   {lines_mine[idx]}")
                        print(f"    Official: {lines_ref[idx]}")
                        mismatch_found = True
                        break
                if not mismatch_found:
                    print(
                        f"  Size Mismatch: Custom={len(lines_mine)} lines, Official={len(lines_ref)} lines."
                    )
                failed_count += 1

        except Exception as e:
            print(f"{test_case_name:<30} | {RED}ERROR{RESET} ({str(e)})")
            failed_count += 1
        finally:
            # Restore our output back to .hack and clean up .hack.mine
            if os.path.exists(hack_mine_path):
                if os.path.exists(hack_ref_path):
                    os.remove(hack_ref_path)
                os.rename(hack_mine_path, hack_ref_path)

    print("-" * 45)
    print(f"\n{BOLD}Test Summary:{RESET}")
    print(f"  Passed: {GREEN}{passed_count}{RESET}")
    print(f"  Failed: {RED if failed_count > 0 else GREEN}{failed_count}{RESET}")
    print(f"{BOLD}{CYAN}=================================================={RESET}")


if __name__ == "__main__":
    main()
