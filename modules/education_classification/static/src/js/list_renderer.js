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
    // Dedicated OWL templates; do not modify Odoo's global ListRenderer.
    static template = "education_classification.RecursiveListRenderer";
    static recordRowTemplate =
        "education_classification.RecursiveListRenderer.RecordRow";

    setup() {
        super.setup();
        this.recursive = true;
        useState(this.props.list.records);
    }

    // Odoo's standard column count does not include the custom tree
    // expander column. Account for it in group headers and pagers too.
    get nbCols() {
        return super.nbCols + 1;
    }

    getGroupNameCellColSpan(group) {
        return super.getGroupNameCellColSpan(group) + 1;
    }

    // Keep the group's matched-record count in its header, but paginate
    // the projected visual roots rather than all matching descendants.
    getGroupPagerProps(group) {
        const props = super.getGroupPagerProps(group);
        if (this.env.model.canExpandRecursively() && !group.list.isGrouped) {
            return { ...props, total: group.list.count };
        }
        return props;
    }

    hasChildren(record) {
        return this.env.model.hasMatchingChildren(record);
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
