
function uiChangeLabelHeight(where, howMuch) {
    tableLabel = $(where);
    currentHeight = parseInt(tableLabel.attr("rowspan"));
    tableLabel.attr("rowspan", currentHeight + howMuch);
}
