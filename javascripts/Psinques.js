
function addSearchHandler(where) {
    
    $(where).click(function() {
      
        if(!uiValidateEmails("#email"))
            return false;
                
        // Remove any previous results
        $("#searchresults").remove();

        psinqueSearchEmail($("#email").val(), function(jsonResults) {

            // Insert the result element into the document
            attachedElement = window.searchResults.appendTo("#searchtable > tbody");
            
            if(jsonResults["found"]) {
          
                // Copy the display name
                attachedElement.find("#searchresult").html(jsonResults["displayName"])
                
                // Copy the key
                attachedElement.find(".friendsprofilekeys").val(jsonResults["key"]);
                
                // Add a handler for the add button
                attachedElement.find("#addcontact").attr("title", "Add to contacts.");
                addAddContactHandler(attachedElement.find("#addcontact"));
            } else {
                attachedElement.find("#searchresult").html("Email not registered. Send an invitation to join Psinque?")
                attachedElement.find("#addcontact").attr("title", "Invite to Psinque.");
            }
            
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

            addAllContactHandlers(newContact);
            uiMakeDropdowns(newContact);

            showElementWithEffects(newContact);
            
        });
    });
}

function addExpandContactHandler(where) {
  
  $(where).click(function() {
    
      contactDetails = $(this).parent().next();
      selectGroupPersona = $(this).parent().parent().next();
      if(contactDetails.is(":visible")) {
          hideElementWithEffects(contactDetails);
          hideElementWithEffects(selectGroupPersona);
      } else {
          showElementWithEffects(contactDetails);
          showElementWithEffects(selectGroupPersona);
      }
  });
}

function addRequestPrivateHandler(where) {
    
    $(where).click(function() {
        
        button = $(this);
        contactBox = button.closest(".contacts");
        contactKey = contactBox.find(".contactkeys").val();
        
        psinqueRequestPrivate(contactKey, function() {
            button.removeClass("contactupgraders clickable buttons-public");
            button.addClass("buttons-pending");
            button.attr("title", "Your request to access private data is pending");
        });
    });
}

function addRemoveContactHandler(where) {
    
    $(where).click(function() {
      
        contactBox = $(this).closest(".contacts");
        contactKey = contactBox.find(".contactkeys").val();
        
        psinqueRemoveContact(contactKey, function() {
            removeElementWithEffects(contactBox.next());
            removeElementWithEffects(contactBox);
        });
    });
}

function addIncomingActivateHandler(where) {
  
    $(where).click(function() {
      
        button = $(this);
        contactBox = button.closest(".contacts");
        contactKey = contactBox.find(".contactkeys").val();

        psinqueAddIncoming(contactKey, function(data) {
            button.removeClass("incominggetters clickable buttons-in-inactive");
            button.addClass("buttons-in-active");
            button.attr("title", "Incoming psinque is active");
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

function addGroupChangeHandler(where) {

    $(where).click(function() {
      
        button = $(this);
        tr = button.closest("tr");
        contactKey = button.closest("div.grouppersonaselects").prev().find(".contactkeys").val();
        groupKey = tr.find("select").val();
      
        psinqueChangeGroup(contactKey, groupKey, function() {
            uiUnmarkChangedFields(tr);
        });
    });

}

function addPersonaChangeHandler(where) {

    $(where).click(function() {
      
        button = $(this);
        tr = button.closest("tr");
        contactKey = button.closest("div.grouppersonaselects").prev().find(".contactkeys").val();
        personaKey = tr.find("select").val();
           
        psinqueChangePersona(contactKey, personaKey, function() {
            uiUnmarkChangedFields(tr);
        });
    });

}

function addNewPersonaHandler(where) {

    $(where).click(function() {
      
        input = $("#newgroupname");
        groupName = input.val();
        if(groupName == "")
            return;
      
        psinqueAddGroup(groupName, function(data) {
            
            input.val("");
            groupSelects = $("select.groupselects");
            groupSelects.append("<option value='" + data["key"] + "'>" + groupName + "</option>");
            
            // Recreate the 'chosen' dropdowns
            $("select").chosen("destroy");
            uiMakeDropdowns("body");
          
        });
    });

}

function addAllContactHandlers(where) {
  
    // Contact expand/contract
    addExpandContactHandler($(where).find(".contactnames"));

    // Contact operations
    addRequestPrivateHandler($(where).find(".contactupgraders"));
    addRemoveContactHandler($(where).find(".contactremovers"));    
    addIncomingActivateHandler($(where).find(".incominggetters"));

    // Notifications
    addAcceptRequestHandler($(where).find(".accepters"));
    addRejectRequestHandler($(where).find(".rejecters"));

    // Group and persona changing
    addGroupChangeHandler($(where).find(".groupchangers"));
    addPersonaChangeHandler($(where).find(".personachangers"));
}

function detachFromDocument(what) {
    detachedElement = $(what).clone();
    $(what).remove();
    return detachedElement;
}

$(document).ready(function() {

    addNewPersonaHandler("#addgroup");

    // Searching for emails
    window.searchResults = detachFromDocument("#searchresults");
    addSearchHandler("#searchbutton");
    
    // React to the Enter key
    $("input[type=text]").unbind('change');
    $("input[type=text]").unbind('keyup');
    uiAddEnterAction("input[type=text]", "#searchbutton");

    addAllContactHandlers(document);
    
});

