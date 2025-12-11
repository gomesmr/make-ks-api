import json
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

EXCLUDED_FILES = [
    'secrets.json', '.env', '.env.local', 'credentials.json', 'config.secret.json', '_kslist.md'
]


def ensure_kslist_dir(parent_dir):
    kslist_dir = os.path.join(parent_dir, "_kslist")
    os.makedirs(kslist_dir, exist_ok=True)
    return kslist_dir


def is_excluded_file(file_path):
    filename = os.path.basename(file_path)
    return filename in EXCLUDED_FILES


def should_ignore_dir(dir_path, ignore_dirs):
    """
    Verifica se um diretório deve ser ignorado.
    Compara tanto o nome do diretório quanto o caminho completo.
    """
    dir_name = os.path.basename(dir_path)
    normalized_path = os.path.normpath(dir_path)

    for ignore_pattern in ignore_dirs:
        ignore_pattern = os.path.normpath(ignore_pattern)

        # Verifica se é o nome do diretório
        if dir_name == ignore_pattern or dir_name == os.path.basename(ignore_pattern):
            return True

        # Verifica se o caminho completo contém o padrão
        if ignore_pattern in normalized_path:
            return True

        # Verifica se termina com o padrão (para caminhos relativos)
        if normalized_path.endswith(ignore_pattern):
            return True

    return False


def merge_files_from_directory(dir_path, output_path, ignore_dirs=None, extensions=None, max_depth=0, paths_only=False):
    if ignore_dirs is None:
        ignore_dirs = []

    # Normaliza os diretórios a ignorar
    ignore_dirs = [os.path.normpath(d) for d in ignore_dirs]

    if extensions is not None:
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]

    base_depth = dir_path.rstrip(os.sep).count(os.sep)

    with open(output_path, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(dir_path):
            current_depth = root.rstrip(os.sep).count(os.sep) - base_depth

            # Verifica profundidade máxima
            if 0 < max_depth < current_depth:
                dirs[:] = []
                continue

            # CORREÇÃO: Filtra diretórios usando a nova função
            dirs_to_remove = []
            for d in dirs:
                full_dir_path = os.path.join(root, d)
                if should_ignore_dir(full_dir_path, ignore_dirs):
                    dirs_to_remove.append(d)
                    print(f"🚫 Diretório ignorado: {full_dir_path}")

            # Remove os diretórios ignorados da lista
            for d in dirs_to_remove:
                dirs.remove(d)

            for file in files:
                file_path = os.path.join(root, file)

                if is_excluded_file(file_path):
                    print(f"🔒 Arquivo excluído (sensível): {file_path}")
                    continue

                if extensions and not any(file.endswith(ext) for ext in extensions):
                    continue

                if os.path.normpath(file_path) == os.path.normpath(output_path):
                    continue

                if paths_only:
                    outfile.write(f'{file_path}\n')
                else:
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
                    write_file(content, file, file_path, outfile)


def write_file(content, file, file_path, outfile):
    ext = os.path.splitext(file)[1]
    lang = EXTENSION_LANGUAGE_MAP.get(ext, ext.lstrip('.'))
    outfile.write(f'## 📄 {file_path}\n\n')
    outfile.write(f'```{lang}\n')
    outfile.write(content)
    outfile.write('\n```\n\n')


def merge_files_from_list(file_list, output_path, base_dir=None, paths_only=False):
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for file_path in file_list:
            file_path = file_path.strip()
            if not file_path:
                continue
            file_path = normalize_path(file_path)
            if base_dir and not os.path.isabs(file_path):
                file_path = os.path.join(base_dir, file_path)
            if is_excluded_file(file_path):
                print(f"🔒 Arquivo excluído (sensível): {file_path}")
                continue
            if not os.path.isfile(file_path):
                print(f"⚠️ Aviso: Arquivo não encontrado: {file_path}")
                continue
            if paths_only:
                outfile.write(f'{file_path}\n')
                print(f"✅ Path adicionado: {file_path}")
            else:
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='latin-1') as infile:
                            content = infile.read()
                    except Exception as e:
                        print(f"❌ Erro ao ler {file_path}: {e}")
                        continue
                ext = os.path.splitext(file_path)[1]
                lang = EXTENSION_LANGUAGE_MAP.get(ext, ext.lstrip('.'))
                outfile.write(f'## 📄 {file_path}\n\n')
                outfile.write(f'```{lang}\n')
                outfile.write(content)
                outfile.write('\n```\n\n')
                print(f"✅ Conteúdo adicionado: {file_path}")


