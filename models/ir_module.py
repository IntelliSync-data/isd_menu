# -*- coding: utf-8 -*-

from odoo import models
import logging

_logger = logging.getLogger(__name__)


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    def button_immediate_upgrade(self):
        """Re-apply custom menu order after any module upgrade."""
        res = super().button_immediate_upgrade()
        try:
            self.env['isd.menu.sequence'].sudo().apply_saved_order()
        except Exception:
            _logger.warning("Could not re-apply custom menu order after module upgrade", exc_info=True)
        return res

    def button_immediate_install(self):
        """Re-apply custom menu order after any module install."""
        res = super().button_immediate_install()
        try:
            self.env['isd.menu.sequence'].sudo().apply_saved_order()
        except Exception:
            _logger.warning("Could not re-apply custom menu order after module install", exc_info=True)
        return res
