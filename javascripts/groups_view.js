
updateGroup = function(permissions, newGroup, groupKey) {
    window.permissionCount = 0;
    permissions.find("input").each(function(dupa) {
        thisInput = $(this);
        if(thisInput.attr("type") == "checkbox") {
            window.permissionCount++;
            $.ajax("/groups/setpermission?key=" + groupKey +
                                        "&type=" + thisInput.attr("class") +
                                        "&name=" + thisInput.attr("name") +
                                        "&value=" + thisInput.val())
                .done(function(data) {
                    console.log(data);
                    parsedJSON = $.parseJSON(data);
                    if(parsedJSON["status"] != 0) {
                        alert("Error setting permission: " + parsedJSON["message"]);
                    }
                    window.permissionCount--;
                    if((window.permissionCount == 0) && (newGroup)) {  // all permissions are set
                        document.location.reload(true);   // refresh the list of groups
                    }
                })
                .error(function(data) {
                    alert("Uknown error occured while setting permission.");
                });
        }
    });
}

addAndUpdateGroup = function(permissions) {
    groupName = permissions.find("#groupName").val();
    if(groupName != "") {
        $.ajax("/groups/addgroup?name=" + groupName)
            .done(function(data) {
                parsedJSON = $.parseJSON(data);
                if(parsedJSON["status"] != 0) {
                    alert("Error creating group: " + parsedJSON["message"]);
                } else {
                    updateGroup(permissions, true, parsedJSON["key"]);
                }
            })
            .error(function() {
                alert("Error while creating group.");
            });
    } else {
        alert("Group name cannot be empty!");
    } 
}

$(document).ready(function() {
    
    $(".updateButtons").click(function() {
        parentNode = $(this).parent();
        updateGroup(parentNode, false, parentNode.attr("id"));
    });
    
    $(".removeButtons").click(function() {
        groupKey = $(this).parent().attr("id");
        $.ajax("/groups/removegroup?key=" + groupKey)
            .done(function(data) {
                parsedJSON = $.parseJSON(data);
                addStatusCode = parsedJSON["status"];
                if(addStatusCode == 0) {
                    parentNode = $("#" + groupKey).parent();
                    parentNode.slideUp(function() {
                        parentNode.remove();
                    });
                } else {
                    alert("Error: " + parsedJSON["message"]);
                }
            })
            .error(function(data) {
                alert("There was an error.");
            });
    });
    
    $("#createButton").click(function() {
        $(this).parent().find(".spinner").show();
        addAndUpdateGroup($(this).parent());
    });
    
});
