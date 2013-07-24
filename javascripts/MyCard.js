
// Global Google Map variables
var geocoder;
var maps = [];
var currentAddressPositions = [];

function initializeGoogleMap(mapNr) {
  
    currentAddressPositon = new google.maps.LatLng(-34.397, 150.644);
    
    var mapOptions = {
        center: currentAddressPositon,
        zoom: 12,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    
    maps[mapNr-1] = new google.maps.Map(document.getElementById("googlemap" + mapNr), mapOptions);
    
}

function codeAddress(address, mapNr) {
  
    geocoder.geocode( { 'address': address }, function(results, status) {
      
        if (status == google.maps.GeocoderStatus.OK) {
          
            currentAddressPositions[mapNr-1] = results[0].geometry.location;
            maps[mapNr-1].setCenter(currentAddressPositions[mapNr-1]);
            addressMarker = new google.maps.Marker({
                map: maps[mapNr-1],
                position: currentAddressPositions[mapNr-1],
                draggable: true
            });

            updateAddressCoordinates(mapNr);

            addressMarker.position_changed = function() {
                currentAddressPositions[mapNr-1] = addressMarker.getPosition();
                updateAddressCoordinates(mapNr);
            };
            
        } else {
          
            alert("Geocode was not successful for the following reason: " + status);
        }
    });
}

function updateAddressCoordinates(mapNr) {
  
    // Copy the coordinates into appropriate input fields
    $("#long" + mapNr).val(currentAddressPositions[mapNr-1].jb);
    $("#lat" + mapNr).val(currentAddressPositions[mapNr-1].kb);
  
}

function addLocalizerHandler(where) {
  
    $(where).click(function() {
      
        mapNr = $(this).attr("data-psinque-index");

        initializeGoogleMap(mapNr);
        fullAddress = $("#city" + mapNr).val() + ", " + $("#address" + mapNr).val();
        codeAddress(fullAddress, mapNr);

        $("#googlemap" + mapNr).parent().parent().show();

        return false;

    });
}

//---------------------------------------------------------

function updateEmail(input) {
  
    emailAddress = input.val();
    
    if(emailAddress == "")
        return;

    if(input.hasClass("primary")) {
        isPrimary = true;
    } else if(input.hasClass("additional")) {
        isPrimary = false;
    } else {
        return;
    }
    
    td = input.parent();
    typeOfEmail = td.next().find(".typesofemail").val();
    emailKey = td.find(".additionalemailkeys");
    if(emailKey.val()) {
        psinqueUpdateEmail(emailKey.val(), emailAddress, typeOfEmail, function() {
            unmarkChangedFields(td);
            unmarkChangedFields(td.next());
        });
    } else {
        psinqueAddEmail(emailAddress, typeOfEmail, isPrimary, function(data) {
            emailKey.val(data["key"]);  // save the key for further queries
            unmarkChangedFields(td);
            unmarkChangedFields(td.next());
        });
    }
}

function updateItem(input, prefix, updateFunction, addFunction) {
  
    itemValue = input.val();
    
    if(itemValue == "")
        return;

    td = input.parent();
    privacytd = td.next();
    typetd = privacytd.next();
    privacyType = privacytd.find("." + prefix + "privacytypes").val();
    itemType    = typetd.find("." + prefix + "types").val();
    
    console.log(privacyType);
    console.log(itemType);
    
    itemKey = td.find("." + prefix + "keys");
    if(itemKey.val()) {
        updateFunction(itemKey.val(), itemValue, privacyType, itemType, function() {
            unmarkChangedFields(td);
            unmarkChangedFields(td.next());
        });
    } else {
        addFunction(itemValue, privacyType, itemType, function(data) {
            itemKey.val(data["key"]);  // save the key for further queries
            unmarkChangedFields(td);
            unmarkChangedFields(td.next());
        });
    }
}

function addUpdateHandler(where) {
    
    $(where).click(function() {
      
        psinqueAjaxTransactionStart();
        
        psinqueUpdateGeneral($("#givennames").val(),  $("#givenroman").val(),
                             $("#familynames").val(), $("#familyroman").val(),
                             $("#companyname").val(), $("#companyroman").val(),
                             $("#birthdays").val(),   $("#birthmonths").val(), 
                             $("#birthyears").val(),  $("#gender").val(), 
            function() {
                unmarkChangedFields("#generalinfo");
            });
        
        $(".emailaddresses").each(function() { updateEmail($(this)); });
        $(".phones").each(function() { updateItem($(this), "phone", psinqueUpdatePhone, psinqueAddPhone); });
        $(".ims").each(function() { updateItem($(this), "im", psinqueUpdateIM, psinqueAddIM); });
        $(".wwws").each(function() { updateItem($(this), "www", psinqueUpdateWWW, psinqueAddWWW); });

        psinqueAjaxTransactionStop();
        
        return false;
    });
}

//---------------------------------------------------------

$(document).ready(function() {

    // Handlers for adding new fields
    uiAddAddHandler("additionalemail", psinqueRemoveEmail);
    uiAddAddHandler("phone", psinqueRemovePhone);
    uiAddAddHandler("im", psinqueRemoveIM);
    uiAddAddHandler("www", psinqueRemoveWWW);
    
    // Handlers for removing fields
    uiAddRemoverHandler(".emailremovers", "additionalemail", psinqueRemoveEmail);
    
    // Google map handlers
    geocoder = new google.maps.Geocoder();
    addLocalizerHandler(".localizers");

    // A handler to save all profile data
    addUpdateHandler("#savebutton");
          
});
