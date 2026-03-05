import os

from src.config import get_path_prefix
from src.constants import EXCLUDED_FILES


def normalize_path(path):
    if path.startswith(r'\\wsl.localhost') or path.startswith(r'//wsl.localhost/'):
        parts = path.replace('\\', '/').replace('//', '/').split('/')
        if len(parts) > 3:
            distro = parts[2]
            linux_path = '/' + '/'.join(parts[3:])
            return linux_path
    return path


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


def remove_path_prefix(path, prefix=None):
    """Remove o prefixo configurado do path"""
    if prefix is None:
        prefix = get_path_prefix()

    if prefix and path.startswith(prefix):
        return path[len(prefix):]
    return path
