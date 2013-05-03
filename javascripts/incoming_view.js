
$(document).ready(function() {
    
    $("#search").click(function() {
        
        // Remove any previous search results
        if($('#addProfile').length > 0)
            $("#addProfile").remove();
        
        $.ajax("/searchemail?email=" + $("#email").val()).done(function(data) {

            jsonResults = $.parseJSON(data)
            if(jsonResults["status"] == 1) {
                
                userKey = jsonResults["fromUser"];
                console.log(userKey);
                newElement = $('<span id="addProfile"> Add profile: <a href="/addincoming?type=public&from=' + userKey + '">public</a> | <a href="" id="addPrivate">private (requires authorization)</a></span>');

                newElement.find("#addPrivate").click(function() {
                    
                    $.ajax("/addincoming?type=private&from=" + userKey).done(function(data) {
                        if($.parseJSON(data)["status"] == 1) {
                            $("#addProfile").remove();
                        }
                        
                    });
                    
                    return false;
                });
                
                newElement.hide();
                newElement.insertAfter('#search');
                newElement.fadeIn();
                
            } else {

                newElement = $('<span id="addProfile"> User not found.</span>')
                newElement.hide();
                newElement.insertAfter('#search');
                newElement.fadeIn();
                
            }
        });
        
        return false;
    });
});
