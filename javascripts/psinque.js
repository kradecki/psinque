
function cloneElement(oldElement) {
    
    newElement = oldElement.clone();  // clone an existing address field group

    // Clean all the input values:
    newElement.find("input,select").val('');
    newElement.hide();
    psinqueSetMarkingOnChange(newElement.find('input,select'));

    return newElement;
}

function startLogoAnimation() {
    window.onbeforeunload = function() {
        return "An AJAX query is in progress. Please wait until it's done.";
    }
    $("#staticlogo").hide();
    $("#animatedlogo").show();
}

function stopLogoAnimation() {
    window.onbeforeunload = null;
    $("#staticlogo").show();
    $("#animatedlogo").hide();
}

function markChangedFields(where) {
    $(where).css("color", "#de5d35");
    $(where).find("input,select").css("color", "#de5d35");
}

function unmarkChangedFields(where) {
    $(where).css("color", "inherit");
    $(where).find("input,select,label").css("color", "inherit");
}

function unmarkAllFields() {
    unmarkChangedFields(document);
}

function removeElementWithEffects(element) {
    element.slideUp('fast', function() {
        element.remove();
    });
}

function hideElementWithEffects(element) {
    element.slideUp('fast');
}

function showElementWithEffects(element) {
    element.slideDown('fast');
}

function psinqueSetMarkingOnChange(where) {
    $(where).change(function() {
        markChangedFields(this);
    });
}

$(document).ready(function() {
    
    $('select').dropdown();
    
    psinqueSetMarkingOnChange("input,select");
    uiInitializeCheckboxes();
    
});
