
function markChangesInPersona(where) {
    uiMarkChangedFields(where);
    $(where).closest(".tableform").prev().addClass("unsavedchanges");
}

function unmarkChangesInPersona(where) {
    uiUnmarkChangedFields(where);
    $(where).closest(".tableform").prev().removeClass("unsavedchanges");
}

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
        photoNr = $("#photoselection" + personaIndex).val();
        photoKey = $("#personaform" + personaIndex).find("#photo" + photoNr).val();
        
        psinqueSetGeneralPersona($("#personakey" + personaIndex).val(),
            newName,
            $("#givennames_" + personaIndex).is(':checked'),
            $("#familynames_" + personaIndex).is(':checked'),
            $("#birthday_" + personaIndex).is(':checked'),
            $("#gender_" + personaIndex).is(':checked'),
            $("#company" + personaIndex).val(),
            $("#nickname" + personaIndex).val(),
            photoKey,
        function() {
            unmarkChangesInPersona(personaForm.find(".general,.generallabels,.photoselections"));    
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
                        unmarkChangesInPersona(parentrow);
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

                    addAllPersonaHandlers(newPersonaForm);

                    window.highestExistingPersonaNumber++;

                    uiMakeDropdowns(newPersonaForm);
                    newPersonaForm.slideDown();
                                        
                    recreateAccordeon();
                    uiInitializeCheckboxes();
                    unmarkChangesInPersona("#newpersonaname");
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

function addThumbnailSelector(where) {
    $(where).click(function() {
        img = $(this);
        selected = img.hasClass("selected");
        input = img.parent().parent().find(".photoselections")
        $(".thumbnails").removeClass("selected");
        if(!selected) {
            img.addClass("selected");
            input.val(img.attr("data-psinque-index"));
        } else {
            input.val("");
        }
        markChangesInPersona(input);
    });
}

function addChangeDataHandlers(where) {
    $(where).change(function() {
        updateDisplayName($(this).attr("data-psinque-index"));
    });

    $(where).change(function() {
        markChangesInPersona($(this).parent().next());
    });
}

function addAllPersonaHandlers(where) {
    addUpdatePersonaHandler(where.find(".updatebuttons"));
    addRemovePersonaHandler(where.find(".removebuttons"));
    addThumbnailSelector(where.find(".thumbnails"));
    addChangeDataHandlers(where.find("input[type=checkbox]"));
}

$(document).ready(function() {
        
    addAllPersonaHandlers($(document));

    window.highestExistingPersonaNumber = parseInt($("h3").length);

    addAddPersonaHandler("#addpersona");
    uiAddEnterAction("#newpersonaname", "#addpersona");
    
    $("#personalist").accordion({
        heightStyle: "content",
        collapsible: true,
        active: false
    });
    
    $("#enablepublicprofile").change(function() {
        if($(this).is(":checked")) {
            psinqueEnablePublic(true, function() {
                $(".publicpersona").slideDown();
                unmarkChangesInPersona("#enablepublicprofile");
                recreateAccordeon();
            });
        } else
            psinqueEnablePublic(false, function() {
                $(".publicpersona").slideUp();
                unmarkChangesInPersona("#enablepublicprofile");
                recreateAccordeon();
            });
    });
    
    if(!$("#enablepublicprofile").is(":checked")) {
        $(".publicpersona").hide();
    }
    
});
