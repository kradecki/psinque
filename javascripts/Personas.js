
function addRemovePersonaHandler(where) {
    
    $(where).click(function() {
        
        personaIndex = $(this).attr('data-psinque-index');
        personaKey = $("#personakey" + personaIndex).val();
        persona = $("#personaform" + personaIndex);

        psinqueRemovePersona(personaKey, function() {
            persona.slideUp(function() {
                persona.prev().remove();
                persona.remove();
                recreateAccordeon();
            });
        });
        
        return false;
    });
}

function addUpdatePersonaHandler(where) {
    
    $(where).click(function(url) {
        
        personaIndex = $(this).attr('data-psinque-index');
        personaForm = $("#personaform" + personaIndex);
        
        psinqueAjaxTransactionStart();
        
        // Update the general personas
        psinqueSetGeneralPersona($("#personakey" + personaIndex).val(),
            $("#givennames_" + personaIndex).is(':checked'),
            $("#familynames_" + personaIndex).is(':checked'),
            $("#birthday_" + personaIndex).is(':checked'),
            $("#gender_" + personaIndex).is(':checked'),
        function() {
            uiUnmarkChangedFields(personaForm.find(".generallabels"));    
        });
        
        // Update all the other personas
        personaForm.find("input").each(function() {
            input = $(this);
            parentrow = input.parent().parent();
            itemIndex = input.attr("data-psinque-subindex");
            if(input.attr("type") == "checkbox" && (input.hasClass("individual"))) {               
                psinqueSetIndividualPermit(input.attr("name"), input.is(':checked'),
                    function() {
                        uiUnmarkChangedFields(parentrow);
                    });
            }
        });
        
        psinqueAjaxTransactionStop();

        return false;
    });
}

function addAddPersonaHandler(where) {
    
    $(where).click(function() {
        
        personaName = $("#newpersonaname").val();
        if(personaName != "") {
            
            psinqueAddPersona(personaName, window.highestExistingPersonaNumber + 1,
                             
                function(data) {

                    newPersonaForm = $($.trim(data));
                    newPersonaForm.hide();
                    newPersonaForm.insertBefore($("#newpersona"));

                    addUpdatePersonaHandler(newPersonaForm.find(".updatebuttons"));
                    addRemovePersonaHandler(newPersonaForm.find(".removebuttons"));

                    newPersonaForm.slideDown();
                    
                    window.highestExistingPersonaNumber++;
                    
                    recreateAccordeon();
                    uiInitializeCheckboxes();
                    uiUnmarkChangedFields("#newpersonaname");
                    $("#newpersonaname").val("");
                    
                });
            
        } else {
            
            alert("Persona name cannot be empty!");
        } 
        
        return false;
    });
}

function recreateAccordeon() {
    var active = $("#personalist").accordion("option", "active");
    $("#personalist").accordion('destroy').accordion({
        heightStyle: "content",
        active: active,
    });
}

function updateDisplayName(personaIndex) {
    
    displayName = "";
    
    if($("#givennames_" + personaIndex).is(":checked"))
        displayName += window.givenNames;
    
    if($("#familynames_" + personaIndex).is(":checked")) {
        if(displayName.length > 0)
            displayName += " ";
        displayName += window.familyNames;
    }
    
    if(displayName.length == 0) {
        emailPermits = $("#personaform" + personaIndex).find(".email");
        for(ii = 0; ii < emailPermits.length; ii++) {
            if($("#email" + personaIndex + "_" + (ii+1)).is(":checked")) {
                displayName = $("#emailaddress" + personaIndex + "_" + (ii+1)).html();
                break;
            }
        }
    }
    
    $("#displayname" + personaIndex).html(displayName);
}

$(document).ready(function() {
    
    window.highestExistingPersonaNumber = parseInt($("h3").length);

    addUpdatePersonaHandler(".updatebuttons");
    addRemovePersonaHandler(".removebuttons");
    addAddPersonaHandler("#createpersona");

    $("input[type=checkbox]").change(function() {
        updateDisplayName($(this).attr("data-psinque-index"));
        console.log($(this).is(":checked"));
    });

    $("input[type=checkbox]").change(function() {
        uiMarkChangedFields($(this).parent().next());
    });

    // jQuery UI
    $("#personalist").accordion({
        heightStyle: "content",
        collapsible: true,
        active: false
    });
    
});
