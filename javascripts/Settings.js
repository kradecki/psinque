
function changeLabelHeight(where, howMuch) {
    tableLabel = $(where);
    currentHeight = parseInt(tableLabel.attr("rowspan"));
    tableLabel.attr("rowspan", currentHeight + howMuch);
}

function cardDAVHTML(key, name) {
    return "<tr class='carddavlogins'> \
        <td class='forminputs'> \
            <input type='hidden' class='carddavkeys' value='" + key + "'> \
            <label class='carddavnames'>" + name + "</label> \
        </td> \
        <td class='forminputs formbuttons'> \
            <span class='buttons clickable' class='carddavremovers'> \
              <img src='/images/squareicons/remove.png' /> \
            </span> \
        </td> \
      </tr>"
}

function addGenerateCardDAVHandler(where) {

    $(where).click(function() {
        
        parent = $(this).parent().parent();
        cardDAVName = $("#newcarddavname").val();
        
        if(cardDAVName == "") {

            window.alert("You need to name your device.");

        } else {

            psinqueGenerateCardDAVLogin(cardDAVName, function(data) {
                
                window.cardDAVCounter++;
                
                cardDAVLogin = $("#carddavlogin");
                cardDAVLogin.html("<b>Username</b>: " + data.username +
                             "</br><b>Password</b>: " + data.password);
                showElementWithEffects(cardDAVLogin.parent());

                changeLabelHeight("#carddavlabel", +1);
                newRow = $(cardDAVHTML(data.key, cardDAVName))
                newRow.insertBefore("#newcarddav");
                addRemoveCardDAVHandler(newRow.find(".carddavremovers"));
                
                $("#newcarddavname").val("");

                if(window.cardDAVCounter == 1) {
                    $("#carddavlabel").prependTo(newRow);
                }
                
            });
        }       
        
        return false;
    });
}

function addRemoveCardDAVHandler(where) {
    
    $(where).click(function() {
        
        console.log("Click");
        cardDAVInfo = $(this).parent().parent();
        cardDAVKey = cardDAVInfo.find(".carddavkeys").val();
        
        psinqueDeleteCardDAVLogin(cardDAVKey, function() {

            window.cardDAVCounter--;
            
            changeLabelHeight("#carddavlabel", -1);
            if(window.cardDAVCounter == 0) {
                $("carddavlabel").prependTo("#newcarddav");
            }

            labelCell = $("#carddav > tbody > tr > .tableformlabels")
            loginCount = parseInt(labelCell.attr('rowspan'));
            labelCell.attr('rowspan', loginCount - 1);
            removeElementWithEffects(cardDAVInfo);
            
        });
        
        return false;
    });
}

function addSaveSettingsHandler(where) {
    
    $(where).click(function() {
        
        psinqueUpdateSettings($("#emailnotifications").is(":checked"),
                              $("#notifystops").is(":checked"),
                              $("#notifyasks").is(":checked"),
                              $("#notifyaccepts").is(":checked"),
                              $("#notifyrejects").is(":checked"),
                              $("#notifyrevokes").is(":checked"),
                              $("#language").val(),
                              $("#synccarddav").is(":checked"),
                              $("#newsletter").is(":checked"),
            function() {
                unmarkChangedFields("#tableform");
            });

        return false;
    });
}

$(document).ready(function() {
    
    window.cardDAVCounter = $(".carddavlogins").length;
    
    if(!$("#synccarddav").is(':checked')) {
        $("#carddav").hide();
    }
    
    $("input[type=checkbox]").change(function() {
        markChangedFields($(this).parent().parent().next());
    });
    
    $("#synccarddav").click(function() {
        if($(this).is(':checked')) {
            showElementWithEffects($("#carddav"));
        } else {
            hideElementWithEffects($("#carddav"));
        }
    });
        
    $("#emailnotifications").click(function() {
        if($(this).is(":checked")) {
            showElementWithEffects($(".individualnotifications"));
        } else {
            hideElementWithEffects($(".individualnotifications"));
        }
    });

    addGenerateCardDAVHandler("#addcarddav");
    addRemoveCardDAVHandler(".carddavremovers");
    addSaveSettingsHandler("#savebutton");
    
});
