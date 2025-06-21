import os

IGNORED_FOLDERS = {'.git', '.venv', '__pycache__', '.idea', '.mypy_cache'}

def write_tree(dir_path, file, indent=""):
    for item in sorted(os.listdir(dir_path)):
        if item in IGNORED_FOLDERS:
            continue
        path = os.path.join(dir_path, item)
        if os.path.isdir(path):
            file.write(f"{indent}{item}/\n")
            write_tree(path, file, indent + "    ")
        else:
            file.write(f"{indent}{item}\n")

def generate_structure(output_file="structure.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Structure du projet :\n\n")
        write_tree(".", f)

if __name__ == "__main__":
    generate_structure()
