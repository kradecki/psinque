
function executeAJAX(query, done) {
    $.ajax(query)
        .done(function(data) {
            parsedJSON = $.parseJSON(data);
            if(parsedJSON["status"] != 0) {
                alert("Error while performing operation: " + parsedJSON["message"]);
            } else {
                done(parsedJSON);
            }
        })
        .error(function(data) {
            alert("Uknown error occured while performing operation.");
        });
}

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
    where.find("input,select").css("color", "#000");
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

$(document).ready(function() {
    $("input[type=text],input").change(function() {
        $(this).css("color", "#de5d35");
    });
});
