import { registry } from "@web/core/registry";
import { dialogProps } from "@web/core/dialog/dialog";
import { t } from "@odoo/owl";

// Dialogs opened without a title
dialogProps.title = t.string().optional("WeberQ ERP");

// The user menu links to the support of Odoo.com
registry.category("user_menuitems").remove("support");
