/** @odoo-module **/

/*
 * Hoot regression tests for the recursive classification list (Odoo 18).
 *
 * Run from /web/tests with the filter "education_classification".
 * These tests use Odoo's mock server and the real view/controller/renderer.
 * They do not require or modify the module's UNESCO/ISCED reference data.
 */

import { animationFrame, beforeEach, click, Deferred, expect, test } from "@odoo/hoot";
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
    // Numeric test-only sorting proxy: Odoo 18's MockServer cannot
    // reliably sort integer-valued Many2one fixtures by their relation.
    edition_sort = fields.Integer();
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
// The production view orders by edition_id,sequence_path,sequence,id.
// HOOT's mock sorter expects a relational [id, name] while validated
// Many2one fixtures store an integer ID. edition_sort mirrors edition_id
// solely for mock ordering; grouping still uses edition_id.
const LIST_ARCH = '<list js_class="education_classification_recursive_list" ' +
    'default_order="edition_sort,sequence_path,sequence,id" limit="80">' +
    '<field name="code"/>' +
    '<field name="name"/>' +
    '<field name="edition_id" optional="hide"/>' +
    '<field name="parent_id" optional="hide"/>' +
    '<field name="child_count" readonly="1"/>' +
    '</list>';

function setClassificationRecords(records) {
    ClassificationItem._records = records.map((record) => ({
        ...record,
        edition_sort: record.edition_id,
    }));
}

beforeEach(() => {
    setClassificationRecords([
        { ...ROOT_A },
        { ...CHILD_A1 },
        { ...CHILD_A2 },
        { ...ROOT_B },
        { ...GRANDCHILD },
    ]);
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
        domain: [],
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
    expect(rowNames()).toEqual(["Root A", "Root B"]);
    await contains('.o_expand_button[data-expand="1"]').click();
    expect(rowNames()).toEqual(["Root A", "Child A1", "Child A2", "Root B"]);

    await toggleSearchBarMenu();
    await toggleMenuItem("Child Categories");
    expect(rowNames()).toEqual(["Child A1", "Child A2"]);
    await contains('.o_expand_button[data-expand="2"]').click();
    expect(rowNames()).toEqual(["Child A1", "Grandchild A1a", "Child A2"]);
});

test("education_classification: root pagination changes the visible records", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH.replace('limit="80"', 'limit="1"'),
        domain: [],
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
    setClassificationRecords([
        { ...ROOT_A, child_count: 205 },
        ...siblings,
    ]);

    const pages = [];
    onRpc("web_search_read", ({ kwargs }) => {
        const domain = kwargs.domain || [];
        if (domain.some((term) => Array.isArray(term) &&
            term[0] === "parent_id" && term[1] === "=")) {
            pages.push([kwargs.offset || 0, kwargs.limit]);
        }
    });

    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: [],
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
        domain: [],
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


test("education_classification: matching parents and children render exactly once", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: [],
    });

    // The raw search matches five records, but the forest has two roots.
    expect(rowNames()).toEqual(["Root A", "Root B"]);

    await contains('.o_expand_button[data-expand="1"]').click();
    expect(rowNames()).toEqual(["Root A", "Child A1", "Child A2", "Root B"]);

    await contains('.o_expand_button[data-expand="2"]').click();
    expect(rowNames()).toEqual([
        "Root A", "Child A1", "Grandchild A1a", "Child A2", "Root B",
    ]);
});

test("education_classification: filtered descendants are promoted to visual roots", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: [["code", "in", ["A1", "A1a"]]],
    });

    // The database parent of A1 is excluded; A1 must not disappear.
    expect(rowNames()).toEqual(["Child A1"]);
    await contains('.o_expand_button[data-expand="2"]').click();
    expect(rowNames()).toEqual(["Child A1", "Grandchild A1a"]);
});

test("education_classification: expansion never shows excluded children", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: [["code", "in", ["A", "A2", "B"]]],
    });

    expect(rowNames()).toEqual(["Root A", "Root B"]);
    await contains('.o_expand_button[data-expand="1"]').click();
    expect(rowNames()).toEqual(["Root A", "Child A2", "Root B"]);
    expect('.o_expand_button[data-expand="2"]').toHaveCount(0);
});

test("education_classification: an explicit root-only filter has no matching descendants", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: ROOT_DOMAIN,
    });

    expect(rowNames()).toEqual(["Root A", "Root B"]);
    expect(".o_expand_button").toHaveCount(0);
});

