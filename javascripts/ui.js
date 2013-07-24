
function uiCloneElement(oldElement) {
    
    newElement = oldElement.clone();  // clone an existing address field group

    // Clean all the input values:
    newElement.find("input,select").val('');
    newElement.hide();
    psinqueSetMarkingOnChange(newElement.find('input,select'));

    return newElement;
}

function uiChangeLabelHeight(where, howMuch) {
    tableLabel = $(where);
    currentHeight = parseInt(tableLabel.attr("rowspan"));
    tableLabel.attr("rowspan", currentHeight + howMuch);
}

function uiRemoveTableRow(tr, tablelabel) {
    tr.slideUp('fast', function() {
        uiChangeLabelHeight(tablelabel, -1);
        tr.remove();
    });
}

function uiAddNewTableRow(prefix, removeAjax) {
  
    tableName = "#" + prefix + "stable"
    removerClass = prefix + "removers"
  
    tr = uiCloneElement($(tableName + " > tbody > tr:first"));
    
    // Remove the table label
    tr.find('.formlabels').remove();

    // Resize the table label
    uiChangeLabelHeight("#" + prefix + "label", +1)
    
    // Replace the add button with a remove button
    tr.find(".formbuttons").remove();
    tr.append("<td class='forminputs formbuttons'><span class='" + removerClass + " buttons clickable'><img src='/images/button_remove.png' /></span></td>");

    // Show the new row
    $(tableName + "> tbody").append(tr);

    // Re-create the dropdown
    tr.find('.dropdown').remove();
    tr.find('select').dropdown();
    
    uiAddRemoverHandler(tr.find('.' + prefix + 'removers'), prefix, removeAjax);
    
    return tr;
}

function uiAddRemoverHandler(where, prefix, removeAjax) {
  
    $(where).click(function() {
        
        tr = $(this).parent().parent();
        itemKey = tr.find("." + prefix + "keys").val();
        if(itemKey) {
            removeAjax(itemKey, function() {
                uiRemoveTableRow(tr, "#" + prefix + "label");
            });
        } else {
            uiRemoveTableRow(tr, "#" + prefix + "label");
        }
      
        return false;
    });
  
}

function uiAddAddHandler(prefix, removeAjax) {

    $("#add" + prefix).click(function() {
      
        console.log("Adding " + prefix);
      
        tr = uiAddNewTableRow(prefix, removeAjax);
        tr.slideDown();
        
        return false;
    });

}
