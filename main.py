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
    []
]

EXCLUDED_FILES = [
    'secrets.json', '.env', '.env.local', 'credentials.json', 'config.secret.json', '_kslist.md'
]

# ✅ NOVO: Configuração de prefixo de path a ser removido
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".merge_files_configs")
os.makedirs(CONFIG_DIR, exist_ok=True)
PATH_PREFIX_CONFIG = os.path.join(CONFIG_DIR, "path_prefix.json")


def get_path_prefix():
    """Obtém o prefixo de path configurado ou detecta automaticamente"""
    try:
        with open(PATH_PREFIX_CONFIG, 'r') as f:
            config = json.load(f)
            return config.get('prefix', '')
    except (FileNotFoundError, json.JSONDecodeError):
        # Tenta detectar automaticamente baseado no home do usuário
        home = os.path.expanduser("~")
        # Procura por padrões comuns como ~/stk-dev/, ~/projects/, etc.
        common_patterns = ['stk-dev', 'projects', 'workspace', 'dev', 'code']
        for pattern in common_patterns:
            potential_prefix = os.path.join(home, pattern)
            if os.path.isdir(potential_prefix):
                return potential_prefix + os.sep
        return ''


def set_path_prefix(prefix):
    """Define o prefixo de path a ser removido"""
    with open(PATH_PREFIX_CONFIG, 'w') as f:
        json.dump({'prefix': prefix}, f, indent=2)
    print(f"✅ Prefixo de path configurado: {prefix}")


def remove_path_prefix(path, prefix=None):
    """Remove o prefixo configurado do path"""
    if prefix is None:
        prefix = get_path_prefix()

    if prefix and path.startswith(prefix):
        return path[len(prefix):]
    return path


def ensure_kslist_dir(parent_dir):
    kslist_dir = os.path.join(parent_dir, "_kslist")
    os.makedirs(kslist_dir, exist_ok=True)
    return kslist_dir


def is_excluded_file(file_path):
    filename = os.path.basename(file_path)
    return filename in EXCLUDED_FILES


def should_ignore_dir(dir_path, ignore_dirs):
    dir_name = os.path.basename(dir_path)
    normalized_path = os.path.normpath(dir_path)

    for ignore_pattern in ignore_dirs:
        ignore_pattern = os.path.normpath(ignore_pattern)

        if dir_name == ignore_pattern or dir_name == os.path.basename(ignore_pattern):
            return True

        if ignore_pattern in normalized_path:
            return True

        if normalized_path.endswith(ignore_pattern):
            return True

    return False


def merge_files_from_directory(dir_path, output_path, ignore_dirs=None, extensions=None, max_depth=0, paths_only=False):
    if ignore_dirs is None:
        ignore_dirs = []

    ignore_dirs = [os.path.normpath(d) for d in ignore_dirs]

    if extensions is not None:
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]

    base_depth = dir_path.rstrip(os.sep).count(os.sep)

    processed_files = []
    file_contents = []

    # ✅ Obtém o prefixo configurado
    path_prefix = get_path_prefix()

    for root, dirs, files in os.walk(dir_path):
        current_depth = root.rstrip(os.sep).count(os.sep) - base_depth

        dirs_to_remove = []
        for d in dirs:
            full_dir_path = os.path.join(root, d)
            if should_ignore_dir(full_dir_path, ignore_dirs):
                dirs_to_remove.append(d)
                print(f"🚫 Diretório ignorado: {full_dir_path}")

        for d in dirs_to_remove:
            dirs.remove(d)

        if 0 < max_depth <= current_depth:
            dirs[:] = []

        for file in files:
            file_path = os.path.join(root, file)

            if is_excluded_file(file_path):
                print(f"🔒 Arquivo excluído (sensível): {file_path}")
                continue

            if extensions and not any(file.endswith(ext) for ext in extensions):
                continue

            if os.path.normpath(file_path) == os.path.normpath(output_path):
                continue

            processed_files.append(file_path)

            if not paths_only:
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
                file_contents.append({
                    'path': file_path,
                    'content': content,
                    'lang': lang
                })

    with open(output_path, 'w', encoding='utf-8') as outfile:
        # ✅ Remove o prefixo do path no cabeçalho
        display_path = remove_path_prefix(dir_path, path_prefix)
        outfile.write(f"# 📁 {display_path}\n\n")
        outfile.write("# 📋 Índice de Arquivos\n\n")
        outfile.write(f"**Total de arquivos processados:** {len(processed_files)}\n\n")

        for idx, file_path in enumerate(processed_files, 1):
            # ✅ Remove o prefixo de cada path
            display_file_path = remove_path_prefix(file_path, path_prefix)
            outfile.write(f"{idx}. `{display_file_path}`\n")

        outfile.write("\n---\n\n")
        outfile.write("# 📦 Conteúdo dos Arquivos\n\n")

        if paths_only:
            for file_path in processed_files:
                display_file_path = remove_path_prefix(file_path, path_prefix)
                outfile.write(f'{display_file_path}\n')
        else:
            for file_data in file_contents:
                display_file_path = remove_path_prefix(file_data['path'], path_prefix)
                outfile.write(f'## 📄 {display_file_path}\n\n')
                outfile.write(f'```{file_data["lang"]}\n')
                outfile.write(file_data['content'])
                outfile.write('\n```\n\n')


