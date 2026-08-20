# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """After first install: snapshot current menu order."""
    env['isd.menu.sequence'].save_current_order()


def _apply_menu_order_after_upgrade(env):
    """Called after any module upgrade to restore custom menu order."""
    try:
        env['isd.menu.sequence'].apply_saved_order()
    except Exception:
        _logger.warning("Could not re-apply custom menu order", exc_info=True)
