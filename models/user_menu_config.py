# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class UserMenuConfig(models.Model):
    _name = 'user.menu.config'
    _description = 'User Menu Configuration'
    _rec_name = 'menu_id'

    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade', index=True)
    menu_id = fields.Many2one('ir.ui.menu', string='Menu', required=True, ondelete='cascade', index=True)
    show_menu = fields.Boolean(string='Show Menu', default=True)

    _sql_constraints = [
        ('user_menu_unique', 'unique(user_id, menu_id)', _('Menu configuration must be unique per user!'))
    ]

    def write(self, vals):
        """Override to clear menu cache when configuration changes"""
        result = super().write(vals)
        # Clear menu cache for affected users
        self.env['ir.ui.menu'].clear_caches()
        return result

    @api.model
    def create(self, vals_list):
        """Override to clear menu cache when creating configuration"""
        result = super().create(vals_list)
        # Clear menu cache
        self.env['ir.ui.menu'].clear_caches()
        return result

    def unlink(self):
        """Override to clear menu cache when deleting configuration"""
        result = super().unlink()
        # Clear menu cache
        self.env['ir.ui.menu'].clear_caches()
        return result

    @api.model
    def get_user_visible_menus(self, user_id):
        """Get list of menu IDs that user is allowed to see"""
        configs = self.search([('user_id', '=', user_id), ('show_menu', '=', True)])
        return configs.mapped('menu_id').ids

    @api.model
    def has_custom_config(self, user_id):
        """Check if user has any custom menu configuration"""
        return bool(self.search_count([('user_id', '=', user_id)]))
