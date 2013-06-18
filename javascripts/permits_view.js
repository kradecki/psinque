
window.ajaxCounter = 0;

updatePermit = function(permitContent) {

    startLogoAnimation();
    
    permitKey = permitContent.find(".keys").val();
    permitNr  = permitContent.find(".indices").val();
    
    // Count the number of AJAX queries
    window.ajaxCounter++;
    permitContent.find("input").each(function(dupa) {
        if(($(this).attr("type") == "checkbox") &&
           (!$(this).hasClass("general"))) {
                window.ajaxCounter++;
        }
    });
    
    // Update the general permits
    canViewFirstNames = $("#firstnames" + permitNr).is(':checked');
    canViewLastNames = $("#lastnames" + permitNr).is(':checked');
    canViewBirthday = $("#birthday" + permitNr).is(':checked');
    canViewGender = $("#gender" + permitNr).is(':checked');
    executeAJAX("/permits/setgeneralpermit?key=" + permitKey +
                                "&firstnames=" + canViewFirstNames +
                                "&lastnames=" + canViewLastNames +
                                "&birthday=" + canViewBirthday +
                                "&gender=" + canViewGender,
        function() {
            window.ajaxCounter--;
        });
    
    // Update all the other permits
    permitContent.find("input").each(function() {
        if($(this).attr("type") == "checkbox") {
            if($(this).attr("class") == "email") {
                executeAJAX("/permits/setemailpermit?key=" + $(this).attr("name") +
                                "&canview=" + $(this).is(':checked'),
                    function() {
                        window.ajaxCounter--;
                        if(window.ajaxCounter == 0) {
                            stopLogoAnimation();
                        }
                    });
            }
        }
    });
}

addPermit = function(permits) {
    permitName = $("#permitname").val();
    if(permitName != "") {
        executeAJAX("/permits/addpermit?name=" + permitName,
            function(parsedJSON) {
                $("<h3><img src='/images/private.png'> " + permitName + "</h3>").insertBefore($("#newpermit"));
                newPermit = $(".tableform:first").clone();
                newPermit.hide();
                newPermit.insertBefore($("#newpermit"));
                newPermit.find(".keys").val(parsedJSON["key"]);
                newPermit.find(".indices").val($(".permits").length);
//                 newPermit.find("h3").html(permitName);
                newPermit.find("input[type=checkbox]").each(function() {
                    if($(this).hasClass("names")) {
                        $(this).prop('checked', true);
                    } else {
                        $(this).prop('checked', false);
                    }
                });
                
                if(newPermit.find(".removebuttons").length == 0) {
                    newPermit.find("p").append('<input type="button" class="removeButtons" value="Remove">');
                }
                
                newPermit.find(".updateButtons").click(function() {
                    updatePermit($(this).parent());
                });

                newPermit.find(".removeButtons").click(function() {
                    removePermit($(this).parent().parent().parent());
                });

                newPermit.slideDown();
                
                recreateAccordeon();
                stopLogoAnimation();
            });
    } else {
        alert("Permit name cannot be empty!");
    } 
}

removePermit = function(removedPermit) {
    
    startLogoAnimation();
    
    permitKey = removedPermit.find(".keys").val();

    executeAJAX("/permits/removepermit?key=" + permitKey,
        function() {
            removedPermit.slideUp(function() {
                removedPermit.prev().remove();
                removedPermit.remove();
                recreateAccordeon();
                stopLogoAnimation();
            });
        });
}

recreateAccordeon = function() {
//     window.permitAccordeon.destroy();
//     window.permitAccordeon = $("#permitlist").accordion();
    $("#permitlist").accordion('destroy').accordion();
}

$(document).ready(function() {

    $(".submitbuttons").click(function() {
        updatePermit($(this).closest(".tableform"));
        return false;
    });
    
    $(".removeButtons").click(function() {
        removePermit($(this).closest(".tableform"));
        return false;
    });
    
    $("#createbutton").click(function() {
        startLogoAnimation();
        addPermit($(this).parent());
        return false;
    });
    
    // jQuery UI
    window.permitAccordeon = $("#permitlist").accordion();
    
});
