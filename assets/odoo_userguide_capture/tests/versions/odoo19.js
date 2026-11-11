// Odoo 19 (selectors read from 19.0+e source; run-verified with the built-in examples).
const UG = {
  listAddLine: '.o_field_x2many_list_row_add a',                    // <a role="button">, a <button> in 20
  activityMenu: '.o_menu_systray button:has(i.fa-clock-o)',         // aria-label is translated, do not use it
  userMenu: '.o_user_menu button',                                       // avatar menu in the navbar
  partnerNameColumn: 'complete_name',                               // base.view_partner_tree
};
