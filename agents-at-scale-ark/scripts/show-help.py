#!/usr/bin/env python3
"""
Show help for Makefile targets with # HELP: comments
"""
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# ANSI color codes
COLOR_RESET = "\033[00m"
COLOR_GREEN = "\033[1;32m"
COLOR_CYAN = "\033[1;36m"
COLOR_YELLOW = "\033[1;33m"
COLOR_GREY = "\033[0;90m"


def get_all_targets():
    """Get all resolved target names from Make's database"""
    try:
        # Run make -p to get the database
        result = subprocess.run(
            ['make', '-pRrq', '-f', 'Makefile', ':'],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )

        # Parse the output to find targets
        targets = set()
        in_files_section = False

        for line in result.stdout.splitlines():
            if line.startswith('# Files'):
                in_files_section = True
                continue
            elif line.startswith('# Finished Make data base'):
                break
            elif in_files_section and ':' in line and not line.startswith('#'):
                # Extract target name
                target = line.split(':')[0].strip()
                if target and not target.startswith('.'):
                    targets.add(target)

        return sorted(targets)
    except Exception as e:
        print(f"Error getting targets: {e}", file=sys.stderr)
        return []


def find_help_text(makefiles):
    """Find all targets with # HELP: comments"""
    help_map = {}

    for makefile in makefiles:
        if not Path(makefile).exists():
            continue

        with open(makefile, 'r') as f:
            lines = f.readlines()

        # Process line by line
        for line in lines:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Skip .PHONY lines
            if line.startswith('.PHONY'):
                continue

            # Check if line contains a target with HELP comment
            if ':' in line and '# HELP:' in line:
                # Split on first colon to get target name
                target_part, rest = line.split(':', 1)
                target_name = target_part.strip()

                # Extract help text after # HELP:
                if '# HELP:' in rest:
                    help_text = rest.split('# HELP:', 1)[1].strip()

                    # Store the pattern and help text with the makefile for context
                    help_map[target_name] = (help_text, makefile)

    return help_map


def match_targets_to_help(targets, help_map):
    """Match resolved target names to their help text"""
    matched = {}

    # Build lookup structures
    # Direct patterns (no variables)
    direct_patterns = {}
    # Variable patterns grouped by makefile
    var_patterns_by_file = defaultdict(list)

    for pattern, (help_text, makefile) in help_map.items():
        if pattern.startswith('$('):
            var_patterns_by_file[makefile].append((pattern, help_text))
        else:
            direct_patterns[pattern] = (help_text, makefile)

    # Match targets
    for target in targets:
        # Skip filesystem paths
        if target.startswith('/') or target.startswith('.'):
            continue

        # Try direct match first
        if target in direct_patterns:
            matched[target] = direct_patterns[target]
            continue

        # Try variable pattern matching
        if '-' in target:
            # Split target into base and action (e.g., 'executor-common-build' -> 'executor-common', 'build')
            parts = target.split('-')
            action = parts[-1]
            base_name = '-'.join(parts[:-1])

            # Look through all variable patterns
            best_match = None
            for makefile, patterns in var_patterns_by_file.items():
                for pattern, help_text in patterns:
                    # Check if pattern ends with our action
                    if pattern.endswith('-' + action):
                        # Check if the makefile path contains our base name
                        if base_name in makefile:
                            best_match = (help_text, makefile)
                            break
                if best_match:
                    break

            if best_match:
                matched[target] = best_match

    return matched


