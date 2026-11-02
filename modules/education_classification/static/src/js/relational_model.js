/** @odoo-module **/

/*
 * Adapted from recursive_list_view for Odoo 18.
 * Copyright (C) 2023 Bemade Inc. — Marc Durepos.
 * Source: https://github.com/bemade/bemade-addons/tree/18.0/recursive_list_view
 * Original license: LGPL-3.0.
 * Adaptation for education_classification: Jorge Soto García, 2026.
 */

import { Domain } from "@web/core/domain";
import { RelationalModel } from "@web/model/relational_model/relational_model";
import {
    getBasicEvalContext,
    getFieldsSpec,
    makeActiveField,
} from "@web/model/relational_model/utils";
import { orderByToString } from "@web/search/utils/order_by";

const PARENT_FIELD = "parent_id";
const CHILD_COUNT_FIELD = "child_count";
const PAGE_SIZE = 200;

/**
 * Present search results as a forest, not as a list of database roots.
 *
 * The search domain and context determine the set of eligible records. A
 * record is a visual root when its parent is not in that set; expanding a
 * node shows only its eligible immediate children. This also works when a
 * search matches descendants but excludes their ancestors.
 *
 * Root pagination is applied after constructing the forest. Applying the
 * original list limit before identifying roots would silently lose roots
 * whose parents or siblings happen to be on other pages.
 */