test("education_classification: pagination counts visual roots rather than matched rows", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH.replace('limit="80"', 'limit="1"'),
        domain: [],
    });

    expect(rowNames()).toEqual(["Root A"]);
    await pagerNext();
    expect(rowNames()).toEqual(["Root B"]);
});

test("education_classification: fetching the exact count uses visual roots", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH
            .replace('limit="80"', 'limit="1" count_limit="1"'),
        domain: [],
    });

    // Five matching database records produce only two visual roots.
    expect(".o_pager_limit").toHaveText("1+");
    await contains(".o_pager_limit").click();
    expect(".o_pager_limit").toHaveText("2");

    await pagerNext();
    expect(rowNames()).toEqual(["Root B"]);
});

test("education_classification: late child loading does not expand a replaced page", async () => {
    const pendingChildren = new Deferred();
    onRpc("web_search_read", ({ kwargs }) => {
        const domain = kwargs.domain || [];
        if (domain.some((term) => Array.isArray(term) &&
            term[0] === "parent_id" && term[1] === "=" && term[2] === 1)) {
            return pendingChildren;
        }
    });

    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH.replace('limit="80"', 'limit="1"'),
        domain: [],
    });

    expect(rowNames()).toEqual(["Root A"]);
    await click('.o_expand_button[data-expand="1"]');
    await animationFrame();
    expect('.o_expand_button[data-expand="1"]').toHaveAttribute("disabled");
    expect('.o_expand_button[data-expand="1"]').toHaveAttribute("aria-busy", "true");

    await pagerNext();
    expect(rowNames()).toEqual(["Root B"]);

    pendingChildren.resolve();
    await animationFrame();
    expect(rowNames()).toEqual(["Root B"]);
});

test("education_classification: recursive styles are scoped to their renderer", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: [],
    });

    expect(".o_list_renderer.o_education_classification_recursive_list").toHaveCount(1);
    expect('.o_expand_button[data-expand="1"]').toHaveCount(1);
});


test("education_classification: expander column stays aligned without selectors", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: [],
        allowSelectors: false,
    });

    expect(".o_list_renderer thead th.o_list_record_selector").toHaveCount(0);
    expect(".o_list_renderer thead th.o_recursive_expand_column").toHaveCount(1);
    expect(".o_list_renderer tbody tr.o_data_row > td.o_recursive_expand_column").toHaveCount(2);
    expect(".o_list_renderer tfoot td.o_recursive_expand_column").toHaveCount(1);

    await contains('.o_expand_button[data-expand="1"]').click();
    expect(rowNames()).toEqual(["Root A", "Child A1", "Child A2", "Root B"]);
    expect(".o_list_renderer tbody tr.o_data_row > td.o_recursive_expand_column").toHaveCount(4);
});

test("education_classification: grouped headers span all columns without selectors", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: [],
        groupBy: ["edition_id"],
        allowSelectors: false,
    });

    const columns = document.querySelectorAll(
        ".o_list_renderer thead tr > th"
    ).length;
    const header = document.querySelector(".o_list_renderer .o_group_header");
    const span = Array.from(header.children).reduce(
        (count, cell) => count + cell.colSpan,
        0
    );
    expect(span).toBe(columns);

    await contains(".o_group_header:eq(0)").click();
    await contains('.o_expand_button[data-expand="1"]').click();
    expect(rowNames()).toEqual(["Root A", "Child A1", "Child A2"]);
});

test("education_classification: expand controls expose accessible state", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: [],
        allowSelectors: false,
    });

    const button = '.o_expand_button[data-expand="1"]';
    expect(button).toHaveAttribute("aria-label", "Expand or collapse child categories");
    expect(button).toHaveAttribute("aria-expanded", "false");
    expect(button).toHaveAttribute("aria-busy", "false");

    await contains(button).click();
    expect(button).toHaveAttribute("aria-expanded", "true");
    expect(".o_recursive_bullet[data-depth='1']").toHaveCount(1);

    await contains('.o_expand_button[data-expand="2"]').click();
    expect(".o_recursive_bullet[data-depth='2']").toHaveCount(1);

    await contains(button).click();
    expect(button).toHaveAttribute("aria-expanded", "false");
});

test("education_classification: expand column precedes optional selectors", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: [],
        allowSelectors: true,
    });

    const headerCells = document.querySelectorAll(".o_list_renderer thead tr > th");
    expect(headerCells[0]).toHaveClass("o_recursive_expand_column");
    expect(headerCells[1]).toHaveClass("o_list_record_selector");

    const rowCells = document.querySelectorAll(
        ".o_list_renderer tbody tr.o_data_row:first-child > td"
    );
    expect(rowCells[0]).toHaveClass("o_recursive_expand_column");
    expect(rowCells[1]).toHaveClass("o_list_record_selector");
});