def merge_files_from_list(file_list, output_path, base_dir=None, paths_only=False):
    processed_files = []
    file_contents = []
    path_prefix = get_path_prefix()

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

        processed_files.append(file_path)

        if not paths_only:
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
            file_contents.append({
                'path': file_path,
                'content': content,
                'lang': lang
            })
            print(f"✅ Conteúdo coletado: {file_path}")

    with open(output_path, 'w', encoding='utf-8') as outfile:
        outfile.write("# 📋 Índice de Arquivos\n\n")
        outfile.write(f"**Total de arquivos processados:** {len(processed_files)}\n\n")

        for idx, file_path in enumerate(processed_files, 1):
            display_file_path = remove_path_prefix(file_path, path_prefix)
            outfile.write(f"{idx}. `{display_file_path}`\n")

        outfile.write("\n---\n\n")
        outfile.write("# 📦 Conteúdo dos Arquivos\n\n")

        if paths_only:
            for file_path in processed_files:
                display_file_path = remove_path_prefix(file_path, path_prefix)
                outfile.write(f'{display_file_path}\n')
                print(f"✅ Path adicionado: {display_file_path}")
        else:
            for file_data in file_contents:
                display_file_path = remove_path_prefix(file_data['path'], path_prefix)
                outfile.write(f'## 📄 {display_file_path}\n\n')
                outfile.write(f'```{file_data["lang"]}\n')
                outfile.write(file_data['content'])
                outfile.write('\n```\n\n')
                print(f"✅ Conteúdo adicionado: {display_file_path}")


