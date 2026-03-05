import os
from src.config import get_path_prefix
from src.constants import EXTENSION_LANGUAGE_MAP
from src.utils import should_ignore_dir, is_excluded_file, remove_path_prefix, normalize_path


def ensure_kslist_dir(parent_dir):
    kslist_dir = os.path.join(parent_dir, "_kslist")
    os.makedirs(kslist_dir, exist_ok=True)
    return kslist_dir


def merge_files_from_directory(dir_path, output_path, ignore_dirs=None, extensions=None, max_depth=0, paths_only=False):
    if ignore_dirs is None:
        ignore_dirs = []

    ignore_dirs = [os.path.normpath(d) for d in ignore_dirs]

    if extensions is not None:
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]

    base_depth = dir_path.rstrip(os.sep).count(os.sep)

    processed_files = []
    file_contents = []

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
        display_path = remove_path_prefix(dir_path, path_prefix)
        outfile.write(f"# 📁 {display_path}\n\n")
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
