# -*- coding: utf-8 -*-

from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def load_menus(self, debug=False):
        """Override to apply custom menu filtering

        Logic:
        - Menus NOT in config: show based on access rights (default behavior)
        - Menus IN config with show_menu=True: show them + all children
        - Menus IN config with show_menu=False: hide them + all children
        """
        # Get default menus (flat dictionary based on access rights)
        menus = super().load_menus(debug=debug)

        # Check if current user has custom menu configuration
        user_id = self.env.user.id
        config_model = self.env['user.menu.config']

        if not config_model.has_custom_config(user_id):
            # No custom config, return default menus based on access rights
            _logger.info(f'User {user_id} has no custom menu config, showing all menus')
            return menus

        # Get all menu configs for this user (both show_menu=True and False)
        all_configs = config_model.search([('user_id', '=', user_id)])

        # Build sets of menu IDs to hide (show_menu=False)
        hidden_root_ids = set(all_configs.filtered(lambda c: not c.show_menu).mapped('menu_id.id'))

        _logger.info(f'User {user_id} has {len(all_configs)} menu configs, {len(hidden_root_ids)} hidden roots')

        if not hidden_root_ids:
            # All configured menus are visible, return default
            _logger.info(f'User {user_id} has no hidden menus, showing all menus')
            return menus

        # Build set of all menu IDs to hide (roots + all descendants)
        def get_descendants_from_dict(menu_id, menus_dict):
            """Get all descendant IDs from flat menu dictionary"""
            descendants = {menu_id}
            if menu_id in menus_dict:
                for child_id in menus_dict[menu_id].get('children', []):
                    descendants.update(get_descendants_from_dict(child_id, menus_dict))
            return descendants

        hidden_ids = set()
        for hidden_root_id in hidden_root_ids:
            hidden_ids.update(get_descendants_from_dict(hidden_root_id, menus))

        _logger.info(f'User {user_id} total hidden menu IDs (including children): {len(hidden_ids)}')

        # Filter menus dictionary - remove hidden menus
        filtered_menus = {}
        for menu_id, menu_data in menus.items():
            if menu_id == 'root':
                # Handle root specially - filter out hidden children
                root_copy = menu_data.copy()
                root_copy['children'] = [
                    child_id for child_id in menu_data.get('children', [])
                    if child_id not in hidden_ids
                ]
                filtered_menus['root'] = root_copy
            elif menu_id not in hidden_ids:
                # Include this menu if not hidden, filter its children list
                menu_copy = menu_data.copy()
                menu_copy['children'] = [
                    child_id for child_id in menu_data.get('children', [])
                    if child_id not in hidden_ids
                ]
                filtered_menus[menu_id] = menu_copy

        _logger.info(f'User {user_id} filtered menus: {len(filtered_menus) - 1} total (excluding root)')

        return filtered_menus
