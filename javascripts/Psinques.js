
function addSearchHandler(where) {
    
    $(where).click(function() {
                
        psinqueSearchEmail($("#email").val(), function(jsonResults) {
            
            // Remove any previous results
            $("#searchresults").remove();

            // Insert the result element into the document
            attachedElement = window.searchResults.appendTo("#searchtable > tbody");
            
            // Copy the display name
            attachedElement.find("#searchresult").html(jsonResults["displayName"])
            
            // Copy the key
            attachedElement.find(".friendsprofilekeys").val(jsonResults["key"]);
            
            // Add a handler for the add button
            addAddContactHandler(attachedElement.find("#addcontact"));
            
            // Slide down the results (using the div workaround)
            attachedElement.find("div").slideDown();

        });
        
        return false;
    });
}

function addAddContactHandler(where) {
    
    $(where).click(function() {
        
        friendsProfileKey = $(this).parent().parent().prev().find(".friendsprofilekeys").val();
        
        psinqueAddPublicPsinque(friendsProfileKey, function(data) {
            
            $("#searchresults").remove();
            
            newContact = $($.trim(data));
            newContact.hide();
            newContact.prependTo("#contactlist");

            addRequestPrivateHandler(newContact.find(".button_publiccontact"));
            addRemoveContactHandler(newContact.find(".button_removecontact"));

            newContact.slideDown();
            
        });
    });
}

function addExpandContactHandler(where) {
  
  $(where).click(function() {
    
    contactDetails = $(this).parent().next();
    if(contactDetails.is(":visible")) {
        contactDetails.slideUp();
    } else {
        contactDetails.slideDown();
    }
  });
}

function addRequestPrivateHandler(where) {
    
    $(where).click(function() {
        
    });
}

function addRemoveContactHandler(where) {
    
    $(where).click(function() {
        
    });
}

function detachFromDocument(what) {
    detachedElement = $(what).clone();
    $(what).remove();
    return detachedElement;
}

$(document).ready(function() {
    
    // Searching for emails
    window.searchResults = detachFromDocument("#searchresults");
    addSearchHandler("#searchbutton");
    
    addExpandContactHandler(".contactnames");
    
    addRequestPrivateHandler(".button_publiccontact");
    addRemoveContactHandler(".button_removecontact");
    
});
