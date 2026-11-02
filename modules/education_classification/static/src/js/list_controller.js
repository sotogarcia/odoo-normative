/** @odoo-module **/

/*
 * Adapted from recursive_list_view for Odoo 18.
 * Copyright (C) 2023 Bemade Inc. — Marc Durepos.
 * Source: https://github.com/bemade/bemade-addons/tree/18.0/recursive_list_view
 * Original license: LGPL-3.0.
 * Adaptation for education_classification: Jorge Soto García, 2026.
 */

import { _t } from "@web/core/l10n/translation";
import { useBus, useService } from "@web/core/utils/hooks";
import { ListController } from "@web/views/list/list_controller";

export class EducationClassificationRecursiveListController extends ListController {
    setup() {
        super.setup();
        this.notification = useService("notification");
        useBus(this.model.bus, "expand-collapse-parent", this.onExpandCollapseParent);
    }

    /**
     * A search, a group refresh or pagination can replace the record while
     * its children are loading. Never expand a stale record or report a
     * stale request as an error in the current view.
     */
    _isCurrentHierarchyRecord(record) {
        return this.model.findRecordInHierarchy(record.resId) === record;
    }

    async onExpandCollapseParent(ev) {
        if (!this.model.canExpandRecursively()) {
            return;
        }

        const parentId = ev.detail?.id ?? ev.detail;
        const record = this.model.findRecordInHierarchy(parentId);
        if (!record || !this.model.hasMatchingChildren(record) || record.loadingChildren) {
            return;
        }

        if (record.expanded) {
            record.expanded = false;
            this.model.notify();
            return;
        }

        if (record.childrenFetched) {
            record.expanded = record.children.length > 0;
            this.model.notify();
            return;
        }

        record.loadingChildren = true;
        this.model.notify();
        try {
            await this.model._loadChildren(record);
            if (this._isCurrentHierarchyRecord(record)) {
                record.expanded = record.children.length > 0;
            }
        } catch (error) {
            if (this._isCurrentHierarchyRecord(record)) {
                // Allow retrying after an RPC error, without losing the
                // current search, selection or grouping.
                record.childrenFetched = false;
                record.children = [];
                this.notification.add(
                    _t("Unable to load child categories. Please try again."),
                    { type: "danger" }
                );
                console.error("Education classification: child loading failed", error);
            }
        } finally {
            record.loadingChildren = false;
            if (this._isCurrentHierarchyRecord(record)) {
                this.model.notify();
            }
        }
    }

    /**
     * Odoo's default openRecord() supplies only root.records as navigation
     * ids. In the recursive list a displayed descendant is not a root record,
     * so use the same visible row order as the renderer when opening a form.
     * Custom open actions and non-recursive groupings keep Odoo's behaviour.
     */
    async openRecord(record, force = false) {
        if (
            !this.model.canExpandRecursively() ||
            (this.props.allowOpenAction && this.archInfo.openAction)
        ) {
            return super.openRecord(record, force);
        }

        const visibleRecords = this.model.getVisibleRecords();
        if (!visibleRecords.includes(record)) {
            return super.openRecord(record, force);
        }

        const dirty = await record.isDirty();
        if (dirty) {
            await record.save();
        }

        const activeIds = visibleRecords.map((item) => item.resId);
        return this.props.selectRecord(record.resId, { activeIds, force });
    }

    get nbTotal() {
        return this.model.getMatchingCount() ?? super.nbTotal;
    }

    get isPageSelected() {
        if (!this.model.canExpandRecursively()) {
            return super.isPageSelected;
        }
        const records = this.model.getVisibleRecords();
        return records.length > 0 && records.every((record) => record.selected);
    }

    discardSelection() {
        if (!this.model.canExpandRecursively()) {
            return super.discardSelection();
        }
        for (const record of this.model.getLoadedRecords()) {
            if (record.selected) {
                record.toggleSelection(false);
            }
        }
    }

    onUnselectAll() {
        if (!this.model.canExpandRecursively()) {
            return super.onUnselectAll();
        }
        this.discardSelection();
        return this.model.root.selectDomain(false);
    }

    get modelParams() {
        const params = super.modelParams;
        return {
            ...params,
            config: { ...params.config, recursive: true },
        };
    }
}
