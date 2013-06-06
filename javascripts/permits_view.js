
updatePermit = function(permits) {

    permitKey = permits.find(".keys").val()
    permits.find(".spinner").show();
    
    // Count the number of AJAX queries
    window.permitCount = 1;
    permits.find("input").each(function(dupa) {
        if(($(this).attr("type") == "checkbox") &&
           ($(this).attr("class") != "general")) {
                window.permitCount++;
        }
    });
    
    // Update the general permits
    canViewName = permits.find("#canViewName").is(':checked');
    canViewBirthday = permits.find("#canViewBirthday").is(':checked');
    canViewGender = permits.find("#canViewGender").is(':checked');
    executeAJAX("/permits/setgeneralpermit?key=" + permitKey +
                                "&canViewName=" + canViewName +
                                "&canViewBirthday=" + canViewBirthday +
                                "&canViewGender=" + canViewGender,
        function() {
            window.permitCount--;
        });
    
    // Update all the other permits
    permits.find("input").each(function() {
        if($(this).attr("type") == "checkbox") {
            if($(this).attr("class") == "email") {
                executeAJAX("/permits/setemailpermit?key=" + $(this).attr("name") +
                                "&canView=" + $(this).is(':checked'),
                    function() {
                        window.permitCount--;
                        if(window.permitCount == 0) {
                            permits.find(".donemark").show();
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

    // Use jQueryUI style for buttons
    $("input[type=button]")
        .button()
        .click(function(event) {
            event.preventDefault();
        });

    $(".updateButtons").click(function() {
        updatePermit($(this).parent());
    });
    
    $(".removeButtons").click(function() {
        removePermit($(this).parent().parent().parent());
    });
    
    $("#createButton").click(function() {
        $(this).parent().find(".spinner").show();
        addPermit($(this).parent());
    });
    
});
