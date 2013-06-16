
window.ajaxCounter = 0;

updatePermit = function(permitContent) {

    startLogoAnimation();
    
    permitKey = permitContent.find(".keys").val();
    permitNr  = permitContent.find(".indices").val();
    
    // Count the number of AJAX queries
    window.ajaxCounter++;
    permitContent.find("input").each(function(dupa) {
        if(($(this).attr("type") == "checkbox") &&
           ($(this).attr("class") != "general")) {
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
    permitName = permits.find("#permitName").val();
    if(permitName != "") {
        executeAJAX("/permits/addpermit?name=" + permitName,
            function() {
                lastPermit = $("#searchContacts:last").parent();
                newPermit = lastPermit.clone();
                newPermit.hide();
                newPermit.insertBefore($("#addPermitForm"));
                newPermit.find(".keys").val(parsedJSON["key"]);
                newPermit.find("legend").html(permitName);
                newPermit.find("input[type=checkbox]").each(function() {
                    if($(this).attr("id") != "canViewName") {
                        $(this).prop('checked', false);
                    } else {
                        $(this).prop('checked', true);
                    }
                });
                
                if(newPermit.find(".removeButtons").length == 0) {
                    newPermit.find("p").append('<input type="button" class="removeButtons" value="Remove">');
                }
                
                newPermit.find(".updateButtons").click(function() {
                    updatePermit($(this).parent());
                });

                newPermit.find(".removeButtons").click(function() {
                    removePermit($(this).parent().parent().parent());
                });

                newPermit.slideDown();
            });
    } else {
        alert("Permit name cannot be empty!");
    } 
}

removePermit = function(removedPermit) {
    removedPermit.find(".spinner").show();
    permitKey = removedPermit.find(".keys").val();
    executeAJAX("/permits/removepermit?key=" + permitKey,
        function() {
            removedPermit.slideUp(function() {
                removedPermit.remove();
            });
        });
}

$(document).ready(function() {

    $(".submitbuttons").click(function() {
        updatePermit($(this).closest(".tableform"));
        return false;
    });
    
    $(".removeButtons").click(function() {
        removePermit($(this).parent().parent().parent());
        return false;
    });
    
    $("#createbutton").click(function() {
        $(this).parent().find(".spinner").show();
        addPermit($(this).parent());
        return false;
    });
    
    // jQuery UI
    $("#permitlist").accordion();
    
});
