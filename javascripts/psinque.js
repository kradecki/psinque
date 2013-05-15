
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
