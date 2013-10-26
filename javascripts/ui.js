
function uiCloneElement(oldElement) {
    
    newElement = oldElement.clone();  // clone an existing address field group

    // Clean all the input values:
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
            $(labelid).parent().prependTo(tr.next());
        }
        uiChangeLabelHeight(labelid, -1);
        tr.remove();
    });
    
}

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
      
        mainTr = $(this).closest("tr");
        mainInput = mainTr.find("input[type=text]:first");
        if(mainInput.val() == "")
            return false;
        
        uiUnmarkChangedFields(mainTr);
            
        tr = uiAddNewTableRow(prefix, removeAjax);
        
        $(this).closest("tr").find("input,select").val("");  // clear them all!
        uiMarkChangedFields(tr);
        
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
    $("#overlay").remove();
    removeElementWithEffects($("#firstlogin"));
}

function uiMarkChangedFields(where) {
    elem = $(where);
    if(elem.is('input,select,label')) {
        elem.addClass("unsavedchanges");
    } else {
        elem.find('input,select,label').addClass("unsavedchanges");
    }
}

function uiUnmarkChangedFields(where) {
    elem = $(where);
    if(elem.is('input,select,label')) {
        elem.removeClass("unsavedchanges");
    } else {
        elem.find('input,select,label').removeClass("unsavedchanges");
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
            
            if((!select.hasClass("nicknames")) && (!select.hasClass("companies")) && (!select.hasClass("personaselects")))
                select.next().find("a > span").html(select.val());
            
            uiMarkChangedFields(select);
        });
        
        if((!select.hasClass("nicknames")) && (!select.hasClass("companies")) && (!select.hasClass("personaselects")))
            select.next().find("a > span").html(select.val());
    });
}


function uiValidateEmail(emailValue) {
  
    var atpos = emailValue.indexOf("@");
    var dotpos = emailValue.lastIndexOf(".");
    return !(atpos < 1 || dotpos < atpos+2 || dotpos+2 >= emailValue.length);
}


function uiValidateDate(year, month, day) {
    
    var dayobj = new Date(year, month, day);
    return ((dayobj.getMonth() == month) && (dayobj.getDate() == day) && (dayobj.getFullYear() == year))
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
  
    uiSetMarkingOnChange("input[type=text],input[type=checkbox],select");
    uiInitializeCheckboxes();

    window.ajaxInProgress = false;
    
    $(window).bind('beforeunload', function(e) {
        
        if(window.ajaxInProgress) {
            return "An AJAX query is in progress. Are you sure you want to exit?";
        } else if($(".unsavedchanges").length > 0) {
            return "There are unsaved changes on the webpage. Are you sure you want to exit?";
        } else
            return;
    });
    
    $("#content").animate({top: "0"}, { duration: 1000 });
    
});
