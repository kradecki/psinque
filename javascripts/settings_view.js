
$(document).ready(function() {
    
    $("#synccarddav").click(function() {
        
        if($(this).is(':checked')) {
            $("#carddavLogins").each(function() {
                $(this).attr("diabled", "disabled");
            });
        } else {
            $("#carddavLogins").each(function() {
                $(this).removeAttr("diabled");
            });
        }
        
    });
        
    $("#generateCardDAV").click(function() {
        
        $(".newCardDAVLogin").remove();
        
        cardDAVName = $("#newCardDAVName").val()
        
        executeAJAX("/settings/generatecarddavlogin?name=" + cardDAVName,
            function(parsedJSON) {
                $("#carddavLogins").append("<p class='newCardDAVLogin'>New CardDAV login:</br>Username: " + 
                    parsedJSON.username + "</br>Password: " +
                    parsedJSON.password + "</p>");
            });
        
    });
        
    $(".RemoveCardDAV").click(function() {
        
        cardDAVInfo = $(this).parent();
        cardDAVKey = cardDAVInfo.find(".CardDAVkeys").val();
        
        executeAJAX("/settings/deletecarddav?key=" + cardDAVKey,
            function() {
                cardDAVInfo.slideUp(function() {
                    cardDAVInfo.remove();
                });
            });
    });
    
    $("#saveButton").click(function() {
        
        theWholeForm = $(this).parent();
        executeAJAX("/settings/updatesettings" + 
            "?emailnotifications=" + $("#emailNotifications").is(":checked") +
            "&language=" + $("#language").val() +
            "&synccarddav=" + $("#syncCardDAV").is(":checked") +
            "&newsletter=" + $("#newsletter").is(":checked"),
            function() {
                theWholeForm.find(".donemark").show();                
            });
    });
});
