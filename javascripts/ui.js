
function uiCloneElement(oldElement) {
    
    newElement = oldElement.clone();  // clone an existing address field group

    // Clean all the input values:
    newElement.find("input,select").val('');
    newElement.hide();
    psinqueSetMarkingOnChange(newElement.find('input,select'));

    return newElement;
}

function uiChangeLabelHeight(label, howMuch) {
  
    tableCell = $(label).closest("td");
    currentHeight = parseInt(tableCell.attr("rowspan"));
    if(currentHeight + howMuch == 0) {
        tableCell.closest("table").remove();
    } else {
        tableCell.attr("rowspan", currentHeight + howMuch);
    }
}

function uiRemoveTableRow(tr, prefix) {
  
    tr.slideUp('fast', function() {
        labelid = "#" + prefix + "label";
        if(tr.find(labelid).length > 0) {
//             console.log("Found label in this row");
            $(labelid).parent().prependTo(tr.next());
        }
        uiChangeLabelHeight(labelid, -1);
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
                uiRemoveTableRow(tr, prefix);
            });
        } else {
            uiRemoveTableRow(tr, prefix);
        }
      
        return false;
    });
  
}

function uiAddAddHandler(prefix, removeAjax) {

    $("#add" + prefix).click(function() {
      
        tr = uiAddNewTableRow(prefix, removeAjax);
        tr.slideDown();
        
        return false;
    });

}

function uiAddEnterAction(where, trigger) {
  
    $(where).keyup(function(event) {
      
        if(event.keyCode == 13) {
            $(trigger).click();
        }
      
    });
}

function uiInitializeCheckboxes() {
    $("input[type=checkbox] + div").bind('click', function() {
        checkBox = $(this).prev();
//         checkBox.prop("checked", !checkBox.prop("checked"));
        checkBox.click();
    });
}

function uiShowErrorMessage(messageText) {
  
   $("body").append("<div id='overlay'></div>");

   $("#overlay")
      .height($(document).height())
      .css({
         'opacity' : 0.6,
         'position': 'fixed',
         'top': 0,
         'left': 0,
         'background-color': 'black',
         'width': '100%',
         'z-index': 5000
      });
    
    $("#overlay").append("<div id='dialogbox'></div>");
    
    $("#dialogbox").dialog({
        autoOpen: false,
        modal: true,
        dialogClass: "no-close",
        width: 500,
        buttons: {
          "Dismiss": function() {
            $(this).dialog("close");
            $("#overlay").remove();
          }
        },
        title: 'Error'
    });

    $("#dialogbox").html(messageText);
    $("#dialogbox").dialog("open");
    
}

function removeElementWithEffects(element) {
    element.slideUp('fast', function() {
        element.remove();
    });
}

function hideElementWithEffects(element) {
    element.slideUp('fast');
}

function showElementWithEffects(element) {
    element.slideDown('fast');
}

function startLogoAnimation() {
    window.onbeforeunload = function() {
        return "An AJAX query is in progress. Please wait until it's done.";
    }
    $("#staticlogo").hide();
    $("#animatedlogo").show();
}

function stopLogoAnimation() {
    window.onbeforeunload = null;
    $("#staticlogo").show();
    $("#animatedlogo").hide();
}

function markChangedFields(where) {
    $(where).css("color", "#de5d35");
    $(where).find("input,select").css("color", "#de5d35");
}

function unmarkChangedFields(where) {
    $(where).css("color", "inherit");
    $(where).find("input,select,label").css("color", "inherit");
}

function unmarkAllFields() {
    unmarkChangedFields(document);
}

function psinqueSetMarkingOnChange(where) {
    $(where).change(function() {
        markChangedFields(this);
    });
}

$(document).ready(function() {
    
    $('select').dropdown();
    
    psinqueSetMarkingOnChange("input,select");
    uiInitializeCheckboxes();
    
});
