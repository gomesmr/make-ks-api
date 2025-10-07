import os

EXTENSION_LANGUAGE_MAP = {
    '.py': 'python',
    '.java': 'java',
    '.kt': 'kotlin',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.md': 'markdown',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.html': 'html',
    '.css': 'css',
    '.sh': 'bash',
    '.c': 'c',
    '.cpp': 'cpp',
    '.cs': 'csharp',
    '.go': 'go',
    '.rb': 'ruby',
    '.php': 'php',
}

PRESET_EXTENSIONS = [
    ['.py', '.md'],
    ['.java', '.kt'],
    ['.js', '.ts'],
    ['.json', '.yaml', '.yml'],
    ['.py', '.yaml', '.yml'],
    ['.html', '.css', '.sh'],
    ['.c', '.cpp', '.cs'],
    ['.go', '.rb', '.php'],
    []  # Todas as extensões
]

def merge_files_from_directory(dir_path, output_path, ignore_dirs=None, extensions=None):
    if ignore_dirs is None:
        ignore_dirs = []
    ignore_dirs = [os.path.normpath(d) for d in ignore_dirs]
    if extensions is not None:
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]

    with open(output_path, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [
                d for d in dirs
                if os.path.relpath(os.path.join(root, d), dir_path) not in ignore_dirs
                and d not in ignore_dirs
            ]
            for file in files:
                if extensions and not any(file.endswith(ext) for ext in extensions):
                    continue
                file_path = os.path.join(root, file)
                if os.path.normpath(file_path) == os.path.normpath(output_path):
                    continue
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='latin-1') as infile:
                            content = infile.read()
                    except Exception as e:
                        print(f"Erro ao ler {file_path}: {e}")
                        continue

                ext = os.path.splitext(file)[1]
                lang = EXTENSION_LANGUAGE_MAP.get(ext, ext.lstrip('.'))
                outfile.write(f'--- {file_path} ---\n')
                outfile.write(f'```{lang}\n')
                outfile.write(content)
                outfile.write('\n```\n\n')

def process_subfolders(root_dir, ignore_dirs=None, extensions=None):
    for entry in os.scandir(root_dir):
        if entry.is_dir():
            subfolder = entry.name
            subfolder_path = os.path.join(root_dir, subfolder)
            output_path = os.path.join(root_dir, f"{subfolder}.md")
            print(f"Processando {subfolder_path} -> {output_path}")
            merge_files_from_directory(
                subfolder_path,
                output_path,
                ignore_dirs=ignore_dirs,
                extensions=extensions
            )

def menu():
    print("=== Merge de arquivos em Markdown ===")
    dir_path = input("Informe o diretório raiz: ").strip()
    if not os.path.isdir(dir_path):
        print("Diretório inválido.")
        return

    print("\nComo deseja gerar os arquivos?")
    print("1 - Gerar um único arquivo para o diretório")
    print("2 - Gerar um arquivo para cada subpasta direta")
    modo = input("Escolha (1 ou 2): ").strip()

    print("\nEscolha o conjunto de extensões para incluir:")
    for idx, preset in enumerate(PRESET_EXTENSIONS):
        if preset:
            print(f"{idx+1} - {', '.join(preset)}")
        else:
            print(f"{idx+1} - Todas as extensões")
    ext_idx = input("Escolha (número): ").strip()
    try:
        ext_idx = int(ext_idx) - 1
        extensions = PRESET_EXTENSIONS[ext_idx]
    except Exception:
        print("Opção inválida.")
        return

    ignore_dirs = ['.venv', '.git', '.idea', '__pycache__']

    if modo == '2':
        process_subfolders(
            dir_path,
            ignore_dirs=ignore_dirs,
            extensions=extensions
        )
    else:
        output_file = os.path.basename(os.path.normpath(dir_path)) + ".md"
        output_path = os.path.join(dir_path, output_file)
        merge_files_from_directory(
            dir_path,
            output_path,
            ignore_dirs=ignore_dirs,
            extensions=extensions
        )
    print("Processo concluído.")

if __name__ == '__main__':
    menu()