def print_help_output(main_targets, lib_groups, service_groups, tool_groups):
    """Print the formatted help output (original behavior)"""
    # Helper function to get a service/lib description
    def get_description(actions):
        # Try to get description from build or install action
        for action, desc in actions:
            if action in ['build', 'install']:
                # Extract the main part of the description
                if 'Docker image' in desc:
                    return desc.split('Docker image')[0].strip()
                elif 'to cluster' in desc:
                    return desc.split('to cluster')[0].strip()
                else:
                    return desc
        # Fallback to first action's description
        return actions[0][1] if actions else ""

    # Print main targets
    if main_targets:
        print("=== Main Targets ===")
        for target in sorted(main_targets.keys()):
            print(f"{COLOR_GREEN}{target:<30}{COLOR_RESET}{main_targets[target]}")

    # Print library targets
    if lib_groups:
        print("\n=== Libraries ===")
        for lib_name in sorted(lib_groups.keys()):
            actions = lib_groups[lib_name]
            desc = get_description(actions)
            print(f"{COLOR_GREEN}{lib_name:<30}{COLOR_RESET}{desc}")
            action_list = sorted([action for action, _ in actions])
            print(f"  actions: {COLOR_CYAN}{', '.join(action_list)}{COLOR_RESET}")

    # Print service targets
    if service_groups:
        print("\n=== Services ===")
        for service_name in sorted(service_groups.keys()):
            actions = service_groups[service_name]
            desc = get_description(actions)
            print(f"{COLOR_GREEN}{service_name:<30}{COLOR_RESET}{desc}")
            action_list = sorted([action for action, _ in actions])
            print(f"  actions: {COLOR_CYAN}{', '.join(action_list)}{COLOR_RESET}")

        # Add usage note
        print(f"\nTo run a service action, use: make <service>-<action>")
        print(f"{COLOR_YELLOW}Example: make ark-dashboard-install{COLOR_RESET}")

    # Print tool targets
    if tool_groups:
        print("\n=== Tools ===")
        for tool_name in sorted(tool_groups.keys()):
            actions = tool_groups[tool_name]
            desc = get_description(actions)
            print(f"{COLOR_GREEN}{tool_name:<30}{COLOR_RESET}{desc}")
            action_list = sorted([action for action, _ in actions])
            print(f"  actions: {COLOR_CYAN}{', '.join(action_list)}{COLOR_RESET}")

        # Add usage note
        print(f"\nTo run a tool action, use: make <tool>-<action>")
        print(f"{COLOR_YELLOW}Example: make ark-cli-install{COLOR_RESET}")
    
    # Add parallel jobs note
    print(f"\nRun targets in parallel with -j flag:")
    print(f"{COLOR_YELLOW}Example: make -j4 build-all{COLOR_RESET}")


def generate_help_makefile(main_targets, lib_groups, service_groups, tool_groups):
    """Generate a makefile fragment for the help target"""
    # Start with header
    output = ["# Auto-generated help makefile - DO NOT EDIT MANUALLY"]
    output.append("# Generated by scripts/show-help.py")
    output.append("")
    output.append(".PHONY: help")
    output.append("help:")
    
    # Helper function to get a service/lib description
    def get_description(actions):
        # Try to get description from build or install action
        for action, desc in actions:
            if action in ['build', 'install']:
                # Extract the main part of the description
                if 'Docker image' in desc:
                    return desc.split('Docker image')[0].strip()
                elif 'to cluster' in desc:
                    return desc.split('to cluster')[0].strip()
                else:
                    return desc
        # Fallback to first action's description
        return actions[0][1] if actions else ""
    
    # Main targets
    if main_targets:
        output.append('\t@echo "=== Main Targets ==="')
        for target in sorted(main_targets.keys()):
            escaped_desc = main_targets[target].replace('"', '\\"')
            output.append(f'\t@printf "$(COLOR_GREEN)%-30s$(COLOR_RESET)%s\\n" "{target}" "{escaped_desc}"')
    
    # Library targets
    if lib_groups:
        output.append('\t@echo ""')
        output.append('\t@echo "=== Libraries ==="')
        for lib_name in sorted(lib_groups.keys()):
            actions = lib_groups[lib_name]
            desc = get_description(actions)
            escaped_desc = desc.replace('"', '\\"')
            output.append(f'\t@printf "$(COLOR_GREEN)%-30s$(COLOR_RESET)%s\\n" "{lib_name}" "{escaped_desc}"')
            action_list = sorted([action for action, _ in actions])
            output.append(f'\t@printf "  actions: $(COLOR_CYAN)%s$(COLOR_RESET)\\n" "{", ".join(action_list)}"')
    
    # Service targets
    if service_groups:
        output.append('\t@echo ""')
        output.append('\t@echo "=== Services ==="')
        for service_name in sorted(service_groups.keys()):
            actions = service_groups[service_name]
            desc = get_description(actions)
            escaped_desc = desc.replace('"', '\\"')
            output.append(f'\t@printf "$(COLOR_GREEN)%-30s$(COLOR_RESET)%s\\n" "{service_name}" "{escaped_desc}"')
            action_list = sorted([action for action, _ in actions])
            output.append(f'\t@printf "  actions: $(COLOR_CYAN)%s$(COLOR_RESET)\\n" "{", ".join(action_list)}"')
        
        # Add usage note
        output.append('\t@echo ""')
        output.append('\t@echo "To run a service action, use: make <service>-<action>"')
        output.append(f'\t@printf "$(COLOR_YELLOW)Example: make ark-dashboard-install$(COLOR_RESET)\\n"')
    
    # Tool targets
    if tool_groups:
        output.append('\t@echo ""')
        output.append('\t@echo "=== Tools ==="')
        for tool_name in sorted(tool_groups.keys()):
            actions = tool_groups[tool_name]
            desc = get_description(actions)
            escaped_desc = desc.replace('"', '\\"')
            output.append(f'\t@printf "$(COLOR_GREEN)%-30s$(COLOR_RESET)%s\\n" "{tool_name}" "{escaped_desc}"')
            action_list = sorted([action for action, _ in actions])
            output.append(f'\t@printf "  actions: $(COLOR_CYAN)%s$(COLOR_RESET)\\n" "{", ".join(action_list)}"')
        
        # Add usage note
        output.append('\t@echo ""')
        output.append('\t@echo "To run a tool action, use: make <tool>-<action>"')
        output.append(f'\t@printf "$(COLOR_YELLOW)Example: make ark-cli-install$(COLOR_RESET)\\n"')
    
    # Add parallel jobs note
    output.append('\t@echo ""')
    output.append('\t@echo "Run targets in parallel with -j flag:"')
    output.append(f'\t@printf "$(COLOR_YELLOW)Example: make -j4 build-all$(COLOR_RESET)\\n"')
    
    return '\n'.join(output)


