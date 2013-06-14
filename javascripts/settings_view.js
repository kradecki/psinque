
$(document).ready(function() {

    if(!$("#synccarddav").is(':checked')) {
        $("#carddavlogins").hide();
    }
    
    $("input,label").change(function() {
        markChangedFields($(this));
    });
    
    $("#synccarddav").click(function() {
        if($(this).is(':checked')) {
            console.log("checked");
            showElementWithEffects($("#carddavlogins"));
        } else {
            console.log("unchecked");
            hideElementWithEffects($("#carddavlogins"));
        }
        
    });
        
    $("#generatecarddav").click(function() {
        
        parent = $(this).parent().parent();
        cardDAVName = $("#newcarddavname").val();
        if(cardDAVName == "") {
            window.alert("You need to name your device.");
        } else {   
            executeAJAX("/settings/generatecarddavlogin?name=" + cardDAVName,
                function(parsedJSON) {
                    parent.find(".tableforminputs").append("</br>" +
                        "<p>New CardDAV login:</br>Username: " + 
                        parsedJSON.username + "</br>Password: " +
                        parsedJSON.password + "</p>");
                });
        }       
        
        return false;
    });
        
    $(".removecarddav").click(function() {
        
        cardDAVInfo = $(this).parent().parent();
        cardDAVKey = cardDAVInfo.find("td > label > .carddavkeys").val();
        
        executeAJAX("/settings/deletecarddav?key=" + cardDAVKey,
            function() {
                labelCell = $("#carddavlogins > tbody > tr > .tableformlabels")
                loginCount = parseInt(labelCell.attr('rowspan'));
                labelCell.attr('rowspan', loginCount - 1);
                removeElementWithEffects(cardDAVInfo);
            });
        
        return false;
    });
    
    $("#submitbutton").click(function() {
        startLogoAnimation();
        executeAJAX("/settings/updatesettings" + 
                "?emailnotifications=" + $("#emailnotifications").is(":checked") +
                "&language=" + $("#language").val() +
                "&synccarddav=" + $("#synccarddav").is(":checked") +
                "&newsletter=" + $("#newsletter").is(":checked"),
            function() {
                stopLogoAnimation();           
            });

        return false;
    });
});
