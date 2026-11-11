// Form/list helpers shared by all Odoo versions. Selectors that differ per version come from UG
// (versions/odooNN.js, loaded first). Every helper fails through el/until/byText when something is missing.
const M = '.o_action_manager .o_form_view ';
// Main-form field only: a form also renders same-name fields inside its one2many/kanban sub-views.
const fld = n => M + `.o_field_widget[name="${n}"]:not(.o_field_x2many .o_field_widget)`;
const fill = async (q, v) => { const i = await el(q); i.focus(); i.value = v;
  i.dispatchEvent(new Event('input', {bubbles: true})); i.dispatchEvent(new Event('change', {bubbles: true}));
  await paint(); await pause(800); };   // let the onchange round-trip re-render the form before the next field
const pick = async (q, typed, label) => { const i = await el(q); i.focus(); i.click(); i.value = typed;
  i.dispatchEvent(new Event('input', {bubbles: true}));
  (await byText('.o-autocomplete--dropdown-item', label || typed)).click();
  await until(() => !document.querySelector('.o-autocomplete--dropdown-item'), 'autocomplete closed'); await pause(500); };
const tab = async label => { (await byText(M + '.o_notebook .nav-link', label)).click(); await pause(400); };
const saveForm = async () => { (await el('.o_form_button_save')).click();
  await until(() => !visible(document.querySelector('.o_form_button_save')), 'record saved'); await pause(800); };
const actionMenu = async () => { (await el('.o_cp_action_menus button')).click(); await el('.o-dropdown--menu'); await pause(300); };
const addLine = async field => { (await el(fld(field) + ' ' + UG.listAddLine)).click(); await el(fld(field) + ' .o_selected_row'); await pause(400); };
const openActivities = async () => { (await el(UG.activityMenu)).click(); await el('.o-mail-ActivityMenu'); };
// Widen the name column like a user dragging it (list names are otherwise cut to "Công ty C...").
const wideName = async (col = UG.partnerNameColumn) => {
  (await el(`.o_list_renderer th[data-name="${col}"]`)).style.width = '330px'; await paint(); await pause(200); };
const search = async t => { const i = await el('.o_searchview_input'); i.focus(); i.value = t;
  i.dispatchEvent(new Event('input', {bubbles: true})); await pause(300);
  i.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true}));
  await until(() => document.querySelector('.o_searchview_facet'), 'search applied'); await pause(800); };
