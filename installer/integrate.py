"""Project-local Codex and Claude Code integration; standard library only."""
from pathlib import Path
import json
import shutil
import sys

FRAMEWORK = Path(__file__).resolve().parents[1]
SKILLS = FRAMEWORK / 'core' / 'skills'
AGENTS = FRAMEWORK / 'core' / 'agents'

HEADER = '''# AIFlow agent integration (managed section)

This repository uses AIFlow for Epic/Task lifecycle and durable knowledge.
When the user types `aiflow?`, `ai flow?`, or `help aiflow`, invoke the installed `aiflow-help` skill and show contextual help. This is a read-only request: do not create or modify project state.
Run `aiflow status` and read `.aiflow/AGENTS.md`, `.aiflow/project.md`, `.aiflow/architecture.md`, `.aiflow/state/current.md` and the relevant Epic/Task documents before acting.
Use `aiflow` for creating IDs, status changes, session/track events and checkpoints. Do not invent approvals: only the human user can explicitly approve a decision or scope.
Use `aiflow recover` after context compaction or interruption. For durable checkpoints use `aiflow checkpoint EPIC-ID[/TASK-ID] "summary" --next "next step"`. Use `aiflow decision propose`, `aiflow decision approve`, and `aiflow approve` to record explicit user decisions; do not fabricate --by/--evidence. Use `aiflow workflow-task start/review/finish` and `aiflow workflow-epic start/approve/finish` for lifecycle. During analysis do not implement code. Capture proposals in the relevant Markdown and ask for grouped approval. In `analitica`, after asking a question that needs user input, STOP the turn and WAIT for the reply; never continue the workflow or choose defaults in the same turn. Persist checkpoints during long tasks and before context compaction; on resume read the durable files again.
Keep Task `task.md` and `report.md` updated, including acceptance criteria, implementation, test results, unresolved issues and handoff. Read `.aiflow/profiles/README.md` and follow every relevant active technology profile together. If profiles conflict, ask the developer rather than silently choosing. Respect the project tech profiles.
Do not commit, push, deploy, access privileged servers, or invoke trust-server without the user's explicit authorization. Never record secrets in Markdown.
Skill entrypoints are installed locally under `.agents/skills/` (Codex) or `.claude/skills/` (Claude Code).
'''
START='<!-- AIFLOW:START -->'
END='<!-- AIFLOW:END -->'

def managed(path, content):
    block = f'{START}\n{content.rstrip()}\n{END}\n'
    if path.exists():
        original=path.read_text(encoding='utf-8')
        if START in original and END in original:
            before, tail = original.split(START,1)
            _, after = tail.split(END,1)
            updated=before+block+after.lstrip('\n')
        else:
            updated=original.rstrip()+'\n\n'+block
    else:
        updated=block
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(updated,encoding='utf-8')

