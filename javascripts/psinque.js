

function cloneElement(oldElement) {
    newElement = oldElement.clone();  // clone an existing address field group

    // Clean all the input values:
    newElement.find("input,select").val('');
    newElement.hide();

    return newElement;
}

function startLogoAnimation() {
    $("#staticlogo").hide();
    $("#animatedlogo").show();
}

function stopLogoAnimation() {
    $("#staticlogo").show();
    $("#animatedlogo").hide();
}

function markChangedFields(where) {
    where.css("color", "#de5d35");
}

function unmarkChangedFields(where) {
//     where.find("input,select,label").css("color", "#000");
    where.css("color", "#000");
}

function removeElementWithEffects(element) {
//   element.slideUp('fast', function() {
    element.remove();
//   });
}

function hideElementWithEffects(element) {
//   element.slideUp('fast');
    element.hide();
}

function showElementWithEffects(element) {
//   element.slideDown('fast');
    element.show();
}

function initializeCheckboxes() {
    $("input[type=checkbox] + div").unbind('click').bind('click', function() {
        checkBox = $(this).prev();
        checkBox.prop("checked", !checkBox.prop("checked"));
    });
}

$(document).ready(function() {
    
    $(document).ajaxError(function() {
//         $("div.log").text("Triggered ajaxError handler.");
        alert("Uknown error occured while performing operation.");
    });

    
    $("input[type=text],input").change(function() {
        $(this).css("color", "#de5d35");
    });

    initializeCheckboxes();
});
