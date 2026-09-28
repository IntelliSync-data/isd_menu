import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";

/**
 * Export All downloads straight away with whatever columns the list happens to
 * show, which leaves no way to pick a saved export template. Open the export
 * dialog instead.
 *
 * Export All is only offered while no record is selected, so downloadExport
 * still sends no ids and the export covers every record matching the filters.
 */
patch(ListController.prototype, {
    async onDirectExportData() {
        return this.onExportData();
    },
});
