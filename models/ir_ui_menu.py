# -*- coding: utf-8 -*-

from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def write(self, vals):
        res = super().write(vals)
        # Only save custom sequence when changed via UI (not during module upgrade)
        if (
            'sequence' in vals
            and not self.env.context.get('isd_menu_applying')
            and not self.pool._init
        ):
            root_menus = self.filtered(lambda m: not m.parent_id)
            if root_menus:
                SeqModel = self.env['isd.menu.sequence'].sudo()
                for menu in root_menus:
                    existing = SeqModel.search([('menu_id', '=', menu.id)], limit=1)
                    if existing:
                        existing.write({'sequence': menu.sequence})
                    else:
                        SeqModel.create({'menu_id': menu.id, 'sequence': menu.sequence})
        return res

    @api.model
    def load_menus(self, debug=False):
        """Override to apply custom menu filtering, ordering, and sync DB sequence."""
        # Sync DB sequence from isd_menu_sequence before loading
        # This ensures Menu Setting list view shows correct order
        self._sync_custom_sequence_to_db()

        menus = super().load_menus(debug=debug)

        # Re-sort root children by custom sequence
        menus = self._apply_custom_menu_order(menus)

        # Check if current user has custom menu configuration
        user_id = self.env.user.id
        config_model = self.env['user.menu.config']

        if not config_model.has_custom_config(user_id):
            return menus

        all_configs = config_model.search([('user_id', '=', user_id)])
        hidden_root_ids = set(all_configs.filtered(lambda c: not c.show_menu).mapped('menu_id.id'))

        if not hidden_root_ids:
            return menus

        def get_descendants_from_dict(menu_id, menus_dict):
            descendants = {menu_id}
            if menu_id in menus_dict:
                for child_id in menus_dict[menu_id].get('children', []):
                    descendants.update(get_descendants_from_dict(child_id, menus_dict))
            return descendants

        hidden_ids = set()
        for hidden_root_id in hidden_root_ids:
            hidden_ids.update(get_descendants_from_dict(hidden_root_id, menus))

        filtered_menus = {}
        for menu_id, menu_data in menus.items():
            if menu_id == 'root':
                root_copy = menu_data.copy()
                root_copy['children'] = [
                    child_id for child_id in menu_data.get('children', [])
                    if child_id not in hidden_ids
                ]
                filtered_menus['root'] = root_copy
            elif menu_id not in hidden_ids:
                menu_copy = menu_data.copy()
                menu_copy['children'] = [
                    child_id for child_id in menu_data.get('children', [])
                    if child_id not in hidden_ids
                ]
                filtered_menus[menu_id] = menu_copy

        return filtered_menus

    @api.model
    def _sync_custom_sequence_to_db(self):
        """Sync saved custom sequences back to ir_ui_menu.sequence via SQL."""
        try:
            self.env.cr.execute("""
                UPDATE ir_ui_menu m
                SET sequence = s.sequence
                FROM isd_menu_sequence s
                WHERE m.id = s.menu_id AND m.sequence != s.sequence
            """)
            if self.env.cr.rowcount:
                _logger.info(f"Synced {self.env.cr.rowcount} menu sequences from custom order")
        except Exception:
            pass

    @api.model
    def _apply_custom_menu_order(self, menus):
        """Re-sort root menu children based on saved custom sequence."""
        try:
            self.env.cr.execute("SELECT menu_id, sequence FROM isd_menu_sequence")
            saved = dict(self.env.cr.fetchall())
        except Exception:
            return menus

        if not saved or 'root' not in menus:
            return menus

        root = menus['root']
        children = root.get('children', [])
        if not children:
            return menus

        def sort_key(menu_id):
            if menu_id in saved:
                return saved[menu_id]
            menu_data = menus.get(menu_id, {})
            return menu_data.get('sequence', 999)

        root['children'] = sorted(children, key=sort_key)
        return menus