def process_root_files(root_dir, kslist_dir, ignore_dirs=None, extensions=None, paths_only=False):
    """
    Processa apenas os arquivos que estão diretamente na raiz do diretório,
    gerando um arquivo root_[nome-do-diretorio].md
    """
    if ignore_dirs is None:
        ignore_dirs = []

    if extensions is not None:
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]

    processed_files = []
    file_contents = []
    path_prefix = get_path_prefix()

    try:
        entries = os.listdir(root_dir)
    except Exception as e:
        print(f"❌ Erro ao listar diretório {root_dir}: {e}")
        return

    for entry in entries:
        entry_path = os.path.join(root_dir, entry)

        if os.path.isdir(entry_path):
            continue

        if is_excluded_file(entry_path):
            print(f"🔒 Arquivo excluído (sensível): {entry_path}")
            continue

        if extensions and not any(entry.endswith(ext) for ext in extensions):
            continue

        processed_files.append(entry_path)

        if not paths_only:
            try:
                with open(entry_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
            except UnicodeDecodeError:
                try:
                    with open(entry_path, 'r', encoding='latin-1') as infile:
                        content = infile.read()
                except Exception as e:
                    print(f"❌ Erro ao ler {entry_path}: {e}")
                    continue

            ext = os.path.splitext(entry)[1]
            lang = EXTENSION_LANGUAGE_MAP.get(ext, ext.lstrip('.'))
            file_contents.append({
                'path': entry_path,
                'content': content,
                'lang': lang
            })

    if len(processed_files) == 1 and os.path.basename(processed_files[0]) == '__init__.py':
        print("ℹ️ Apenas __init__.py encontrado na raiz. Arquivo root não será gerado.")
        return

    if not processed_files:
        print("ℹ️ Nenhum arquivo encontrado na raiz do diretório.")
        return

    dir_name = os.path.basename(os.path.normpath(root_dir))
    output_path = os.path.join(kslist_dir, f"root_{dir_name}.md")

    with open(output_path, 'w', encoding='utf-8') as outfile:
        display_path = remove_path_prefix(root_dir, path_prefix)
        outfile.write(f"# 📁 {display_path}\n\n")
        outfile.write("# 📋 Índice de Arquivos da Raiz\n\n")
        outfile.write(f"**Total de arquivos processados:** {len(processed_files)}\n\n")

        for idx, file_path in enumerate(processed_files, 1):
            display_file_path = remove_path_prefix(file_path, path_prefix)
            outfile.write(f"{idx}. `{display_file_path}`\n")

        outfile.write("\n---\n\n")
        outfile.write("# 📦 Conteúdo dos Arquivos\n\n")

        if paths_only:
            for file_path in processed_files:
                display_file_path = remove_path_prefix(file_path, path_prefix)
                outfile.write(f'{display_file_path}\n')
        else:
            for file_data in file_contents:
                display_file_path = remove_path_prefix(file_data['path'], path_prefix)
                outfile.write(f'## 📄 {display_file_path}\n\n')
                outfile.write(f'```{file_data["lang"]}\n')
                outfile.write(file_data['content'])
                outfile.write('\n```\n\n')

    print(f"✅ Arquivo root_{dir_name}.md gerado: {output_path}")


def process_subfolders(root_dir, ignore_dirs=None, extensions=None, max_depth=0, paths_only=False):
    kslist_dir = ensure_kslist_dir(root_dir)
    if ignore_dirs is None:
        ignore_dirs = []

    print(f"\n📁 Processando arquivos da raiz de {root_dir}...")
    process_root_files(root_dir, kslist_dir, ignore_dirs, extensions, paths_only)

    print(f"\n📁 Processando subpastas de {root_dir}...")
    for entry in os.scandir(root_dir):
        if entry.is_dir():
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


def extract_directory_levels(file_list):
    """
    Extrai os níveis de diretório únicos de uma lista de arquivos.
    Retorna uma lista de diretórios ordenados por profundidade.
    """
    directories = set()

    for file_path in file_list:
        file_path = normalize_path(file_path.strip())
        if not file_path:
            continue

        dir_path = os.path.dirname(file_path)

        parts = dir_path.split(os.sep)
        for i in range(1, len(parts) + 1):
            level_path = os.sep.join(parts[:i])
            if level_path:
                directories.add(level_path)

    sorted_dirs = sorted(directories, key=lambda x: x.count(os.sep))

    return sorted_dirs


def select_output_directory(file_list):
    """
    Permite ao usuário selecionar o diretório de saída a partir dos níveis
    de profundidade dos arquivos da lista.
    """
    dir_levels = extract_directory_levels(file_list)

    if not dir_levels:
        print("⚠️ Não foi possível extrair diretórios da lista de arquivos.")
        return os.getcwd()

    print("\n📁 Selecione o diretório onde salvar o arquivo:")
    for idx, dir_path in enumerate(dir_levels, 1):
        print(f"{idx} - {dir_path}")

    print(f"{len(dir_levels) + 1} - Outro diretório (digitar manualmente)")

    while True:
        try:
            choice = input("\nEscolha uma opção: ").strip()
            choice_num = int(choice)

            if 1 <= choice_num <= len(dir_levels):
                selected_dir = dir_levels[choice_num - 1]
                print(f"✅ Diretório selecionado: {selected_dir}")
                return selected_dir
            elif choice_num == len(dir_levels) + 1:
                custom_dir = input("Informe o diretório: ").strip()
                custom_dir = normalize_path(custom_dir)
                if os.path.isdir(custom_dir):
                    print(f"✅ Diretório selecionado: {custom_dir}")
                    return custom_dir
                else:
                    print("❌ Diretório inválido. Tente novamente.")
            else:
                print("❌ Opção inválida. Tente novamente.")
        except ValueError:
            print("❌ Por favor, digite um número válido.")
        except KeyboardInterrupt:
            print("\n\n❌ Operação cancelada.")
            return None


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
    configs = [f.replace('.json', '') for f in os.listdir(CONFIG_DIR) if
               f.endswith('.json') and f != 'path_prefix.json']
    return configs


def execute_from_config(config_data):
    modo = config_data.get('modo')
    paths_only = config_data.get('paths_only', False)
    if modo == '3':
        file_list = config_data.get('file_list', [])
        base_dir = config_data.get('base_dir')
        output_path = config_data.get('output_path')
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


def configure_path_prefix():
    """Menu para configurar o prefixo de path"""
    current_prefix = get_path_prefix()

    print("\n⚙️ Configuração de Prefixo de Path")
    print("=" * 50)

    if current_prefix:
        print(f"📍 Prefixo atual: {current_prefix}")
    else:
        print("📍 Nenhum prefixo configurado")

    print("\nOpções:")
    print("1 - Definir novo prefixo")
    print("2 - Usar detecção automática")
    print("3 - Remover prefixo (mostrar paths completos)")
    print("4 - Voltar")

    choice = input("\nEscolha uma opção: ").strip()

    if choice == '1':
        new_prefix = input("\nInforme o prefixo a ser removido dos paths (ex: /home/marcelo.gomes/stk-dev/): ").strip()
        if new_prefix and not new_prefix.endswith(os.sep):
            new_prefix += os.sep
        set_path_prefix(new_prefix)
    elif choice == '2':
        home = os.path.expanduser("~")
        print(f"\n🔍 Detectando diretórios comuns em {home}...")
        common_patterns = ['stk-dev', 'projects', 'workspace', 'dev', 'code', 'work']
        found = []
        for pattern in common_patterns:
            potential_prefix = os.path.join(home, pattern)
            if os.path.isdir(potential_prefix):
                found.append(potential_prefix)

        if found:
            print("\n📁 Diretórios encontrados:")
            for idx, path in enumerate(found, 1):
                print(f"{idx} - {path}")

            try:
                sel = int(input("\nEscolha um diretório (número): ").strip())
                if 1 <= sel <= len(found):
                    selected = found[sel - 1] + os.sep
                    set_path_prefix(selected)
                else:
                    print("❌ Opção inválida.")
            except ValueError:
                print("❌ Por favor, digite um número válido.")
        else:
            print("❌ Nenhum diretório comum encontrado.")
    elif choice == '3':
        set_path_prefix('')
        print("✅ Prefixo removido. Paths completos serão exibidos.")


def menu():
    print("=== Merge de arquivos em Markdown ===")
    print("\n🎯 Modo de operação:")
    print("1 - Configurar e executar manualmente")
    print("2 - Usar configuração salva")
    print("3 - Listar configurações salvas")
    print("4 - Configurar prefixo de path")  # ✅ NOVA OPÇÃO
    operation_mode = input("Escolha (1, 2, 3 ou 4): ").strip()

    if operation_mode == '4':
        configure_path_prefix()
        return

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
            for idx, config in enumerate(configs, 1):
                print(f"{idx} - {config}")

            print("\n💡 Deseja executar alguma configuração?")
            choice = input("Digite o número da configuração ou pressione Enter para voltar: ").strip()

            if choice:
                try:
                    if choice.isdigit():
                        config_idx = int(choice) - 1
                        if 0 <= config_idx < len(configs):
                            config_name = configs[config_idx]
                            config_data = load_config(config_name)
                            if config_data:
                                print(f"\n🚀 Executando configuração '{config_name}'...")
                                execute_from_config(config_data)
                        else:
                            print("❌ Número inválido.")
                    else:
                        print("❌ Por favor, digite um número válido.")
                except (IndexError, ValueError):
                    print("❌ Opção inválida.")
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

        base_output_dir = select_output_directory(file_list)

        if base_output_dir is None:
            return

        kslist_dir = ensure_kslist_dir(base_output_dir)
        output_path = os.path.join(kslist_dir, output_filename)

        config_data.update({
            'file_list': file_list,
            'base_dir': base_dir,
            'output_path': output_path
        })

        print(f"\nProcessando {len(file_list)} arquivo(s)...")
        merge_files_from_list(file_list, output_path, base_dir, paths_only=paths_only)
        print(f"✅ Arquivo gerado: {output_path}")

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

        ignore_dirs = ['.venv', '.git', '.idea', '__pycache__', 'assets', '_kslist']

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

        save_choice = input("\n💾 Deseja salvar esta configuração para uso futuro? (s/n): ").strip().lower()
        if save_choice == 's':
            config_name = input("Nome para esta configuração: ").strip()
            if config_name:
                save_config(config_name, config_data)

    print("✅ Processo concluído.")


if __name__ == '__main__':
    menu()