export class EducationClassificationRecursiveListModel extends RelationalModel {
    setup(params, services) {
        super.setup(params, services);

        this._recursiveIndices = new Map();
        this._recursiveIndexById = new Map();
        this._recursiveGroupingCompatible = true;
        this._recursiveGeneration = 0;

        const onWillLoadRoot = this.hooks.onWillLoadRoot;
        this.hooks.onWillLoadRoot = (config) => {
            this._recursiveGeneration++;
            this._recursiveIndices.clear();
            this._recursiveIndexById.clear();
            this._recursiveGroupingCompatible = (config.groupBy || []).every(
                (field) => field.split(":")[0] === "edition_id"
            );
            return onWillLoadRoot(config);
        };

        const onRootLoaded = this.hooks.onRootLoaded;
        this.hooks.onRootLoaded = async (...args) => {
            await onRootLoaded(...args);
            if (!this.config.recursive) {
                return;
            }
            // Group rows are loaded lazily and do not necessarily exist when
            // onRootLoaded runs. They are initialised when first expanded.
            for (const record of this.root?.records || []) {
                this._ensureHierarchyRecordState(record);
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
            config.activeFields[PARENT_FIELD] ??= makeActiveField({ invisible: true });
            config.activeFields[CHILD_COUNT_FIELD] ??= makeActiveField({ readonly: true });
        }
        return super._loadData(config);
    }

    /**
     * Non-invariant groupings (such as parent or hierarchy level) retain
     * Odoo's normal grouped list. A recursive child cannot be placed under
     * a group header for a different value of the grouping field.
     */
    canExpandRecursively() {
        return this._recursiveGroupingCompatible;
    }

    /**
     * Load *matching* ids and parent references in the same order as Odoo's
     * list. This is a separate projection query; never rewrite config.domain
     * or config.context and never alter the search used by other views.
     *
     * All matching ids are required to distinguish a genuine visual root
     * from a matching child whose parent is on a different page.
     */
    async _getRecursiveIndex(config) {
        const key = JSON.stringify([
            config.resModel,
            config.domain,
            config.context,
            config.orderBy,
        ]);
        if (!this._recursiveIndices.has(key)) {
            const promise = this._buildRecursiveIndex(config);
            this._recursiveIndices.set(key, promise);
            promise.catch(() => {
                if (this._recursiveIndices.get(key) === promise) {
                    this._recursiveIndices.delete(key);
                }
            });
        }
        return this._recursiveIndices.get(key);
    }

    async _buildRecursiveIndex(config) {
        const generation = this._recursiveGeneration;
        const order = orderByToString(
            (config.orderBy || []).filter((item) => item.name !== "__count")
        );
        const matches = [];
        let offset = 0;
        while (true) {
            const batch = await this.orm.searchRead(
                config.resModel,
                config.domain,
                ["id", PARENT_FIELD],
                {
                    context: config.context,
                    offset,
                    limit: PAGE_SIZE,
                    order,
                }
            );
            matches.push(...batch);
            offset += batch.length;
            if (batch.length < PAGE_SIZE) {
                break;
            }
        }

        const ids = new Set(matches.map((record) => record.id));
        const roots = [];
        const childrenByParent = new Map();

        for (const record of matches) {
            const value = record[PARENT_FIELD];
            const parentId = Array.isArray(value)
                ? value[0]
                : typeof value === "object" && value !== null
                  ? value.id
                  : value;

            if (ids.has(parentId)) {
                if (!childrenByParent.has(parentId)) {
                    childrenByParent.set(parentId, []);
                }
                childrenByParent.get(parentId).push(record.id);
            } else {
                roots.push(record.id);
            }
        }

        const index = {
            roots,
            childrenByParent,
            domain: config.domain,
            context: config.context,
            order,
        };
        // A newer search may have replaced this forest while its RPCs
        // were pending. Never let a stale search populate the current
        // record-to-index lookup.
        if (generation === this._recursiveGeneration) {
            for (const id of ids) {
                this._recursiveIndexById.set(id, index);
            }
        }
        return index;
    }

    /**
     * Odoo's native list paginates database records. Here the paginated
     * records are visual roots *of the current search result*, irrespective
     * of their real parent_id. This also handles opened edition groups,
     * because Odoo supplies each group's effective domain in config.
     */
    async _loadUngroupedList(config) {
        if (!this._recursiveGroupingCompatible || config.resIds) {
            return super._loadUngroupedList(config);
        }

        const index = await this._getRecursiveIndex(config);
        const roots = index.roots.slice(
            config.offset || 0,
            (config.offset || 0) + config.limit
        );
        const records = await this._loadRecords({ ...config, resIds: roots });
        return { records, length: index.roots.length };
    }

    /**
     * Odoo's "fetch full count" normally counts all matching database rows.
     * Our pager counts visible roots of the filtered forest instead, so the
     * full-count action must use the same projection as the initial load.
     */
    async _updateCount(config) {
        if (!this.canExpandRecursively() || config.isMonoRecord || config.resIds) {
            return super._updateCount(config);
        }
        const index = await this._getRecursiveIndex(config);
        config.countLimit = Number.MAX_SAFE_INTEGER;
        return index.roots.length;
    }

    hasMatchingChildren(record) {
        if (!this.canExpandRecursively()) {
            return false;
        }
        const index = this._recursiveIndexById.get(record.resId);
        if (index) {
            return (index.childrenByParent.get(record.resId)?.length || 0) > 0;
        }
        return (record.data?.[CHILD_COUNT_FIELD] || 0) > 0;
    }

    _ensureHierarchyRecordState(record) {
        if (record.depth === undefined) {
            record.depth = 0;
            record.expanded = false;
            record.childrenFetched = false;
            record.children = [];
        }
    }

    /**
     * Children are read from the *same filtered set* as their visual roots.
     * Repeat the original domain in the fetch to respect concurrent changes
     * and access rules, as well as search context (including active_test).
     */
    async _loadChildren(record, config = this.config) {
        const parents = Array.isArray(record) ? record : [record];
        for (const parent of parents) {
            if (!parent?.resId || parent.childrenFetched) {
                continue;
            }

            const index = this._recursiveIndexById.get(parent.resId);
            const ids = index?.childrenByParent.get(parent.resId) || [];
            const data = [];
            if (ids.length) {
                const specification = getFieldsSpec(
                    config.activeFields,
                    config.fields,
                    getBasicEvalContext(config)
                );
                const domain = Domain.and([
                    index.domain,
                    [["id", "in", ids]],
                    [[PARENT_FIELD, "=", parent.resId]],
                ]).toList();
                let offset = 0;
                while (true) {
                    const result = await this.orm.webSearchRead(
                        config.resModel,
                        domain,
                        {
                            context: index.context,
                            specification,
                            offset,
                            limit: PAGE_SIZE,
                            order: index.order,
                        }
                    );
                    const batch = result.records || [];
                    data.push(...batch);
                    offset += batch.length;
                    if (batch.length < PAGE_SIZE || offset >= result.length) {
                        break;
                    }
                }
            }

            // Preserve the order of the original filtered search even if a
            // read returns records in a different order.
            const positions = new Map(ids.map((id, position) => [id, position]));
            data.sort((a, b) => positions.get(a.id) - positions.get(b.id));
            const depth = parent.depth ?? 0;
            parent.children = data.map((values) => {
                const child = new this.constructor.Record(
                    this,
                    {
                        context: index.context,
                        activeFields: config.activeFields,
                        resModel: config.resModel,
                        fields: config.fields,
                        resId: values.id,
                        resIds: [values.id],
                        isMonoRecord: true,
                        currentCompanyId: parent.currentCompanyId,
                        mode: parent.mode,
                    },
                    values,
                    { manuallyAdded: false }
                );
                child.depth = depth + 1;
                child.expanded = false;
                child.childrenFetched = false;
                child.children = [];
                return child;
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
                const child = findRecords(record.children || []);
                if (child) {
                    return child;
                }
            }
            return null;
        };

        const findInList = (list) => {
            if (!list) {
                return null;
            }
            if (list.isGrouped) {
                for (const group of list.groups || []) {
                    if (!group.isFolded) {
                        const record = findInList(group.list);
                        if (record) {
                            return record;
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
