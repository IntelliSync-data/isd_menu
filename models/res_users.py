# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    menu_config_ids = fields.One2many(
        'user.menu.config',
        'user_id',
        string='Menu Configuration'
    )

    @api.model
    def create(self, vals_list):
        """Override to auto-initialize menu config for new users"""
        users = super().create(vals_list)

        # Auto-initialize menu config for each new user
        for user in users:
            user._auto_initialize_menu_config()

        return users

    def _auto_initialize_menu_config(self):
        """Auto-initialize menu config from Default User Template

        Copies menu configuration from the "Default User Template" user.
        """
        self.ensure_one()

        # Find Default User Template (it's usually a user with login='__default__' or name='Default User Template')
        default_user = self.env.ref('base.default_user', raise_if_not_found=False)

        if not default_user:
            # Try finding by name if ref doesn't work
            default_user = self.env['res.users'].sudo().search([
                ('name', '=', 'Default User Template')
            ], limit=1)

        if not default_user:
            # No default user template found, don't create any config
            return

        # Get menu config from Default User Template
        default_configs = self.env['user.menu.config'].sudo().search([
            ('user_id', '=', default_user.id)
        ])

        if not default_configs:
            # Default user has no menu config, don't create any config
            return

        # Copy menu config from Default User Template
        config_model = self.env['user.menu.config'].sudo()
        for config in default_configs:
            # Check if config already exists
            existing = config_model.search([
                ('user_id', '=', self.id),
                ('menu_id', '=', config.menu_id.id)
            ], limit=1)

            if not existing:
                config_model.create({
                    'user_id': self.id,
                    'menu_id': config.menu_id.id,
                    'show_menu': config.show_menu,
                })

    def action_apply_menu_settings(self):
        """Refresh menu settings by clearing cache and reloading"""
        self.ensure_one()
        # Clear all menu-related caches
        self.env['ir.ui.menu'].clear_caches()
        self.env['user.menu.config'].clear_caches()
        self.clear_caches()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_initialize_menu_config(self):
        """Initialize menu config with all root menus"""
        self.ensure_one()

        # Get all root menus (parent_id is False)
        root_menus = self.env['ir.ui.menu'].search([('parent_id', '=', False)])

        # Create config for each root menu if not exists
        for menu in root_menus:
            existing = self.env['user.menu.config'].search([
                ('user_id', '=', self.id),
                ('menu_id', '=', menu.id)
            ], limit=1)

            if not existing:
                self.env['user.menu.config'].create({
                    'user_id': self.id,
                    'menu_id': menu.id,
                    'show_menu': True,  # Default to show
                })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Menu configuration initialized successfully!'),
                'type': 'success',
                'sticky': False,
            }
        }
