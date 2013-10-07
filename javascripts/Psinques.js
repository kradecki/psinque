
function addSearchHandler(where) {
    
    $(where).click(function() {
      
        if(!uiValidateEmails("#email"))
            return false;
                
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

            addRequestPrivateHandler(newContact.find(".contactupgraders"));
            addRemoveContactHandler(newContact.find(".contactremovers"));

            showElementWithEffects(newContact);
            
        });
    });
}

function addExpandContactHandler(where) {
  
  $(where).click(function() {
    
      contactDetails = $(this).parent().next();
      if(contactDetails.is(":visible")) {
          hideElementWithEffects(contactDetails);
      } else {
          showElementWithEffects(contactDetails);
      }
  });
}

function addRequestPrivateHandler(where) {
    
    $(where).click(function() {
        
        contactBox = $(this).closest(".contacts");
        contactKey = contactBox.find(".contactkeys").val();
        
        psinqueRequestPrivate(contactKey, function() {
            requestButton = contactBox.find(".contactupgraders");
            requestButton.removeClass("contactupgraders clickable");
            requestButton.find("img").attr("src", "/images/button_pending.png");
        });
    });
}

function addRemoveContactHandler(where) {
    
    $(where).click(function() {
      
        contactBox = $(this).closest(".contacts");
        contactKey = contactBox.find(".contactkeys").val();
        
        psinqueRemoveContact(contactKey, function() {
            removeElementWithEffects(contactBox);
        });
    });
}

function addAcceptRequestHandler(where) {
    
    $(where).click(function() {
      
        notification = $(this).closest(".notifications");
        notificationKey = notification.find(".notificationkeys").val();
        
        psinqueAcceptRequest(notificationKey, function() {
            uiRemoveTableRow(notification, "notification");
        });
    });
}

function addRejectRequestHandler(where) {
    
    $(where).click(function() {
      
        notification = $(this).closest(".notifications");
        notificationKey = notification.find(".notificationkeys").val();
        
        psinqueRejectRequest(notificationKey, function() {
            uiRemoveTableRow(notification, "notification");
        });
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
    
    addRequestPrivateHandler(".contactupgraders");
    addRemoveContactHandler(".contactremovers");
    
    addAcceptRequestHandler(".accepters");
    addRejectRequestHandler(".rejecters");

    // React to the Enter key
    uiAddEnterAction("input[type=text]", "#searchbutton");
    
    $(".permitselects").change(function() {
        console.log("DUpa!");
    });
    
});

