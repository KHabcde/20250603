from transpiler import natural_to_macro
from interpreter import execute_macro
from parser_and_supplementer import macro_parse_and_supplement

def process_natural_language(file_path):
    """
    Reads natural language instructions from a file, converts them to macro syntax,
    and executes the macros.

    Args:
        file_path (str): Path to the file containing natural language instructions.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        natural_command = line.strip()
        if not natural_command:
            continue

        print(f"Processing: {natural_command}")

        # Convert natural language to macro
        macro = natural_to_macro(natural_command)
        print(f"Converted Macro: {macro}")

        # Parse and supplement the macro
        parsed_macro = macro_parse_and_supplement(macro)
        print(f"Parsed Macro: {parsed_macro}")

        # Execute the parsed macro
        execute_macro(parsed_macro)

if __name__ == "__main__":
    process_natural_language("natural_text.txt")