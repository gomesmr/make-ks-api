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

def merge_files_from_directory(dir_path, output_path, ignore_dirs=None, extensions=None, max_depth=0):
    if ignore_dirs is None:
        ignore_dirs = []
    ignore_dirs = [os.path.normpath(d) for d in ignore_dirs]
    if extensions is not None:
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]

    base_depth = dir_path.rstrip(os.sep).count(os.sep)
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(dir_path):
            current_depth = root.rstrip(os.sep).count(os.sep) - base_depth
            if max_depth > 0 and current_depth > max_depth:
                # Remove subdirs to prevent deeper walk
                dirs[:] = []
                continue
            dirs[:] = [
                d for d in dirs
                if os.path.relpath(os.path.join(root, d), dir_path) not in ignore_dirs
                and d not in ignore_dirs
            ]
            for file in files:
                file_path = os.path.join(root, file)
                if extensions and not any(file.endswith(ext) for ext in extensions):
                    continue
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
                outfile.write(f'## 📄 {file_path}\n\n')
                outfile.write(f'```{lang}\n')
                outfile.write(content)
                outfile.write('\n```\n\n')

def merge_files_from_list(file_list, output_path, base_dir=None):
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for file_path in file_list:
            file_path = file_path.strip()
            if not file_path:
                continue

            file_path = normalize_path(file_path)

            if base_dir and not os.path.isabs(file_path):
                file_path = os.path.join(base_dir, file_path)

            if not os.path.isfile(file_path):
                print(f"Aviso: Arquivo não encontrado: {file_path}")
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

            ext = os.path.splitext(file_path)[1]
            lang = EXTENSION_LANGUAGE_MAP.get(ext, ext.lstrip('.'))
            outfile.write(f'## 📄 {file_path}\n\n')
            outfile.write(f'```{lang}\n')
            outfile.write(content)
            outfile.write('\n```\n\n')
            print(f"Adicionado: {file_path}")

def process_subfolders(root_dir, ignore_dirs=None, extensions=None, max_depth=0):
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
                extensions=extensions,
                max_depth=max_depth
            )

# \\wsl.localhost\Ubuntu_Zup\home\marcelo.gomes\stk-dev\stk-code-shift-content\actions
def normalize_path(path):
    if path.startswith(r'\\wsl.localhost') or path.startswith(r'//wsl.localhost/'):
        parts = path.replace('\\', '/').replace('//', '/').split('/')
        if len(parts) > 3:
            distro = parts[2]
            linux_path = '/' + '/'.join(parts[3:])
            return linux_path
    return path

def read_file_list_from_file(list_file_path):
    try:
        with open(list_file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Erro ao ler arquivo de lista: {e}")
        return []

def menu():
    print("=== Merge de arquivos em Markdown ===")

    print("\nComo deseja gerar os arquivos?")
    print("1 - Gerar um único arquivo para o diretório")
    print("2 - Gerar um arquivo para cada subpasta direta")
    print("3 - Gerar arquivo a partir de uma lista específica de arquivos")
    modo = input("Escolha (1, 2 ou 3): ").strip()

    if modo == '3':
        # Modo de lista de arquivos
        print("\nComo deseja fornecer a lista de arquivos?")
        print("1 - Digitar os caminhos manualmente (um por linha, linha vazia para finalizar)")
        print("2 - Ler de um arquivo de texto")
        list_mode = input("Escolha (1 ou 2): ").strip()

        file_list = []
        base_dir = None

        if list_mode == '2':
            list_file = input("Informe o caminho do arquivo com a lista: ").strip()
            list_file = normalize_path(list_file)
            file_list = read_file_list_from_file(list_file)
            if not file_list:
                print("Nenhum arquivo válido encontrado na lista.")
                return

            use_base = input("Os caminhos são relativos a algum diretório? (s/n): ").strip().lower()
            if use_base == 's':
                base_dir = input("Informe o diretório base: ").strip()
                base_dir = normalize_path(base_dir)
        else:
            print("\nDigite os caminhos dos arquivos (um por linha).")
            print("Deixe uma linha em branco para finalizar:")
            while True:
                path = input().strip()
                if not path:
                    break
                file_list.append(path)

            if not file_list:
                print("Nenhum arquivo informado.")
                return

            use_base = input("\nOs caminhos são relativos a algum diretório? (s/n): ").strip().lower()
            if use_base == 's':
                base_dir = input("Informe o diretório base: ").strip()
                base_dir = normalize_path(base_dir)

        output_path = input("\nInforme o caminho do arquivo de saída (.md): ").strip()
        output_path = normalize_path(output_path)

        if not output_path.endswith('.md'):
            output_path += '.md'

        print(f"\nProcessando {len(file_list)} arquivo(s)...")
        merge_files_from_list(file_list, output_path, base_dir)
        print(f"Arquivo gerado: {output_path}")

    else:
        dir_path = input("Informe o diretório raiz: ").strip()
        dir_path = normalize_path(dir_path)
        if not os.path.isdir(dir_path):
            print("Diretório inválido.")
            return

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

        print("\nLimite de profundidade de busca (0 = todos os níveis, 1 = apenas raiz, 2 = raiz + 1 nível, ...):")
        try:
            max_depth = int(input("Profundidade máxima: ").strip() or "0")
        except Exception:
            max_depth = 0

        ignore_dirs = ['.venv', '.git', '.idea', '__pycache__']

        if modo == '2':
            process_subfolders(
                dir_path,
                ignore_dirs=ignore_dirs,
                extensions=extensions,
                max_depth=max_depth
            )
        else:
            output_file = os.path.basename(os.path.normpath(dir_path)) + ".md"
            output_path = os.path.join(dir_path, output_file)
            merge_files_from_directory(
                dir_path,
                output_path,
                ignore_dirs=ignore_dirs,
                extensions=extensions,
                max_depth=max_depth
            )

    print("Processo concluído.")

if __name__ == '__main__':
    menu()