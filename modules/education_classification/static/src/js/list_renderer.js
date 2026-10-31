/** @odoo-module **/

/*
 * Adapted from recursive_list_view for Odoo 18.
 * Copyright (C) 2023 Bemade Inc. — Marc Durepos.
 * Source: https://github.com/bemade/bemade-addons/tree/18.0/recursive_list_view
 * Original license: LGPL-3.0.
 * Adaptation for education_classification: Jorge Soto García, 2026.
 */

import { ListRenderer } from "@web/views/list/list_renderer";
import { useState } from "@odoo/owl";

export class EducationClassificationRecursiveListRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.recursive = true;
        useState(this.props.list.records);
    }

    hasChildren(record) {
        return (record.children?.length ?? 0) > 0 ||
            (record.data?.child_count ?? 0) > 0;
    }

    _onExpandClick(ev) {
        ev.preventDefault();
        ev.stopPropagation();

        const parentId = Number(ev.currentTarget.dataset.expand);
        if (!Number.isInteger(parentId) || parentId <= 0) {
            return;
        }
        this.env.model.bus.trigger("expand-collapse-parent", { id: parentId });
    }
}