def install(root, target='both'):
    if target not in ('codex','claude','both'):
        raise ValueError('Target non valido')
    if not (root/'.aiflow'/'config.json').exists():
        raise ValueError('Esegui prima aiflow init')
    targets=['codex','claude'] if target=='both' else [target]
    created=[]
    for tool in targets:
        skillbase=root/('.agents/skills' if tool=='codex' else '.claude/skills')
        for skill in sorted(SKILLS.iterdir()):
            if not (skill/'SKILL.md').exists(): continue
            dest=skillbase/('aiflow-'+skill.name)
            dest.mkdir(parents=True,exist_ok=True)
            original=(skill/'SKILL.md').read_text(encoding='utf-8')
            original += "\n\n## Contratto workflow\nLeggere `core/GOVERNANCE_V2.md` nel framework installato. Usare `aiflow recover` per ricostruire il contesto e `aiflow checkpoint` prima della compattazione. Approvazioni solo su istruzione umana esplicita; aggiornare `task.md`, `analysis.md`, `ux.md`, `report.md` senza inventare risultati.\n"
            prefix='''\n## Esecuzione AIFlow (obbligatoria)\n- CLI: `aiflow` deve essere disponibile nel PATH (oppure eseguire il path assoluto configurato).\n- Prima di operare, `aiflow status` e lettura dei documenti `.aiflow` rilevanti.\n- Per Epic/Task usare `aiflow epic create`, `aiflow task create`, `aiflow epic status`, `aiflow task status`; per registrare checkpoint/decisioni usare `aiflow note`.\n- Scrivere e mantenere i documenti reali `.aiflow/epics/<EPIC-ID>/` e `.aiflow/epics/<EPIC-ID>/tasks/<TASK-ID>/`, senza sovrascrivere contenuto approvato.\n- Durante `analitica` non scrivere codice applicativo. Non considerare approvata una decisione senza conferma esplicita dell'utente.\n- `--confirm` va usato solo dopo verifica e autorizzazione umana, mai come scorciatoia.\n- Documentare risultati, test, rischi e prossimi passi nel report Task; fare checkpoint prima della compattazione.\n'''
            if skill.name == 'trust-server':
                # Never overwrite a pre-existing privileged skill without explicit migration.
                if (dest/'SKILL.md').exists() and '## Limite della versione' not in (dest/'SKILL.md').read_text(encoding='utf-8'):
                    created.append(str(dest.relative_to(root))+' (existing; preserved)')
                    continue
                (dest/'SKILL.md').write_text(original,encoding='utf-8')
            else:
                (dest/'SKILL.md').write_text(original.rstrip()+'\n'+prefix,encoding='utf-8')
            created.append(str(dest.relative_to(root)))
        if tool=='codex':
            managed(root/'AGENTS.md', HEADER)
            created.append('AGENTS.md')
        else:
            managed(root/'CLAUDE.md',HEADER)
            created.append('CLAUDE.md')
            # Claude Code supports project hooks for PreCompact and SessionStart.
            # Preserve existing user hooks and avoid duplicate AIFlow entries.
            settings=root/'.claude/settings.json'
            try:
                config=json.loads(settings.read_text(encoding='utf-8')) if settings.exists() else {}
            except json.JSONDecodeError as exc:
                raise ValueError(f'Invalid Claude settings.json: {exc}')
            hooks=config.setdefault('hooks',{})
            hookfile=FRAMEWORK/'installer/hooks.py'
            for event_name, action in [('PreCompact','precompact'),('SessionStart','sessionstart')]:
                entries=hooks.setdefault(event_name,[])
                command=f'{sys.executable} {hookfile} {action}'
                # Only replace hooks previously installed by AIFlow.
                for entry in entries:
                    entry['hooks']=[h for h in entry.get('hooks',[]) if 'installer/hooks.py' not in h.get('command','')]
                entries[:]=[e for e in entries if e.get('hooks')]
                entries.append({'hooks':[{'type':'command','command':command,'timeout':15}]})
            settings.parent.mkdir(parents=True,exist_ok=True)
            settings.write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            created.append(str(settings.relative_to(root)))
            agentsbase=root/'.claude/agents' 
            agentsbase.mkdir(parents=True,exist_ok=True)
            for agent in sorted(AGENTS.glob('*.md')):
                # Install reference descriptions; agents are not automatically delegated.
                content=agent.read_text(encoding='utf-8')
                (agentsbase/('aiflow-'+agent.name)).write_text(content,encoding='utf-8')
                created.append(str((agentsbase/('aiflow-'+agent.name)).relative_to(root)))
    cfg=root/'.aiflow/config.json'
    data=json.loads(cfg.read_text(encoding='utf-8'))
    data['integrations']=sorted(set(data.get('integrations',[])+targets))
    cfg.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return created

# The local integration intentionally does not install automatic shell hooks:
# compaction callbacks vary by tool/version. Agents must call `aiflow checkpoint`
# at meaningful boundaries and `aiflow recover` when resuming.
