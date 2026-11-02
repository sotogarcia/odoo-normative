/** @odoo-module **/

/*
 * Adapted from recursive_list_view for Odoo 18.
 * Copyright (C) 2023 Bemade Inc. — Marc Durepos.
 * Source: https://github.com/bemade/bemade-addons/tree/18.0/recursive_list_view
 * Original license: LGPL-3.0.
 * Adaptation for education_classification: Jorge Soto García, 2026.
 */

import { ListRenderer } from "@web/views/list/list_renderer";

export class EducationClassificationRecursiveListRenderer extends ListRenderer {
    // Dedicated OWL templates; do not modify Odoo's global ListRenderer.
    static template = "education_classification.RecursiveListRenderer";
    static recordRowTemplate =
        "education_classification.RecursiveListRenderer.RecordRow";

    // Odoo's standard column count does not include the custom tree
    // expander column. Account for it in group headers and pagers too.
    get nbCols() {
        return super.nbCols + 1;
    }

    getGroupNameCellColSpan(group) {
        return super.getGroupNameCellColSpan(group) + 1;
    }

    // Odoo's group header describes all matching records (group.count),
    // while the inner list is paginated by visual roots (group.list.count).
    // Keep those counts independent when rendering the group pager.
    getGroupPagerProps(group) {
        const props = super.getGroupPagerProps(group);
        if (this.env.model.canExpandRecursively() && !group.list.isGrouped) {
            return { ...props, total: group.list.count };
        }
        return props;
    }

    // The standard renderer tests the number of root list records. In this
    // view the selection checkbox must reflect *all displayed rows*, including
    // descendants, rather than roots alone.
    get selectAll() {
        if (!this.env.model.canExpandRecursively()) {
            return super.selectAll;
        }
        if (this.props.list.isDomainSelected) {
            return true;
        }
        const records = this.env.model.getVisibleRecords(this.props.list);
        return records.length > 0 && records.every((record) => record.selected);
    }

    // Shift-selection must follow the rendered row order, not list.records
    // (which deliberately contains only visual roots).
    toggleRecordShiftSelection(record) {
        if (!this.env.model.canExpandRecursively()) {
            return super.toggleRecordShiftSelection(record);
        }
        const records = this.env.model.getVisibleRecords(this.props.list);
        const from = records.indexOf(this.lastCheckedRecord);
        const to = records.indexOf(record);
        if (from === -1 || to === -1) {
            record.toggleSelection();
            return;
        }
        const selected = record.selected;
        for (let i = Math.min(from, to); i <= Math.max(from, to); i++) {
            records[i].toggleSelection(!selected);
        }
    }

    hasChildren(record) {
        return this.env.model.hasMatchingChildren(record);
    }

    _onExpandClick(ev) {
        // The button template already stops and prevents click propagation,
        // including inside an opened Odoo group.
        const parentId = Number(ev.currentTarget.dataset.expand);
        if (!Number.isInteger(parentId) || parentId <= 0) {
            return;
        }
        this.env.model.bus.trigger("expand-collapse-parent", { id: parentId });
    }
}