test("education_classification: indentation supports depths beyond twelve", async () => {
    const items = [{ ...ROOT_A, child_count: 1 }];
    for (let depth = 1; depth <= 14; depth++) {
        items.push({
            id: 100 + depth,
            name: "Depth " + depth,
            code: "D" + depth,
            sequence: 1,
            sequence_path: "0001/" + "0001/".repeat(depth),
            parent_id: depth === 1 ? 1 : 99 + depth,
            edition_id: 10,
            child_count: depth < 14 ? 1 : 0,
            level: depth,
        });
    }
    setClassificationRecords(items);

    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: [],
    });

    for (let depth = 1; depth <= 14; depth++) {
        await contains('.o_expand_button[data-expand="' + (
            depth === 1 ? 1 : 99 + depth
        ) + '"]').click();
    }

    // Use the public depth marker, not the internal Odoo record key.
    const depthCell = document.querySelector(
        '.o_recursive_bullet[data-depth="14"]'
    ).closest("td");
    expect(depthCell.style.getPropertyValue("--ec-recursive-depth").trim()).toBe("14");
});

test("education_classification: selecting a descendant updates the selected ids", async () => {
    let selectedIds = [];
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: [],
        onSelectionChanged: (ids) => { selectedIds = ids; },
    });

    await contains('.o_expand_button[data-expand="1"]').click();
    await contains(".o_data_row .o_list_record_selector input:eq(1)").click();

    expect(".o_list_selection_box").toHaveText("1\nselected");
    expect(selectedIds).toEqual([2]);
    expect(".o_data_row .o_list_record_selector input:checked").toHaveCount(1);
});

test("education_classification: shift selection includes intermediate descendants", async () => {
    let selectedIds = [];
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: [],
        onSelectionChanged: (ids) => { selectedIds = ids; },
    });

    await contains('.o_expand_button[data-expand="1"]').click();
    await contains(".o_data_row .o_list_record_selector input:eq(0)").click();
    await contains(".o_data_row .o_list_record_selector input:eq(2)").click({
        shiftKey: true,
    });

    expect(".o_data_row .o_list_record_selector input:checked").toHaveCount(3);
    expect(selectedIds).toEqual([1, 2, 3]);
});

test("education_classification: select all includes expanded descendants", async () => {
    let selectedIds = [];
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        domain: [],
        onSelectionChanged: (ids) => { selectedIds = ids; },
    });

    await contains('.o_expand_button[data-expand="1"]').click();
    await contains('.o_expand_button[data-expand="2"]').click();
    await contains("thead .o_list_record_selector input").click();

    expect(".o_data_row .o_list_record_selector input:checked").toHaveCount(5);
    expect(selectedIds).toEqual([1, 2, 5, 3, 4]);
    expect(".o_list_selection_box").toHaveText("5\nselected");

    await contains("thead .o_list_record_selector input").click();
    expect(".o_data_row .o_list_record_selector input:checked").toHaveCount(0);
    expect(selectedIds).toEqual([]);
});

test("education_classification: selecting a descendant works in an edition group", async () => {
    let selectedIds = [];
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        groupBy: ["edition_id"],
        domain: [],
        onSelectionChanged: (ids) => { selectedIds = ids; },
    });

    await contains(".o_group_header:eq(0)").click();
    await contains('.o_expand_button[data-expand="1"]').click();
    await contains(".o_data_row .o_list_record_selector input:eq(1)").click();

    expect(".o_list_selection_box").toHaveText("1\nselected");
    expect(selectedIds).toEqual([2]);
});

test("education_classification: nonrecursive grouping keeps standard selection", async () => {
    let selectedIds = [];
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: LIST_ARCH,
        groupBy: ["level"],
        domain: [],
        onSelectionChanged: (ids) => { selectedIds = ids; },
    });

    await contains(".o_group_header:eq(0)").click();
    await contains(".o_data_row .o_list_record_selector input:eq(0)").click();
    expect(selectedIds).toHaveLength(1);
    expect(".o_list_selection_box").toHaveText("1\nselected");
});

test("education_classification: standard list does not receive recursive CSS scope", async () => {
    await mountView({
        type: "list",
        resModel: "education.classification.item",
        arch: '<list><field name="name"/></list>',
        domain: [],
    });

    expect(".o_list_renderer").toHaveCount(1);
    expect(".o_list_renderer.o_education_classification_recursive_list").toHaveCount(0);
});
