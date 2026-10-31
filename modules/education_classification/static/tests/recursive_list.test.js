/** @odoo-module **/

/*
 * Hoot regression tests for the recursive classification list (Odoo 18).
 *
 * Run from /web/tests with the filter "education_classification".
 * These tests use Odoo's mock server and the real view/controller/renderer.
 * They do not require or modify the module's UNESCO/ISCED reference data.
 */

import { beforeEach, expect, test } from "@odoo/hoot";
import {
    contains,
    defineModels,
    fields,
    models,
    mountView,
    onRpc,
    pagerNext,
    removeFacet,
    toggleMenuItem,
    toggleSearchBarMenu,
    webModels,
} from "@web/../tests/web_test_helpers";

class ClassificationEdition extends models.Model {
    _name = "education.classification.edition";

    name = fields.Char();

    _records = [
        { id: 10, name: "Edition A" },
        { id: 20, name: "Edition B" },
    ];
}

class ClassificationItem extends models.Model {
    _name = "education.classification.item";

    name = fields.Char();
    code = fields.Char();
    sequence = fields.Integer();
    sequence_path = fields.Char();
    parent_id = fields.Many2one({ relation: "education.classification.item" });
    edition_id = fields.Many2one({ relation: "education.classification.edition" });
    child_count = fields.Integer();
    level = fields.Integer();

    _records = [];
}

// ListController needs the standard user, partner and company mock models.
// Odoo 18's own list-view tests register these alongside their test models.
const { ResCompany, ResPartner, ResUsers } = webModels;

defineModels([
    ClassificationEdition,
    ClassificationItem,
    ResCompany,
    ResPartner,
    ResUsers,
]);

const ROOT_A = {
    id: 1,
    name: "Root A",
    code: "A",
    sequence: 1,
    sequence_path: "0001/",
    parent_id: false,
    edition_id: 10,
    child_count: 2,
    level: 0,
};
const CHILD_A1 = {
    id: 2,
    name: "Child A1",
    code: "A1",
    sequence: 1,
    sequence_path: "0001/0001/",
    parent_id: 1,
    edition_id: 10,
    child_count: 1,
    level: 1,
};
const CHILD_A2 = {
    id: 3,
    name: "Child A2",
    code: "A2",
    sequence: 2,
    sequence_path: "0001/0002/",
    parent_id: 1,
    edition_id: 10,
    child_count: 0,
    level: 1,
};
const ROOT_B = {
    id: 4,
    name: "Root B",
    code: "B",
    sequence: 1,
    sequence_path: "0001/",
    parent_id: false,
    edition_id: 20,
    child_count: 0,
    level: 0,
};
const GRANDCHILD = {
    id: 5,
    name: "Grandchild A1a",
    code: "A1a",
    sequence: 1,
    sequence_path: "0001/0001/0001/",
    parent_id: 2,
    edition_id: 10,
    child_count: 0,
    level: 2,
};

const ROOT_DOMAIN = [["parent_id", "=", false]];
const LIST_ARCH = '<list js_class="education_classification_recursive_list" ' +
    'default_order="edition_id,sequence_path,sequence,id" limit="80">' +
    '<field name="code"/>' +
    '<field name="name"/>' +
    '<field name="edition_id" optional="hide"/>' +
    '<field name="parent_id" optional="hide"/>' +
    '<field name="child_count" readonly="1"/>' +
    '</list>';

beforeEach(() => {
    ClassificationItem._records = [
        { ...ROOT_A },
        { ...CHILD_A1 },
        { ...CHILD_A2 },
        { ...ROOT_B },
        { ...GRANDCHILD },
    ];
});

function rowNames() {
    return Array.from(
        document.querySelectorAll(".o_data_row .o_data_cell[name='name']")
    ).map((cell) => cell.textContent.trim());
}

