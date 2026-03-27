# make-ks-api

Ferramenta CLI para mesclar arquivos de código-fonte em documentos Markdown, facilitando a preparação de bases de código para análise com LLMs.

## Como usar

```bash
python main.py
```

## Modos de operação

### 1 — Configurar e executar manualmente

Permite configurar e executar uma nova mesclagem. Você escolhe:

- **Como gerar os arquivos:**
  - `1` — Um único `.md` para todo o diretório
  - `2` — Um `.md` por subpasta direta (mais `root_<nome>.md` para os arquivos da raiz)
  - `3` — A partir de uma lista específica de arquivos

- **Formato de saída:**
  - `1` — Apenas os paths dos arquivos (índice)
  - `2` — Conteúdo completo com syntax highlighting

- **Conjunto de extensões** (presets disponíveis):
 
  | # | Extensões |
  |---|-----------|
  | 1 | `.py`, `.md` |
  | 2 | `.java`, `.kt` |
  | 3 | `.js`, `.ts` |
  | 4 | `.json`, `.yaml`, `.yml` |
  | 5 | `.py`, `.yaml`, `.yml` |
  | 6 | `.html`, `.css`, `.sh` |
  | 7 | `.c`, `.cpp`, `.cs` |
  | 8 | `.go`, `.rb`, `.php` |
  | 9 | Todas as extensões |

- **Profundidade máxima:**
  - `0` — Sem limite (todos os níveis)
  - `1` — Apenas a pasta raiz
  - `2` — Raiz + 1 nível de subpastas
  - e assim por diante

Os arquivos gerados são salvos em `_kslist/` dentro do diretório processado.

### 2 — Usar configuração salva

Executa uma configuração salva anteriormente pelo nome ou número.

### 3 — Listar configurações salvas

Lista as configurações disponíveis e permite executar uma delas.

### 4 — Configurar prefixo de path

Define um prefixo a ser removido dos caminhos exibidos nos arquivos gerados.

Por exemplo, se seus projetos estão em `/home/usuario/projetos/`, configurar esse caminho como prefixo faz com que os paths no output apareçam como `meu-projeto/src/arquivo.py` em vez de `/home/usuario/projetos/meu-projeto/src/arquivo.py`.

Opções:
- Definir manualmente
- Detecção automática de diretórios comuns (`~/stk-dev`, `~/projects`, `~/workspace`, etc.)
- Remover o prefixo (exibir paths completos)

A configuração é salva em `~/.merge_files_configs/path_prefix.json` e persiste entre execuções.

### 5 — Gerenciar configurações salvas

Lista as configurações existentes e permite deletar as que não são mais necessárias.

### 0 — Sair

## Arquivos excluídos automaticamente

Os seguintes arquivos nunca são incluídos no output, independente da configuração:

`secrets.json`, `.env`, `.env.local`, `credentials.json`, `config.secret.json`

## Configurações salvas

As configurações são armazenadas como JSON em `~/.merge_files_configs/`. Cada configuração salva contém o diretório, extensões, profundidade, modo de geração e formato de saída, permitindo reexecutar a mesclagem sem reconfigurar.
