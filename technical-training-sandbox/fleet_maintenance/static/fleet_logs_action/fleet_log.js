odoo.define('fleet_maintenance.open_form_on_click', function (require) {
    "use strict";

    var ListController = require('web.ListController');

    ListController.include({
        _onRowClicked: function (event) {
            alert("LLEGAMOS");
            var self = this;
            this._super.apply(this, arguments);
            var $target = $(event.target);
            if ($target.hasClass('o_data_row')) {
                var recordID = $target.data('id');
                self.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'fleet.vehicle.assignation.log',
                    view_mode: 'form',
                    res_id: recordID,
                    target: 'current',
                });
            }
        },
    });
});