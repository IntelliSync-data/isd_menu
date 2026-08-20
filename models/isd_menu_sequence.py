# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class IsdMenuSequence(models.Model):
    _name = 'isd.menu.sequence'
    _description = 'Custom Menu Sequence'

    def _register_hook(self):
        """Re-apply saved menu order after registry rebuild (runs after all data files loaded)."""
        super()._register_hook()
        try:
            cr = self.env.cr
            cr.execute("SELECT COUNT(*) FROM isd_menu_sequence")
            count = cr.fetchone()[0]
            if count == 0:
                # First time or empty — snapshot current order
                cr.execute("""
                    INSERT INTO isd_menu_sequence (menu_id, sequence, create_uid, write_uid, create_date, write_date)
                    SELECT id, sequence, 1, 1, NOW(), NOW()
                    FROM ir_ui_menu WHERE parent_id IS NULL
                """)
                _logger.info("Saved initial menu order snapshot")
            else:
                # Re-apply saved order
                cr.execute("SELECT menu_id, sequence FROM isd_menu_sequence")
                for menu_id, seq in cr.fetchall():
                    cr.execute(
                        "UPDATE ir_ui_menu SET sequence = %s WHERE id = %s AND sequence != %s",
                        (seq, menu_id, seq),
                    )
                _logger.info(f"Re-applied custom menu order ({count} entries checked)")
        except Exception:
            _logger.warning("Could not re-apply custom menu order", exc_info=True)

    menu_id = fields.Many2one(
        'ir.ui.menu', string='Menu',
        required=True, ondelete='cascade', index=True,
    )
    sequence = fields.Integer('Sequence', default=10)

    _sql_constraints = [
        ('unique_menu', 'UNIQUE(menu_id)', 'Each menu can only have one custom sequence.'),
    ]

    @api.model
    def save_current_order(self):
        """Snapshot current root menu sequences."""
        root_menus = self.env['ir.ui.menu'].sudo().search([('parent_id', '=', False)])
        for menu in root_menus:
            existing = self.sudo().search([('menu_id', '=', menu.id)], limit=1)
            if existing:
                if existing.sequence != menu.sequence:
                    existing.sudo().write({'sequence': menu.sequence})
            else:
                self.sudo().create({
                    'menu_id': menu.id,
                    'sequence': menu.sequence,
                })
        _logger.info(f"Saved custom menu order for {len(root_menus)} root menus")

    @api.model
    def apply_saved_order(self):
        """Re-apply saved custom sequences to root menus."""
        saved = self.sudo().search([])
        if not saved:
            return
        count = 0
        for record in saved:
            if record.menu_id.exists() and record.menu_id.sequence != record.sequence:
                record.menu_id.sudo().with_context(isd_menu_applying=True).write({'sequence': record.sequence})
                count += 1
        if count:
            _logger.info(f"Re-applied custom menu order for {count} menus")