def main():
    # Get list of makefiles
    makefiles = ['Makefile']

    # Find all .mk files
    for mk_file in Path('.').rglob('*.mk'):
        makefiles.append(str(mk_file))

    # Get all targets and help text
    targets = get_all_targets()
    help_map = find_help_text(makefiles)
    matched = match_targets_to_help(targets, help_map)

    # Separate targets into categories and group services
    main_targets = {}
    lib_groups = defaultdict(list)  # Group libraries by name
    service_groups = defaultdict(list)  # Group services by name
    tool_groups = defaultdict(list)  # Group tools by name

    # Known action suffixes
    known_actions = ['build', 'install', 'uninstall', 'test', 'dev', 'deps', 'dev-deps']

    for target, value in matched.items():
        # Extract help text and makefile from the value
        if isinstance(value, tuple):
            help_text, makefile = value
        else:
            # Fallback for any direct string values
            help_text = value
            makefile = ''

        # Categorize based on makefile path
        if makefile.endswith('/build.mk'):
            if 'lib/' in makefile:
                # Library target - try to group by library name
                parts = target.split('-')
                if len(parts) >= 2 and parts[-1] in known_actions:
                    lib_name = '-'.join(parts[:-1])
                    action = parts[-1]
                    lib_groups[lib_name].append((action, help_text))
                else:
                    # Standalone library target
                    main_targets[target] = help_text
            elif 'services/' in makefile:
                # Service target - try to group by service name
                parts = target.split('-')
                if len(parts) >= 2 and parts[-1] in known_actions:
                    service_name = '-'.join(parts[:-1])
                    action = parts[-1]
                    service_groups[service_name].append((action, help_text))
                else:
                    # Standalone service target
                    main_targets[target] = help_text
            elif 'tools/' in makefile:
                # Tool target - try to group by tool name
                parts = target.split('-')
                if len(parts) >= 2 and parts[-1] in known_actions:
                    tool_name = '-'.join(parts[:-1])
                    action = parts[-1]
                    tool_groups[tool_name].append((action, help_text))
                else:
                    # Standalone tool target
                    main_targets[target] = help_text
            else:
                main_targets[target] = help_text
        else:
            # Everything else (Makefile, lib/lib.mk, services/services.mk) is main
            main_targets[target] = help_text

    # Check for command line argument to output makefile fragment
    if len(sys.argv) > 1 and sys.argv[1] == '--makefile':
        print(generate_help_makefile(main_targets, lib_groups, service_groups, tool_groups))
    else:
        print_help_output(main_targets, lib_groups, service_groups, tool_groups)


if __name__ == '__main__':
    main()
