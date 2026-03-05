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
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".merge_files_configs")
os.makedirs(CONFIG_DIR, exist_ok=True)
PATH_PREFIX_CONFIG = os.path.join(CONFIG_DIR, "path_prefix.json")
