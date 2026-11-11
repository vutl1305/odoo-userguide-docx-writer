# Odoo user guide skills

Two agent skills (Claude Code / Codex) for Vietnamese, customer-facing Odoo user guides in Word:

| Skill | Purpose |
| --- | --- |
| `odoo-userguide-docx-writer/` | Outline, SRS-based task guides, real screenshots (Odoo `HttpCase` + Chrome), sections written as Markdown. |
| `odoo-userguide-docx-export/` | Local, no-AI export of reviewed Markdown into the customer's DOCX (figures, references, borders, TOC pages, checks). |

## Install

Install both skills side by side (the writer calls the export skill):

```bash
git clone git@github.com:vutl1305/odoo-userguide-docx-writer.git /tmp/ug-skills
mkdir -p .claude/skills            # per project; or ~/.claude/skills for all projects
cp -R /tmp/ug-skills/odoo-userguide-docx-* .claude/skills/
```

Then ask the agent, e.g. “Dùng skill odoo-userguide-docx-writer viết mục 3.3”.
