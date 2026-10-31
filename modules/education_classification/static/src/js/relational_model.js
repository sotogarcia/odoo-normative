/** @odoo-module **/

/*
 * Adapted from recursive_list_view for Odoo 18.
 * Copyright (C) 2023 Bemade Inc. — Marc Durepos.
 * Source: https://github.com/bemade/bemade-addons/tree/18.0/recursive_list_view
 * Original license: LGPL-3.0.
 * Adaptation for education_classification: Jorge Soto García, 2026.
 */

import { RelationalModel } from "@web/model/relational_model/relational_model";
import {
    getBasicEvalContext,
    getFieldsSpec,
    makeActiveField,
} from "@web/model/relational_model/utils";

const PARENT_FIELD = "parent_id";
const CHILD_COUNT_FIELD = "child_count";
const CHILD_PAGE_SIZE = 200;
const CHILD_ORDER = "sequence asc, code asc, id asc";

export class EducationClassificationRecursiveListModel extends RelationalModel {
    setup(params, services) {
        super.setup(params, services);

        // The standard model replaces its root records on a search or reload.
        // Initialise each new root record without preloading descendants.
        const onRootLoaded = this.hooks.onRootLoaded;
        this.hooks.onRootLoaded = async (...args) => {
            await onRootLoaded(...args);
            if (!this.config.recursive || !this.root?.records) {
                return;
            }
            for (const record of this.root.records) {
                record.depth = 0;
                record.expanded = false;
                record.childrenFetched = false;
                record.children = record.data?.child_count > 0 ? [] : undefined;
            }
        };
    }

    async _loadData(config) {
        if (config.recursive && config.isRoot && !config.isMonoRecord && !config.resIds) {
            if (!config.fields[PARENT_FIELD] || !config.fields[CHILD_COUNT_FIELD]) {
                throw new Error(
                    "The recursive classification list requires parent_id and child_count."
                );
            }

            // The renderer needs child_count even when a column is hidden.
            // The parent relation is also required when instantiating children.
            config.activeFields[PARENT_FIELD] ??= makeActiveField({ invisible: true });
            config.activeFields[CHILD_COUNT_FIELD] ??= makeActiveField({ readonly: true });

            // Respect Odoo's search domain: the action's Root Categories
            // default filter already restricts the initial list to roots.
            // Removing that filter must allow searches to include descendants.
        }
        return super._loadData(config);
    }

    /**
     * The native grouped list puts rows inside group.list, possibly through
     * several nested group levels. Expand only when every grouping dimension
     * is invariant for a category and its descendants (edition_id).
     * Grouping by parent_id or level must remain a flat Odoo grouped list:
     * showing children under a different group's header would be misleading.
     */
    canExpandRecursively() {
        const groupBy = this.config.groupBy || [];
        return groupBy.every((field) => field.split(":")[0] === "edition_id");
    }

    /**
     * Groups opened after the root load create records that have not passed
     * through onRootLoaded. Initialise them when they are first expanded.
     * Do not reset an already expanded child encountered in a later search.
     */
    _ensureHierarchyRecordState(record) {
        if (record.depth === undefined) {
            record.depth = 0;
            record.expanded = false;
            record.childrenFetched = false;
            record.children = record.data?.child_count > 0 ? [] : undefined;
        }
    }

    async _loadChildren(records, config = this.config) {
        const parents = (Array.isArray(records) ? records : [records]).filter(
            (record) => record?.resId && !record.childrenFetched
        );
        if (!parents.length) {
            return;
        }

        const { resModel, activeFields, fields, context } = config;
        if (!resModel) {
            return;
        }

        const specification = getFieldsSpec(
            activeFields,
            fields,
            getBasicEvalContext(config)
        );
        const parentIds = parents.map((record) => record.resId);
        const childrenByParent = new Map(parentIds.map((id) => [id, []]));

        // web_search_read returns { records, length }, not a bare array.
        // Fetch all immediate children; its default limit would truncate
        // large groups of siblings.
        let offset = 0;
        while (true) {
            const result = await this.orm.webSearchRead(
                resModel,
                [[PARENT_FIELD, "in", parentIds]],
                {
                    context: { ...context },
                    specification,
                    offset,
                    limit: CHILD_PAGE_SIZE,
                    order: CHILD_ORDER,
                }
            );
            const children = result.records || [];
            for (const child of children) {
                // Odoo's web_read may return an ID or an {id, ...} object
                // for a many2one, depending on the field specification.
                const value = child[PARENT_FIELD];
                const parentId = typeof value === "object" ? value?.id : value;
                if (childrenByParent.has(parentId)) {
                    childrenByParent.get(parentId).push(child);
                }
            }
            offset += children.length;
            if (!children.length || offset >= result.length || children.length < CHILD_PAGE_SIZE) {
                break;
            }
        }

        for (const parent of parents) {
            const childData = childrenByParent.get(parent.resId) || [];
            const depth = parent.depth ?? 0;
            parent.children = childData.map((data) => {
                const record = new this.constructor.Record(
                    this,
                    {
                        context,
                        activeFields,
                        resModel,
                        fields,
                        resId: data.id,
                        resIds: [data.id],
                        isMonoRecord: true,
                        currentCompanyId: parent.currentCompanyId,
                        mode: parent.mode,
                    },
                    data,
                    { manuallyAdded: false }
                );
                record.depth = depth + 1;
                record.expanded = false;
                record.childrenFetched = false;
                record.children = record.data?.child_count > 0 ? [] : undefined;
                return record;
            });
            parent.childrenFetched = true;
        }
    }

    findRecordInHierarchy(resId) {
        const target = String(resId);

        const findRecords = (records) => {
            for (const record of records) {
                if (String(record.resId) === target) {
                    this._ensureHierarchyRecordState(record);
                    return record;
                }
                if (record.children?.length) {
                    const found = findRecords(record.children);
                    if (found) {
                        return found;
                    }
                }
            }
            return null;
        };

        // In Odoo 18 a grouped list stores records in Group.list, not in
        // the group headers. Only traverse opened groups with loaded rows;
        // never load a folded group merely to locate an expansion target.
        const findInList = (list) => {
            if (!list) {
                return null;
            }
            if (list.isGrouped) {
                for (const group of list.groups || []) {
                    if (!group.isFolded) {
                        const found = findInList(group.list);
                        if (found) {
                            return found;
                        }
                    }
                }
                return null;
            }
            return findRecords(list.records || []);
        };

        return findInList(this.root);
    }
}
