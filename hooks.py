# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """After first install: snapshot current menu order."""
    env['isd.menu.sequence'].save_current_order()
