# -*- coding: utf-8 -*-

import logging

from odoo import _
from odoo.http import request

from odoo.addons.web.controllers.action import Action

_logger = logging.getLogger(__name__)


class IsdMenuAction(Action):
    """Hiding a menu only removes the button; the action behind it stays one
    URL away. Every action the web client opens goes through /web/action/load,
    so this is the single place that can turn a hidden menu into a closed door.
    """

    def load(self, action_id, context=None):
        action = super().load(action_id, context=context)

        if not action or not isinstance(action, dict):
            return action

        blocked = request.env['ir.ui.menu'].sudo()._get_isd_blocked_action_ids()
        if not blocked or action.get('id') not in blocked:
            return action

        _logger.info(
            "isd_menu: user %s was refused action %s (menu hidden for them)",
            request.env.user.login, action.get('id'))

        return {
            'type': 'ir.actions.client',
            'tag': 'isd_menu_access_denied',
            'target': 'current',
            'name': _('Access denied'),
            'params': {
                'message': _("You do not have access to this page."),
            },
        }