def process_subfolders(root_dir, ignore_dirs=None, extensions=None, max_depth=0, paths_only=False):
    kslist_dir = ensure_kslist_dir(root_dir)
    if ignore_dirs is None:
        ignore_dirs = []

    for entry in os.scandir(root_dir):
        if entry.is_dir():
            # CORREÇÃO: Verifica se a pasta deve ser ignorada
            if should_ignore_dir(entry.path, ignore_dirs):
                print(f"🚫 Subpasta ignorada: {entry.path}")
                continue

            subfolder = entry.name
            subfolder_path = os.path.join(root_dir, subfolder)
            output_path = os.path.join(kslist_dir, f"{subfolder}.md")
            print(f"Processando {subfolder_path} -> {output_path}")
            merge_files_from_directory(
                subfolder_path,
                output_path,
                ignore_dirs=ignore_dirs,
                extensions=extensions,
                max_depth=max_depth,
                paths_only=paths_only
            )


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


CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".merge_files_configs")
os.makedirs(CONFIG_DIR, exist_ok=True)


def save_config(config_name, config_data):
    config_path = os.path.join(CONFIG_DIR, f"{config_name}.json")
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
        print(f"✅ Configuração '{config_name}' salva com sucesso!")
        print(f"📁 Local: {config_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar configuração: {e}")
        return False


def load_config(config_name):
    config_path = os.path.join(CONFIG_DIR, f"{config_name}.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Configuração '{config_name}' não encontrada.")
        return None
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        return None


def list_configs():
    configs = [f.replace('.json', '') for f in os.listdir(CONFIG_DIR) if f.endswith('.json')]
    return configs


def execute_from_config(config_data):
    modo = config_data.get('modo')
    paths_only = config_data.get('paths_only', False)
    if modo == '3':
        file_list = config_data.get('file_list', [])
        base_dir = config_data.get('base_dir')
        output_path = config_data.get('output_path')
        # Garante que está na pasta _kslist
        kslist_dir = ensure_kslist_dir(os.path.dirname(output_path))
        output_filename = os.path.basename(output_path)
        output_path = os.path.join(kslist_dir, output_filename)
        merge_files_from_list(file_list, output_path, base_dir, paths_only=paths_only)
        print(f"✅ Arquivo gerado: {output_path}")
    else:
        dir_path = config_data.get('dir_path')
        extensions = config_data.get('extensions')
        max_depth = config_data.get('max_depth', 0)
        ignore_dirs = config_data.get('ignore_dirs', ['.venv', '.git', '.idea', '__pycache__'])
        if modo == '2':
            process_subfolders(
                dir_path,
                ignore_dirs=ignore_dirs,
                extensions=extensions,
                max_depth=max_depth,
                paths_only=paths_only
            )
        else:
            kslist_dir = ensure_kslist_dir(dir_path)
            output_file = os.path.basename(os.path.normpath(dir_path)) + ".md"
            output_path = os.path.join(kslist_dir, output_file)
            merge_files_from_directory(
                dir_path,
                output_path,
                ignore_dirs=ignore_dirs,
                extensions=extensions,
                max_depth=max_depth,
                paths_only=paths_only
            )
        print("✅ Processo concluído.")


