import os

from src.config import get_path_prefix, set_path_prefix, list_configs, load_config, save_config
from src.constants import PRESET_EXTENSIONS
from src.merge import ensure_kslist_dir, merge_files_from_list, process_subfolders, merge_files_from_directory
from src.utils import normalize_path


def read_file_list_from_file(list_file_path):
    try:
        with open(list_file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Erro ao ler arquivo de lista: {e}")
        return []


def extract_directory_levels(file_list):
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
    print("4 - Configurar prefixo de path")
    operation_mode = input("Escolha (1, 2, 3 ou 4) [padrão: 1]: ").strip()

    if not operation_mode:
        operation_mode = '1'
        print("✅ Usando padrão: Configurar e executar manualmente")

    if operation_mode == '4':
        configure_path_prefix()
        print("✅ Processo concluído.")
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
        print("✅ Processo concluído.")
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
            choice = input("Digite o número da configuração ou pressione Enter para sair: ").strip()

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
        print("✅ Processo concluído.")
        return

    print("\nComo deseja gerar os arquivos?")
    print("1 - Gerar um único arquivo para o diretório")
    print("2 - Gerar um arquivo para cada subpasta direta")
    print("3 - Gerar arquivo a partir de uma lista específica de arquivos")
    modo = input("Escolha (1, 2 ou 3) [padrão: 1]: ").strip()

    if not modo:
        modo = '1'
        print("✅ Usando padrão: Gerar um único arquivo para o diretório")

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

        ext_idx = input("Escolha (número) [padrão: 9 - Todas]: ").strip()
        try:
            if not ext_idx:
                ext_idx = len(PRESET_EXTENSIONS)
                print(f"✅ Usando padrão: Todas as extensões")
            else:
                ext_idx = int(ext_idx)

            ext_idx = ext_idx - 1
            extensions = PRESET_EXTENSIONS[ext_idx]
        except (ValueError, IndexError):
            print("❌ Opção inválida.")
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

        save_choice = input("\n💾 Deseja salvar esta configuração para uso futuro? (s/n) [padrão: n]: ").strip().lower()

        if not save_choice:
            save_choice = 'n'
            print("✅ Usando padrão: Não salvar configuração")

        if save_choice == 's':
            config_name = input("Nome para esta configuração: ").strip()
            if config_name:
                save_config(config_name, config_data)

    print("✅ Processo concluído.")
