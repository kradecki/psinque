
$(document).ready(function() {
    $("#search").click(function() {
        
        // Remove any previous search results
        if($('#addProfile').length > 0)
            $("#addProfile").remove();
        
        $.ajax("/searchemail?email=" + $("#email").val()).done(function(data) {
            
            jsonResults = $.parseJSON(data)
            if(jsonResults["status"] == 1) {
                
                fromUser = jsonResults["fromUser"];
                newElement = $('<a id="addProfile">Add profile: <a href="" id="addPublic">public</a> | <a href="" id="addPrivate">private (requires authorization)</a></a>');

                newElement.find("#addPublic").click(function() {
                    $.ajax("/addincoming?type=public&from=" + userKey).done(function(data) {
                        if($.parseJSON(data)["status"] == 1) {
                            $("#addProfile").remove();
                        }
                    });

                newElement.find("#addPrivate").click(function() {
                    $.ajax("/addincoming?type=private&from=" + userKey).done(function(data) {
                        if($.parseJSON(data)["status"] == 1) {
                            $("#addProfile").remove();
                        }
                    });
                });
                
                newElement.hide();
                newElement.insertAfter('.inner');
                newElement.fadeIn();
                
            } else {
                
                newElement = $('<a id="addProfile">User not found.</a>')
                newElement.hide();
                newElement.insertAfter('.inner');
                newElement.fadeIn();
                
            }
        });
        return false;
    });
});
