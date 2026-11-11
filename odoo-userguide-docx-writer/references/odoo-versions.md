# Odoo version profiles

The capture template loads `tests/versions/odoo<major>.js` (selectors that differ per version) and then `tests/versions/common.js` (helpers used by frames: `fld`, `fill`, `pick`, `tab`, `saveForm`, `actionMenu`, `addLine`, `openActivities`, `wideName`, `search`). Frames use only these helpers and `UG.*`, so the same frame code runs on every supported version. With no profile for the running version, every capture test fails with a message telling you to create one.

## Status

| Version | Profile | Run-verified | Python that works |
| --- | --- | --- | --- |
| 20.0 | `odoo20.js` | built-in examples on a plain DB; full CRM guide section (Entobel, 11/11/2026) | 3.14 |
| 19.0 | `odoo19.js` | built-in examples on a plain DB (11/11/2026) | 3.10 (**not 3.14**: `'OrderedSet' object has no attribute 'copy'` at registry load) |
| 18, 17 | none yet | — | — |

## Add a version

1. Copy the nearest profile to `versions/odoo<major>.js`.
2. Check each `UG` selector against that version's `web/` and `mail/` templates (grep the class in `static/src`), and the Python notes below.
3. Run the built-in examples (`test_login_logout`, `test_preferences`, `test_contact_form`) on a **plain** DB of that version (only `base`, `web`). A DB with customer modules may add required fields and make the plain contact example fail for business reasons.
4. Look at the images, then keep the profile in the skill and update this table.

## Known differences

| Item | 20 | 19 |
| --- | --- | --- |
| "Add a line" in one2many lists | `<button>` | `<a role="button">` |
| Activities systray icon | `i[data-icon="schedule"]` | `i.fa-clock-o` |
| User (avatar) menu | `button.o_user_menu` | `.o_user_menu button` (div wrapper) |
| Contacts list name column | `display_name` | `complete_name` |
| Individual/Company on the contact form | not in the standard form (a single "Name (company or person)" field; a customer module may add a radio) | `company_type` radio |
| Record action menu | ⋮ icon | ⚙ icon |
| "Schedule activity" dialog: activity type | badges `.o_selection_badge` (To-Do, Call, ...) | not checked |
| Kanban horizontal scroll container | `main.o_content` (not `.o_kanban_renderer`); `scrollIntoView` on a card can push the next column off-screen | not checked |
| `ir.config_parameter` | `set_str` | `set_param` (template falls back) |
| Users' groups field | `group_ids` | `group_ids` (18 and older: `groups_id`; use `user_groups_field(env)`) |

All versions:
- `aria-label` and button texts are translated: never select by `aria-label="Activities"`, `"Done"`, etc.; use classes, `data-*` or `byText` with the Vietnamese label.
- A form renders same-name fields inside its one2many/kanban sub-views; `fld()` keeps only main-form fields.
- Typing into a field triggers an onchange round-trip that re-renders the form; `fill()` waits for it, otherwise the next autocomplete loses its text (seen on 19).
- Kanban quick create → "Edit" saves the record first; fields that are not on the quick-create card (e.g. a required custom field) stay empty and must be filled on the form.
- The save button is hidden, not removed, after saving: wait for "not visible", not "not present".
- `ir.sequence` with the standard implementation uses PostgreSQL sequences, which are **not rolled back** with the test; switch the sequence to `no_gap` in `setUpClass` when images show generated numbers.
- A project config with `log_handler = :ERROR` writes nothing when tests pass; add `--log-handler=:INFO` to see `tests.result`.
