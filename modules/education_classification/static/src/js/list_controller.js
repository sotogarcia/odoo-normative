/** @odoo-module **/

/*
 * Adapted from recursive_list_view for Odoo 18.
 * Copyright (C) 2023 Bemade Inc. — Marc Durepos.
 * Source: https://github.com/bemade/bemade-addons/tree/18.0/recursive_list_view
 * Original license: LGPL-3.0.
 * Adaptation for education_classification: Jorge Soto García, 2026.
 */

import { ListController } from "@web/views/list/list_controller";
import { useBus } from "@web/core/utils/hooks";

export class EducationClassificationRecursiveListController extends ListController {
    setup() {
        super.setup();
        useBus(this.model.bus, "expand-collapse-parent", this.onExpandCollapseParent);
    }

    async onExpandCollapseParent(ev) {
        if (!this.model.canExpandRecursively()) {
            return;
        }
        const parentId = ev.detail?.id ?? ev.detail;
        const record = this.model.findRecordInHierarchy(parentId);
        if (!record) {
            return;
        }
        if (record.expanded) {
            record.expanded = false;
            return;
        }
        if (record.loadingChildren) {
            return;
        }
        record.loadingChildren = true;
        try {
            await this.model._loadChildren(record);
            record.expanded = true;
        } finally {
            record.loadingChildren = false;
        }
    }

    get modelParams() {
        const params = super.modelParams;
        return {
            ...params,
            config: { ...params.config, recursive: true },
        };
    }
}
