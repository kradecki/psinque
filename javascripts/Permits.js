
function addRemovePermitHandler(where) {
    
    $(where).click(function() {
        
        permitIndex = $(this).attr('data-psinque-index');
        permitKey = $("#permitkey" + permitIndex).val();
        permit = $("#permitform" + permitIndex);

        psinqueRemovePermit(permitKey, function() {
            permit.slideUp(function() {
                permit.prev().remove();
                permit.remove();
                recreateAccordeon();
            });
        });
        
        return false;
    });
}

function addUpdatePermitHandler(where) {
    
    $(where).click(function(url) {
        
        permitIndex = $(this).attr('data-psinque-index');
        permitForm = $("#permitform" + permitIndex);
        
        psinqueAjaxTransactionStart();
        
        // Update the general permits
        psinqueSetGeneralPermit($("#permitkey" + permitIndex).val(),
            $("#givennames_" + permitIndex).is(':checked'),
            $("#familynames_" + permitIndex).is(':checked'),
            $("#birthday_" + permitIndex).is(':checked'),
            $("#gender_" + permitIndex).is(':checked'),
        function() {
            unmarkChangedFields(permitForm.find(".generallabels"));    
        });
        
        // Update all the other permits
        permitForm.find("input").each(function() {
            input = $(this);
            parentrow = input.parent().parent();
            itemIndex = input.attr("data-psinque-subindex");
            if(input.attr("type") == "checkbox" && (input.hasClass("individual"))) {               
                psinqueSetIndividualPermit(input.attr("name"), input.is(':checked'),
                    function() {
                        unmarkChangedFields(parentrow);
                    });
            }
        });
        
        psinqueAjaxTransactionStop();

        return false;
    });
}

function addAddPermitHandler(where) {
    
    $(where).click(function() {
        
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
                    uiInitializeCheckboxes();
                    unmarkChangedFields("#newpermitname");
                    $("#newpermitname").val("");
                    
                });
            
        } else {
            
            alert("Permit name cannot be empty!");
        } 
        
        return false;
    });
}

function recreateAccordeon() {
    var active = $("#permitlist").accordion("option", "active");
    $("#permitlist").accordion('destroy').accordion({
        heightStyle: "content",
        active: active,
    });
}

function updateDisplayName(permitIndex) {
    
    displayName = "";
    
    if($("#givennames_" + permitIndex).is(":checked"))
        displayName += window.givenNames;
    
    if($("#familynames_" + permitIndex).is(":checked")) {
        if(displayName.length > 0)
            displayName += " ";
        displayName += window.familyNames;
    }
    
    if(displayName.length == 0) {
        emailPermits = $("#permitform" + permitIndex).find(".email");
        for(ii = 0; ii < emailPermits.length; ii++) {
            if($("#email" + permitIndex + "_" + (ii+1)).is(":checked")) {
                displayName = $("#emailaddress" + permitIndex + "_" + (ii+1)).html();
                break;
            }
        }
    }
    
    $("#displayname" + permitIndex).html(displayName);
}

$(document).ready(function() {
    
    window.highestExistingPermitNumber = parseInt($("h3").length);

    addUpdatePermitHandler(".updatebuttons");
    addRemovePermitHandler(".removebuttons");
    addAddPermitHandler("#createpermit");

    $("input[type=checkbox]").change(function() {
        updateDisplayName($(this).attr("data-psinque-index"));
        console.log($(this).is(":checked"));
    });

    $("input[type=checkbox]").change(function() {
        markChangedFields($(this).parent().next());
    });

    // jQuery UI
    $("#permitlist").accordion({
        heightStyle: "content",
    });
    
});
