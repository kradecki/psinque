
displayMessage = function(msg) {
    newElement = $('<span id="searchResult"> ' + msg + '</span>');
    newElement.hide();
    newElement.insertAfter('#search');
    newElement.fadeIn();
}

$(document).ready(function() {
    
    $("#search").click(function() {
        
        // Remove any previous search results
        if($('#searchResult').length > 0)
            $("#searchResult").remove();
        
        $.ajax("/incoming/searchemail?email=" + $("#email").val()).done(function(data) {

            jsonResults = $.parseJSON(data)
            statusCode = jsonResults["status"];
            if(statusCode == 0) {
                
                userKey = jsonResults["fromUser"];
                displayMessage('Add psinque: <a href="/incoming/addincoming?type=public&from=' + userKey + '">public</a> | <a href="" id="addPrivate">private (requires authorization)</a>');

                $("#addPrivate").click(function() {
                    
                    $.ajax("/incoming/addincoming?type=private&from=" + userKey)
                        .done(function(data) {
                            $("#searchResult").remove();
                            addStatusCode = $.parseJSON(data)["status"];
                            if(addStatusCode == 0) {
                                displayMessage('Psinque request sent');
                            } else {
                                displayMessage('Unknown error (' + addStatusCode + ')');
                            }
                        })
                        .error(function(data) {
                            $("#searchResult").remove();
                            displayMessage('Server error')
                        });
                    
                    return false;
                });   
            }
            
            else if(statusCode == 1) {
                displayMessage('Psinque already exists.');
            }
            
            else {
                displayMessage('User not found.');                
            }
        });
        
        return false;
    });
});
