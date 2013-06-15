
displayMessage = function(msg) {
    newElement = $('<span id="message"> ' + msg + '</span>');
    newElement.hide();
    newElement.insertAfter('#search');
    newElement.fadeIn();
}

$(document).ready(function() {
    
    $("#search").click(function() {
        
        // Remove any previous search results
        if($('#message').length > 0)
            $("#message").remove();
        
        $.ajax("/psinques/searchemail?email=" + $("#email").val()).done(function(data) {

            jsonResults = $.parseJSON(data)
            statusCode = jsonResults["status"];
            if(statusCode == 0) {
                
                userKey = jsonResults["key"];
                displayMessage('<span id="message">Add psinque: <a href="/psinques/addpublic?key=' + userKey + '">public</a> | <a href="" id="addPrivate">private (requires authorization)</a></span>');

                $("#addPrivate").click(function() {
                    
                    $.ajax("/psinques/addprivate?key=" + userKey)
                        .done(function(data) {
                            $("#message").remove();
                            addStatusCode = $.parseJSON(data)["status"];
                            if(addStatusCode == 0) {
                                displayMessage('Psinque request sent');
                            } else {
                                displayMessage('Unknown error (' + addStatusCode + ')');
                            }
                        })
                        .error(function(data) {
                            $("#message").remove();
                            displayMessage('Server error')
                        });
                    
                    return false;
                });   
            }
            
            else if(statusCode == 1) {
                displayMessage(jsonResults["message"]);
            }
            
            else {
                displayMessage('User not found.');                
            }
        });
        
        return false;
    });
    
    
    $(".Removers").click(function() {
        
        contactKey = $(this).parent().find(".ContactKeys").val();
        executeAJAX("/psinques/removecontact?key=" + contactKey,
            function() {
                location.reload();
            }
        );
        
        return false;
        
    });
    

    $(".requesters").click(function() {
        
        contactKey = $(this).parent().find(".ContactKeys").val();
        executeAJAX("/psinques/requestupgrade?key=" + contactKey,
            function() {
                window.alert("Request sent");
            }
        );
        
        return false;
        
    });
    
    
    $(".privateadders").click(function() {
        
        contactKey = $(this).parent().find(".ContactKeys").val();
        executeAJAX("/psinques/addprivate?key=" + contactKey,
            function() {
                window.alert("Request sent");
            }
        );
        
        return false;
        
    });
    
    
    $(".Accepters").click(function() {
        
        psinqueKey = $(this).parent().find(".PsinqueKeys").val();
        
        executeAJAX("/psinques/acceptrequest?key=" + psinqueKey,
            function() {
                location.reload();
            }
        );
        
        return false;
    });

    
    $(".Rejecters").click(function() {
        
        psinqueKey = $(this).parent().find(".PsinqueKeys").val();
        
        executeAJAX("/psinques/rejectrequest?key=" + psinqueKey,
            function() {
                location.reload();
            }
        );
        
        return false;
    });

});
