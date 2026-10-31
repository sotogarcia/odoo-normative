/** @odoo-module **/

/*
 * Register the dedicated recursive classification list in Odoo 18.
 *
 * The controller, renderer, model and OWL templates are adapted from
 * recursive_list_view by Marc Durepos / Bemade Inc. (LGPL-3.0):
 * https://github.com/bemade/bemade-addons/tree/18.0/recursive_list_view
 */

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";

import { EducationClassificationRecursiveListController } from "./list_controller";
import { EducationClassificationRecursiveListRenderer } from "./list_renderer";
import { EducationClassificationRecursiveListModel } from "./relational_model";

export const educationClassificationRecursiveListView = {
    ...listView,
    Controller: EducationClassificationRecursiveListController,
    Renderer: EducationClassificationRecursiveListRenderer,
    Model: EducationClassificationRecursiveListModel,
};

registry.category("views").add(
    "education_classification_recursive_list",
    educationClassificationRecursiveListView
);
