# Installazione guidata e upgrade

## Setup

```bash
python3 tools/install_manager.py install
```

L'installer verifica Python e rileva Git/Codex/Claude, propone `~/.local/share/aiflow` e chiede conferma prima di installare. Usa GitHub Releases del repository `alegiac/aiflow` e verifica il file SHA256.

```bash
export PATH="$HOME/.local/share/aiflow/bin:$PATH"
aiflow --help
```

## Upgrade

```bash
aiflow check-update
aiflow upgrade
```

Conserva una copia `.previous` della precedente installazione. Non modifica automaticamente i progetti. Dentro ogni progetto esegui `aiflow integrate both` e `aiflow doctor`.

## Report email

Il setup può illustrare come configurare il riepilogo, ma non salva password e non configura da solo un scheduler. Segui `DAILY_DIGEST.md` per SMTP e `launchd`.

## Limiti

Una GitHub Release con `aiflow-release.zip` e `aiflow-release.zip.sha256` deve essere pubblicata prima dell'installazione remota. Il checksum non è una firma indipendente.