test("education_classification: expand, collapse, and reopen descendants", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: ROOT_DOMAIN,
    });

    expect(rowNames()).toEqual(["Root A", "Root B"]);
    await contains('.o_expand_button[data-expand="1"]').click();
    expect(rowNames()).toEqual(["Root A", "Child A1", "Child A2", "Root B"]);

    await contains('.o_expand_button[data-expand="2"]').click();
    expect(rowNames()).toEqual([
        "Root A",
        "Child A1",
        "Grandchild A1a",
        "Child A2",
        "Root B",
    ]);

    await contains('.o_expand_button[data-expand="1"]').click();
    expect(rowNames()).toEqual(["Root A", "Root B"]);

    // Reopening the parent must restore the previously expanded grandchild.
    await contains('.o_expand_button[data-expand="1"]').click();
    expect(rowNames()).toEqual([
        "Root A",
        "Child A1",
        "Grandchild A1a",
        "Child A2",
        "Root B",
    ]);
});

test("education_classification: searching respects root and child filters", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        context: { search_default_root_items: 1 },
        searchViewArch:
            '<search>' +
            '<field name="name"/>' +
            '<filter name="root_items" string="Root Categories" ' +
            'domain="[(\'parent_id\', \'=\', False)]"/>' +
            '<filter name="child_items" string="Child Categories" ' +
            'domain="[(\'parent_id\', \'!=\', False)]"/>' +
            '</search>',
    });

    expect(rowNames()).toEqual(["Root A", "Root B"]);

    await removeFacet("Root Categories");
    expect(rowNames()).toEqual([
        "Root A",
        "Child A1",
        "Grandchild A1a",
        "Child A2",
        "Root B",
    ]);

    await toggleSearchBarMenu();
    await toggleMenuItem("Child Categories");
    expect(rowNames()).toEqual(["Child A1", "Grandchild A1a", "Child A2"]);
});

test("education_classification: root pagination changes the visible records", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH.replace('limit="80"', 'limit="1"'),
        domain: ROOT_DOMAIN,
    });

    expect(rowNames()).toEqual(["Root A"]);
    await pagerNext();
    expect(rowNames()).toEqual(["Root B"]);
});

test("education_classification: lazy children are fetched in multiple pages", async () => {
    const siblings = Array.from({ length: 205 }, (_, index) => ({
        id: index + 2,
        name: "Child " + String(index + 1).padStart(3, "0"),
        code: "C" + String(index + 1).padStart(3, "0"),
        sequence: index + 1,
        sequence_path: "0001/" + String(index + 1).padStart(4, "0") + "/",
        parent_id: 1,
        edition_id: 10,
        child_count: 0,
        level: 1,
    }));
    ClassificationItem._records = [
        { ...ROOT_A, child_count: 205 },
        ...siblings,
    ];

    const pages = [];
    onRpc("web_search_read", ({ kwargs }) => {
        const domain = kwargs.domain || [];
        if (domain.some((term) => Array.isArray(term) &&
            term[0] === "parent_id" && term[1] === "in")) {
            pages.push([kwargs.offset || 0, kwargs.limit]);
        }
    });

    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: ROOT_DOMAIN,
    });
    expect(rowNames()).toEqual(["Root A"]);

    await contains('.o_expand_button[data-expand="1"]').click();

    expect(rowNames()).toHaveLength(206);
    expect(rowNames()[1]).toBe("Child 001");
    expect(rowNames()[205]).toBe("Child 205");
    expect(pages).toEqual([[0, 200], [200, 200]]);
});

test("education_classification: expansion works in an opened edition group", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: ROOT_DOMAIN,
        groupBy: ["edition_id"],
    });

    expect(".o_group_header").toHaveCount(2);
    await contains(".o_group_header:eq(0)").click();
    expect('.o_expand_button[data-expand="1"]').toHaveCount(1);

    await contains('.o_expand_button[data-expand="1"]').click();
    expect(rowNames()).toEqual(["Root A", "Child A1", "Child A2"]);
});

test("education_classification: parent and level groups do not expand across groups", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        groupBy: ["parent_id"],
    });

    await contains(".o_group_header:eq(0)").click();
    expect(".o_expand_button").toHaveCount(0);
});

test("education_classification: grouping by level disables recursive controls", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        groupBy: ["level"],
    });

    await contains(".o_group_header:eq(0)").click();
    expect(".o_expand_button").toHaveCount(0);
});
