
function uiCloneElement(oldElement) {
    
    newElement = oldElement.clone();  // clone an existing address field group

    // Clean all the input values:
//     newElement.find("input,select").val('');
    newElement.hide();
    uiSetMarkingOnChange(newElement.find('input,select'));

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


// function uiCountObjects(selector) {
//     return parseInt($(selector).length);
// }
// 
// function uiCountProfileObjects() {
//   
//   window.objectCounters = {
//       'additionalemail': uiCountObjects(".additional.emailaddresses"),
//       'phone': uiCountObjects(".additional.emailaddresses"),
//       'im': uiCountObjects(".additional.emailaddresses"),
//       'www': uiCountObjects(".additional.emailaddresses"),
//       'nickname': uiCountObjects(".additional.emailaddresses"),
//       'company': uiCountObjects(".additional.emailaddresses"),
//   };
//   
// }

function uiAddNewTableRow(prefix, removeAjax) {
  
    tableName = "#" + prefix + "stable"
    removerClass = prefix + "removers"
  
    originaltr = $(tableName + " > tbody > tr:first");
    tr = uiCloneElement(originaltr);
    
    // Remove the table label
    tr.find('.formlabels').remove();

    // Resize the table label
    uiChangeLabelHeight("#" + prefix + "label", +1)
    
    // Replace the add button with a remove button
    tr.find(".formbuttons").remove();
    tr.append("<td class='forminputs formbuttons'><span class='" + removerClass + " buttons clickable buttons-remove'></span></td>");

    // Show the new row
    $(tableName + "> tbody").append(tr);

    // Re-create the dropdown
    tr.find('.chosen-container').remove();
    tr.find('select').val(originaltr.find('select').val());
    uiMakeDropdowns(tr);
    
    uiAddRemoverHandler(tr.find('.' + prefix + 'removers'), prefix, removeAjax);
    
//     window.objectCounters[prefix]++;
    
//     tr.find("input").each(function() {
//       
//       e = $(this);
//       newID = e.attr("id").replace(/[0-9]+/g, "");
//       newID += window.objectCounters[prefix];
//       e.attr("id", newID);      
//       
//     });
    
    return tr;
}

function uiAddRemoverHandler(where, prefix, removeAjax) {
  
    $(where).click(function() {
        
        tr = $(this).closest("tr");
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
      
        mainInput = $(this).closest("tr").find("input[type=text]:first");
        if(mainInput.val() == "")
            return false;
            
        tr = uiAddNewTableRow(prefix, removeAjax);
        
        $(this).closest("tr").find("input,select").val("");  // clear them all!
        
        tr.show();
        
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

function uiAddOverlay() {
  
   $("body").append("<div id='overlay'></div>");

   $("#overlay").height($(document).height());
}

function uiShowDialogbox(messageText, options) {
  
    uiAddOverlay();
    $("#overlay").append("<div id='dialogbox'></div>");
    $("#dialogbox").dialog(options);
    $("#dialogbox").html(messageText);
    $("#dialogbox").dialog("open");
}

function uiShowErrorMessage(messageText) {
      
    uiShowDialogbox(messageText, {
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
}

function uiShowYesNoMessage(messageText) {
      
    uiShowDialogbox(messageText, {
        autoOpen: false,
        modal: true,
        dialogClass: "no-close",
        width: 500,
        buttons: {
          "Yes": function() {
              $(this).dialog("close");
              $("#overlay").remove();
              return true;
          },
          "No": function() {
              $(this).dialog("close");
              $("#overlay").remove();
              return false;
          }
        },
        title: 'Warning'
    });    
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

function uiStartLogoAnimation() {
  
    if($("#overlay").length == 0) {
      
        uiAddOverlay();
        
        $("#overlay").append("<div id='animatedlogo'><img src='/images/logo_01.png' alt='Psinque logo' /></div>");
        $("#animatedlogo").position({
            my: "center",
            at: "center",
            of: window
        });
    }
}

function uiStopLogoAnimation() {
    window.unsavedChanges = false;  // well... it's not pretty, but it works
    $("#overlay").remove();
    removeElementWithEffects($("#firstlogin"));
}

function uiMarkChangedFields(where) {
  
    window.unsavedChanges = true;
  
    elem = $(where);
    if(elem.is('input')) {
        elem.addClass("unsavedchanges");
    } else if(elem.is('select')) {
        elem.addClass("unsavedchanges");
        elem.next().find("a").css("color", "#e35c33");
    } else {
        elem.find("input,select,label").addClass("unsavedchanges");
    } 
}

function uiUnmarkChangedFields(where) {
    elem = $(where);
    if(elem.is('input')) {
        elem.removeClass("unsavedchanges");
    } else if(elem.is('select')) {
        elem.removeClass("unsavedchanges");
        elem.next().find("a").css("color", "");
    } else {
        elem.find("input,select,label").removeClass("unsavedchanges");
    }
}

function unmarkAllFields() {
    uiUnmarkChangedFields(document);
}

function uiSetMarkingOnChange(where) {
    elem = $(where);
    elem.change(function() {
        uiMarkChangedFields(this);
    }).keyup(function() {
        if($(this).is("input") && ($(this).attr("type") == "text"))
            uiMarkChangedFields(this);
    });
}

function uiMakeDropdowns(where) {
  
    $(where).find('select').each(function() {
      
        select = $(this);
      
        chosenOptions = {
            width: "100%",
            disable_search: false,
        }
        
        if(select.hasClass("nosearch"))
            chosenOptions.disable_search = true;
        
        if(select.hasClass("shortbox"))
            chosenOptions.width = "80px";
        
        if(select.hasClass("mediumbox"))
            chosenOptions.width = "160px";
        
        if(select.hasClass("bigbox"))
            chosenOptions.width = "240px";
                
        select.chosen(chosenOptions).change(function() {
          
            select = $(this);
            if(select.hasClass("countries")) {
                select.next().find("a > span").html(select.val());
            }
            uiMarkChangedFields(select);
        });
        
        if(select.hasClass("countries"))
            select.next().find("a > span").html(select.val());
    });
}

function uiValidateEmail(emailValue) {
  
    var atpos = emailValue.indexOf("@");
    var dotpos = emailValue.lastIndexOf(".");
    return !(atpos < 1 || dotpos < atpos+2 || dotpos+2 >= emailValue.length);
}

function uiValidateTextInputs(selector, message) {
  
    fieldsCorrect = true;
  
    $(selector).each(function() {
      
        e = $(this);
      
        if(e.val() == "") {
      
            uiShowErrorMessage(message);
            fieldsCorrect = false;
        }
    });
  
    return fieldsCorrect;
}

function uiValidateEmails(selector) {
  
    fieldsCorrect = true;
  
    $(selector).each(function() {
      
        e = $(this);
        
        if(e.hasClass("emailaddresses")) {
            if(e.val() == "") {  
                uiShowErrorMessage("Email address cannot be empty.");
                fieldsCorrect = false;
            } else if(!uiValidateEmail(e.val())) {
                uiShowErrorMessage("Invalid email address: " + e.val());
                fieldsCorrect = false;
            }
        }
    });
  
    return fieldsCorrect;
}

$(document).ready(function() {
  
    uiMakeDropdowns("body");
  
    uiSetMarkingOnChange("input,select");
    uiInitializeCheckboxes();

    window.ajaxInProgress = false;
    window.unsavedChanges = false;
    
    $(window).bind('beforeunload', function(e) {
      
        if(window.ajaxInProgress) {
            return "An AJAX query is in progress. Are you sure you want to exit?";
        } else if(window.unsavedChanges) {
            return "There are unsaved changes on the webpage. Are you sure you want to exit?";
        } else
            return;
    });
    
    $("#content").animate({top: "0"}, { duration: 1000 });
    
});