def menu():
    print("=== Merge de arquivos em Markdown ===")
    print("\n🎯 Modo de operação:")
    print("1 - Configurar e executar manualmente")
    print("2 - Usar configuração salva")
    print("3 - Listar configurações salvas")
    operation_mode = input("Escolha (1, 2 ou 3): ").strip()

    if operation_mode == '2':
        configs = list_configs()
        if not configs:
            print("❌ Nenhuma configuração salva encontrada.")
            return
        print("\n📋 Configurações disponíveis:")
        for idx, config in enumerate(configs, 1):
            print(f"{idx} - {config}")
        choice = input("\nEscolha uma configuração (número ou nome): ").strip()
        try:
            if choice.isdigit():
                config_name = configs[int(choice) - 1]
            else:
                config_name = choice
        except (IndexError, ValueError):
            print("❌ Opção inválida.")
            return
        config_data = load_config(config_name)
        if config_data:
            print(f"\n🚀 Executando configuração '{config_name}'...")
            execute_from_config(config_data)
        return

    elif operation_mode == '3':
        configs = list_configs()
        if not configs:
            print("❌ Nenhuma configuração salva encontrada.")
        else:
            print("\n📋 Configurações salvas:")
            for config in configs:
                print(f" • {config}")
        return

    print("\nComo deseja gerar os arquivos?")
    print("1 - Gerar um único arquivo para o diretório")
    print("2 - Gerar um arquivo para cada subpasta direta")
    print("3 - Gerar arquivo a partir de uma lista específica de arquivos")
    modo = input("Escolha (1, 2 ou 3): ").strip()

    print("\nQual formato de saída deseja?")
    print("1 - Apenas paths dos arquivos")
    print("2 - Conteúdo completo dos arquivos (formato atual)")
    output_format = input("Escolha (1 ou 2): ").strip()
    paths_only = (output_format == '1')

    config_data = {
        'modo': modo,
        'paths_only': paths_only
    }

    if modo == '3':
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

        output_filename = input("\nInforme o nome do arquivo de saída (.md): ").strip()
        if not output_filename.endswith('.md'):
            output_filename += '.md'

        base_output_dir = input(
            "Informe o diretório onde salvar (deixe em branco para usar o diretório atual): ").strip()
        if not base_output_dir:
            base_output_dir = os.getcwd()
        base_output_dir = normalize_path(base_output_dir)

        kslist_dir = ensure_kslist_dir(base_output_dir)
        output_path = os.path.join(kslist_dir, output_filename)

        config_data.update({
            'file_list': file_list,
            'base_dir': base_dir,
            'output_path': output_path
        })

        print(f"\nProcessando {len(file_list)} arquivo(s)...")
        merge_files_from_list(file_list, output_path, base_dir, paths_only=paths_only)
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
                print(f"{idx + 1} - {', '.join(preset)}")
            else:
                print(f"{idx + 1} - Todas as extensões")

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

        ignore_dirs = ['.venv', '.git', '.idea', '__pycache__', 'assets', 'docs', '_kslist']

        config_data.update({
            'dir_path': dir_path,
            'extensions': extensions,
            'max_depth': max_depth,
            'ignore_dirs': ignore_dirs
        })

        kslist_dir = ensure_kslist_dir(dir_path)

        if modo == '2':
            process_subfolders(
                dir_path,
                ignore_dirs=ignore_dirs,
                extensions=extensions,
                max_depth=max_depth,
                paths_only=paths_only
            )
        else:
            output_file = os.path.basename(os.path.normpath(dir_path)) + ".md"
            output_path = os.path.join(kslist_dir, output_file)

            merge_files_from_directory(
                dir_path,
                output_path,
                ignore_dirs=ignore_dirs,
                extensions=extensions,
                max_depth=max_depth,
                paths_only=paths_only
            )

        # Perguntar se deseja salvar a configuração
        save_choice = input("\n💾 Deseja salvar esta configuração para uso futuro? (s/n): ").strip().lower()
        if save_choice == 's':
            config_name = input("Nome para esta configuração: ").strip()
            if config_name:
                save_config(config_name, config_data)

    print("Processo concluído.")


if __name__ == '__main__':
    menu()