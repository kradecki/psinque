
executeAJAX = function(query, done) {
    $.ajax(query)
        .done(function(data) {
            parsedJSON = $.parseJSON(data);
            if(parsedJSON["status"] != 0) {
                alert("Error while performing operation: " + parsedJSON["message"]);
            } else {
                done();
            }
            $(".spinner").hide();
        })
        .error(function(data) {
            alert("Uknown error occured while performing operation.");
            $(".spinner").hide();
        });
}

updateGroup = function(permissions) {

    groupKey = permissions.find(".keys").val()
    permissions.find(".spinner").show();
    
    // Count the number of AJAX queries
    window.permissionCount = 1;
    permissions.find("input").each(function(dupa) {
        if(($(this).attr("type") == "checkbox") &&
           ($(this).attr("class") != "general")) {
                window.permissionCount++;
        }
    });
    
    // Update the general permissions
    canViewName = permissions.find("#canViewName").is(':checked');
    canViewBirthday = permissions.find("#canViewBirthday").is(':checked');
    canViewGender = permissions.find("#canViewGender").is(':checked');
    executeAJAX("/groups/setpermission?pkey=" + groupKey +
                                "&ptype=general" +
                                "&canViewName=" + canViewName +
                                "&canViewBirthday=" + canViewBirthday +
                                "&canViewGender=" + canViewGender,
        function() {
            window.permissionCount--;
        });
    
    // Update all the other permissions
    permissions.find("input").each(function() {
        if($(this).attr("type") == "checkbox") {
            if($(this).attr("class") == "email") {
                executeAJAX("/groups/setpermission?pkey=" + $(this).attr("name") +
                                "&ptype=" + $(this).attr("class") + 
                                "&canView=" + $(this).is(':checked'),
                    function() {
                        window.permissionCount--;
                        if(window.permissionCount == 0) {
                            permissions.find(".donemark").show();
                        }
                    });
            }
        }
    });
}

addGroup = function(permissions) {
    groupName = permissions.find("#groupName").val();
    if(groupName != "") {
        executeAJAX("/groups/addgroup?name=" + groupName,
            function() {
                lastGroup = $("#searchContacts:last").parent();
                newGroup = lastGroup.clone();
                newGroup.hide();
                newGroup.insertBefore($("#addGroupForm"));
                newGroup.find(".keys").val(parsedJSON["key"]);
                newGroup.find("legend").html(groupName);
                newGroup.find("input").each(function() {
                    if($(this).attr("type") != "button") {
                        if($(this).attr("id") != "canViewName") {
                            $(this).prop('checked', false);
                        } else {
                            $(this).prop('checked', true);
                        }
                    }
                });
                
                if(newGroup.find(".removeButtons").length == 0) {
                    newGroup.find("p").append('<input type="button" class="removeButtons" value="Remove">');
                }
                
                newGroup.find(".updateButtons").click(function() {
                    updateGroup($(this).parent());
                });

                newGroup.find(".removeButtons").click(function() {
                    removeGroup($(this).parent().parent().parent());
                });

                newGroup.slideDown();
            });
    } else {
        alert("Group name cannot be empty!");
    } 
}

removeGroup = function(removedGroup) {
    removedGroup.find(".spinner").show();
    groupKey = removedGroup.find(".keys").val();
    executeAJAX("/groups/removegroup?key=" + groupKey,
        function() {
            removedGroup.slideUp(function() {
                removedGroup.remove();
            });
        });
}

$(document).ready(function() {
    
    $(".updateButtons").click(function() {
        updateGroup($(this).parent());
    });
    
    $(".removeButtons").click(function() {
        removeGroup($(this).parent().parent().parent());
    });
    
    $("#createButton").click(function() {
        $(this).parent().find(".spinner").show();
        addGroup($(this).parent());
    });
    
});
