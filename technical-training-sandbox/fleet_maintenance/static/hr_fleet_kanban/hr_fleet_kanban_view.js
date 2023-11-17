/** @odoo-module **/

import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { HrFleetKanbanController } from "@fleet_maintenance/views/hr_fleet_kanban/hr_fleet_kanban_controller";

export const hrFleetKanbanView = {
    ...kanbanView,
    Controller: HrFleetKanbanController,
    buttonTemplate: "fleet_maintenance.HrFleetKanbanController.Buttons",
};
registry.category("views").add("fleet_maintenance_kanban_view", hrFleetKanbanView);
