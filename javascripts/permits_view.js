
window.ajaxCounter = 0;

recreateAccordeon = function() {
    var active = $("#permitlist").accordion("option", "active");
    $("#permitlist").accordion('destroy').accordion({
        heightStyle: "content",
        active: active,
    });
}

function addRemovePermitHandler(where) {
    
    $(where).click(function() {
        
        if(window.ajaxCounter > 0)  // another query in progress
            return false;
        
        startLogoAnimation();
        window.ajaxCounter = 1;

        permitIndex = $(this).attr('data-psinque-index');
        permitKey = $("#permitkey" + permitIndex).val();
        permit = $("#permitform" + permitIndex);

        psinqueRemovePermit(permitKey, function() {
            permit.slideUp(function() {
                permit.prev().remove();
                permit.remove();
                recreateAccordeon();
                stopLogoAnimation();
                window.ajaxCounter = 0;
            });
        });
        
        return false;
    });
}

function addUpdatePermitHandler(where) {
    
    $(where).click(function(url) {
        
        if(window.ajaxCounter > 0)  // another query in progress
            return false;

        startLogoAnimation();

        permitIndex = $(this).attr('data-psinque-index');
        permitKey = $("#permitkey" + permitIndex).val();
        permitForm = $("#permitform" + permitIndex);
        
        // Count the number of AJAX queries
        window.ajaxCounter++;  // the general permit data
        permitForm.find("input").each(function() {
            if(($(this).attr("type") == "checkbox") && (!$(this).hasClass("general")))
                window.ajaxCounter++;
        });
        
        // Update the general permits
        psinqueSetGeneralPermit(permitKey,
            $("#firstnames" + permitIndex).is(':checked'),
            $("#lastnames" + permitIndex).is(':checked'),
            $("#birthday" + permitIndex).is(':checked'),
            $("#gender" + permitIndex).is(':checked'),
            function() {
                window.ajaxCounter--;
        });
        
        // Update all the other permits
        permitForm.find("input").each(function() {
            if(($(this).attr("type") == "checkbox") && ($(this).attr("class") == "email"))
                psinqueSetEmailPermit($(this).attr("name"), $(this).is(':checked'),
                    function() {
                        window.ajaxCounter--;
                        if(window.ajaxCounter == 0) {
                            stopLogoAnimation();
                        }
                    });
        });

        return false;
    });
}

function addAddPermitHandler(where) {
    
    $(where).click(function() {
        
        if(window.ajaxCounter > 0)  // another query in progress
            return false;
        
        startLogoAnimation();
        window.ajaxCounter = 1;
                
        permitName = $("#newpermitname").val();
        
        if(permitName != "") {
            
            psinqueAddPermit(permitName, window.highestExistingPermitNumber + 1,
                             
                function(data) {

                    newPermitForm = $($.trim(data));
                    newPermitForm.hide();
                    newPermitForm.insertBefore($("#newpermit"));

                    addUpdatePermitHandler(newPermitForm.find(".updatebuttons"));
                    addRemovePermitHandler(newPermitForm.find(".removebuttons"));

                    newPermitForm.slideDown();
                    
                    window.highestExistingPermitNumber++;
                    
                    recreateAccordeon();
                    initializeCheckboxes();
                    stopLogoAnimation();
                    window.ajaxCounter = 0;
                    
                });
            
        } else {
            
            alert("Permit name cannot be empty!");
        } 
        
        return false;
    });
}

$(document).ready(function() {
    
    window.highestExistingPermitNumber = parseInt($("h3").length);

    addUpdatePermitHandler(".updatebuttons");
    addRemovePermitHandler(".removebuttons");
    addAddPermitHandler("#addbutton");
        
    // jQuery UI
    $("#permitlist").accordion({
        heightStyle: "content",
    });
    
});
