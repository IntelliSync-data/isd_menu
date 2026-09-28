import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

/**
 * Shown in place of an action the user is not allowed to open.
 *
 * Returning a real client action instead of raising keeps the web client in a
 * valid state: the screen loads, says why, and offers the way back.
 */
export class IsdMenuAccessDenied extends Component {
    static template = "isd_menu.AccessDenied";
    static props = ["*"];

    get message() {
        return (
            this.props.action.params?.message ||
            "You do not have access to this page."
        );
    }

    goHome() {
        window.location.href = "/odoo";
    }
}

registry.category("actions").add("isd_menu_access_denied", IsdMenuAccessDenied);
