
function cardDAVHTML(key, name) {
    return "<tr class='carddavlogins'> \
              <td class='forminputs'> \
                  <input type='hidden' class='carddavkeys' value='" + key + "'> \
                  <label class='carddavnames'>" + name + "</label> \
              </td> \
              <td class='forminputs formbuttons'> \
                  <span class='buttons clickable carddavremovers'> \
                    <img src='/images/button_remove.png' /> \
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

                uiChangeLabelHeight("#carddavlabel", +1);
                newRow = $(cardDAVHTML(data.key, cardDAVName))
                newRow.insertBefore(".newcarddav");
                console.log(newRow);
                addRemoveCardDAVHandler(newRow.find(".carddavremovers"));
                
                // Clear the new CardDAV name input 
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
        
        tr = $(this).parent().parent();

        cardDAVKey = tr.find(".carddavkeys").val();
        
        psinqueDeleteCardDAVLogin(cardDAVKey, function() {
            window.cardDAVCounter--;
            uiRemoveTableRow(tr, "carddav");
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
                unmarkChangedFields("#settings");
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
        markChangedFields($(this).parent().parent().next().children());
    });
    
    // Hiding the CardDAV logins
    $("#synccarddav").click(function() {
        console.log("Click");
        if($(this).is(':checked')) {
            showElementWithEffects($("#carddav"));
        } else {
            hideElementWithEffects($("#carddav"));
        }
    });
    
    // Hiding the individual email notifications
    if(!$("#emailnotifications").is(":checked"))
      $(".individualnotifications").hide();
    
    $("#emailnotifications").click(function() {
        if($(this).is(":checked")) {
            showElementWithEffects($(".individualnotifications"));
        } else {
            hideElementWithEffects($(".individualnotifications"));
        }
    });

    addGenerateCardDAVHandler("#createcarddav");
    addRemoveCardDAVHandler(".carddavremovers");
    addSaveSettingsHandler("#savebutton");
    
    // React to pressing the Enter key
    uiAddEnterAction("#newcarddavname", "#createcarddav")

});
