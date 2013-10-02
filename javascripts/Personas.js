
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
        
        newName = $("#personaname" + personaIndex).val();
        
        psinqueAjaxTransactionStart();
        
        // Update the general personas
        psinqueSetGeneralPersona($("#personakey" + personaIndex).val(),
            newName,
            $("#givennames_" + personaIndex).is(':checked'),
            $("#familynames_" + personaIndex).is(':checked'),
            $("#birthday_" + personaIndex).is(':checked'),
            $("#gender_" + personaIndex).is(':checked'),
        function() {
            uiUnmarkChangedFields(personaForm.find(".general"));    
            if(newName) personaForm.prev().find("label").html(newName);
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
                        
                        if($(".unsavedchanges").length == 0)
                            window.unsavedChanges = false;
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
        collapsible: true,
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
        emailPermits = $("#personaform" + personaIndex).find(".emails");
        for(ii = 0; ii < emailPermits.length; ii++) {
            if($("#email" + (ii+1) + "_" + personaIndex).is(":checked")) {
                displayName = $("#labelemail" + (ii+1) + "_" + personaIndex).html();
                break;
            }
        }
    }

    if(displayName.length == 0) {
        displayName = "Anonymous user " + $("#personaid" + personaIndex).val();
    }

    $("#displayname" + personaIndex).html(displayName);
}

$(document).ready(function() {
    
    window.highestExistingPersonaNumber = parseInt($("h3").length);

    addUpdatePersonaHandler(".updatebuttons");
    addRemovePersonaHandler(".removebuttons");
    addAddPersonaHandler("#addpersona");

    $("input[type=checkbox]").change(function() {
        updateDisplayName($(this).attr("data-psinque-index"));
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
    
    $("#enablepublicprofile").change(function() {
        if($(this).is(":checked")) {
            $(".publicpersona").slideDown();
            recreateAccordeon();
        } else
            $(".publicpersona").slideUp();
            recreateAccordeon();
    });
    
    // Correct the margins in image grids; couldn't do that in CSS
    // CORRECTION: did that in CSS
//     $(".imageinputs").each(function() {
//         imgs = $(this).find("img");
//         imgs.slice(-(imgs.length % 9)).css("margin-bottom", 0)
//     });
    
});
