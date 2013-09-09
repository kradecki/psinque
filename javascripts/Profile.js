
// Global Google Map variables
var geocoder;
var maps = [];
var currentAddressPositions = [];
var markers = [];

function initializeGoogleMap(mapNr, lat, long) {
  
    currentAddressPositions[mapNr-1] = new google.maps.LatLng(lat, long);
    
    var mapOptions = {
        center: currentAddressPositions[mapNr-1],
        zoom: 12,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    
    maps[mapNr-1] = new google.maps.Map(document.getElementById("googlemap" + mapNr), mapOptions);  

    markers[mapNr-1] = new google.maps.Marker({
        map: maps[mapNr-1],
        position: currentAddressPositions[mapNr-1],
        draggable: true,
    });

    markers[mapNr-1].position_changed = function() {
        currentAddressPositions[mapNr-1] = markers[mapNr-1].getPosition();
        updateAddressCoordinates(mapNr);
    };
}

function updateMapMarker(mapNr) {
  markers[mapNr-1].setPosition(currentAddressPositions[mapNr-1]);
}

function codeAddress(address, mapNr) {
  
    geocoder.geocode( { 'address': address }, function(results, status) {
      
        console.log(status);
      
        if (status == google.maps.GeocoderStatus.OK) {
          
            currentAddressPositions[mapNr-1] = results[0].geometry.location;
            
            maps[mapNr-1].setCenter(currentAddressPositions[mapNr-1]);
            updateMapMarker(mapNr);
            
            updateAddressCoordinates(mapNr);
            $("#googlemap" + mapNr).parent().parent().show();
                        
        } else if(status == google.maps.GeocoderStatus.ZERO_RESULTS) {
            
            uiShowErrorMessage("No results were found for the given address.");
            
            return false;
          
        } else {

            uiShowErrorMessage("Geocode was not successful for the following reason: " + status);
            
            return false;
        }
    });
}

function updateAddressCoordinates(mapNr) {
  
    // Copy the coordinates into appropriate input fields
    $("#longitude" + mapNr).val(currentAddressPositions[mapNr-1].pb);
    $("#latitude" + mapNr).val(currentAddressPositions[mapNr-1].ob);
  
}

function addLocalizerHandler(where) {
  
    $(where).click(function() {
      
        if(!uiValidateTextInputs(".required.addressdata", "Not enough address data to perform geocoding. You need to specify at least the address and the city."))
           return false;
      
        mapNr = $(this).attr("data-psinque-index");

        initializeGoogleMap(mapNr, 54.366667, 18.633333);
        fullAddress = $("#city" + mapNr).val() + ", " + $("#address" + mapNr).val();
        
        codeAddress(fullAddress, mapNr);

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
            uiUnmarkChangedFields(td);
            uiUnmarkChangedFields(td.next());
        });
    } else {
        psinqueAddEmail(emailAddress, typeOfEmail, isPrimary, function(data) {
            emailKey.val(data["key"]);  // save the key for further queries
            uiUnmarkChangedFields(td);
            uiUnmarkChangedFields(td.next());
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
    
    itemKey = td.find("." + prefix + "keys");
    if(itemKey.val()) {
        updateFunction(itemKey.val(), itemValue, privacyType, itemType, function() {
            uiUnmarkChangedFields(td);
            uiUnmarkChangedFields(td.next());
        });
    } else {
        addFunction(itemValue, privacyType, itemType, function(data) {
            itemKey.val(data["key"]);  // save the key for further queries
            uiUnmarkChangedFields(td);
            uiUnmarkChangedFields(td.next());
        });
    }
}

function updateAddress(input) {
  
    address = input.val();
    if(address == "")
        return;

    tr = input.parent().parent();
    
    addressNr = input.attr("data-psinque-index");
    console.log(addressNr);
    
    addressKey = $("#addresskey" + addressNr);
    city = $("#city" + addressNr).val();
    postalCode = $("#postalcode" + addressNr).val();
    country = $("#country" + addressNr).val();
    privacyType = $("#addressprivacytype" + addressNr).val();
    longitude = $("#longitude" + addressNr).val();
    latitude = $("#latitude" + addressNr).val();

    if(addressKey.val()) {
        psinqueUpdateAddress(addressKey.val(), address, city,
                             postalCode, country, privacyType,
                             longitude, latitude,
            function() {
                uiUnmarkChangedFields(tr);
                uiUnmarkChangedFields(tr.next());
            });
    } else {
        psinqueAddAddress(address, city, postalCode, country,
                          privacyType, longitude, latitude, 
            function(data) {
                addressKey.val(data["key"]);
                uiUnmarkChangedFields(tr);
                uiUnmarkChangedFields(tr.next());
            });
    }
}

function uiValidateTextInputs(selector, message) {
  
    fieldsCorrect = true;
  
    $(selector).each(function() {
      
        e = $(this);
      
        if(e.val() == "") {
      
            uiShowErrorMessage(message);
            fieldsCorrect = false;
        }
    });
  
    return fieldsCorrect;
}

function uiValidateEmails(selector) {
  
    fieldsCorrect = true;
  
    $(selector).each(function() {
      
        e = $(this);
      
        if(e.hasClass("emailaddresses") && (e.val() != "") &&  (!uiValidateEmail(e.val()))) {
          
            uiShowErrorMessage("Invalid email address: " + e.val());
            fieldsCorrect = false;
        }
    });
  
    return fieldsCorrect;
}

function addUpdateHandler(where) {
    
    $(where).click(function() {
      
        if(!uiValidateTextInputs(".required.general", "You need to fill out the given and family names."))
            return false;
      
        if(!uiValidateTextInputs(".required.emailaddresses", "You need to fill out the primary email address."))
            return false;
        
        if(!uiValidateEmails(".emailaddresses"))
            return false;
      
        psinqueAjaxTransactionStart();
        
        psinqueUpdateGeneral($("#prefix").val(), 
                             $("#givennames").val(),  $("#givenroman").val(),
                             $("#familynames").val(), $("#familyroman").val(),
                             $("#suffix").val(), 
                             $("#companyname").val(), $("#companyroman").val(),
                             $("#birthdays").val(),   $("#birthmonths").val(), 
                             $("#birthyears").val(),  $("#gender").val(), 
            function() {
                uiUnmarkChangedFields("#generalinfo");
            });
        
        $(".emailaddresses").each(function() { updateEmail($(this)); });
        $(".phones").each(function() { updateItem($(this), "phone", psinqueUpdatePhone, psinqueAddPhone); });
        $(".ims").each(function() { updateItem($(this), "im", psinqueUpdateIM, psinqueAddIM); });
        $(".wwws").each(function() { updateItem($(this), "www", psinqueUpdateWWW, psinqueAddWWW); });
        $(".addresses").each(function() { updateAddress($(this)); });

        psinqueAjaxTransactionStop();
        
        return false;
    });
}

//---------------------------------------------------------

$(document).ready(function() {

    // Count the elements
    additionalEmailCounter = $(".additionalemails").length;
    addressCounter = $(".adresses").length;

    // Handlers for adding new fields
    uiAddAddHandler("additionalemail", psinqueRemoveEmail);
    uiAddAddHandler("phone", psinqueRemovePhone);
    uiAddAddHandler("im", psinqueRemoveIM);
    uiAddAddHandler("www", psinqueRemoveWWW);
    uiAddAddHandler("nickname", null);
    uiAddAddHandler("company", null);
    
    // Handlers for removing fields
    uiAddRemoverHandler(".emailremovers", "additionalemail", psinqueRemoveEmail);
    uiAddRemoverHandler(".imremovers", "im", psinqueRemoveIM);
    uiAddRemoverHandler(".phoneremovers", "phone", psinqueRemovePhone);
    uiAddRemoverHandler(".wwwremovers", "www", psinqueRemoveWWW);
    
    $(".mapremovers").click(function() {
        map = $(this).parent().parent().prev();
        map.find("input").val("");
        map.parent().hide();
    });
    
    // Google map handlers
    geocoder = new google.maps.Geocoder();
    addLocalizerHandler(".localizers");
    $(".longitudes").each(function() {
        long = $(this).val();
        if(long != "") {

            mapNr = $(this).attr("data-psinque-index");
            lat = $("#latitude" + mapNr).val();
            
            initializeGoogleMap(mapNr, lat, long);

            $("#googlemap" + mapNr).parent().parent().show();
        }
    });

    // A handler to save all profile data
    addUpdateHandler("#savebutton");
    
    // React to pressing the Enter key
    uiAddEnterAction("input[type=text]", "#savebutton");
    
});
