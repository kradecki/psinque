
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
    
    console.log(mapNr);
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

// Copies the coordinates into appropriate input fields
function updateAddressCoordinates(mapNr) {
  
    lonInput = $("#longitude" + mapNr);
    lonInput.val(currentAddressPositions[mapNr-1].lng());
    lonInput.addClass("unsavedchanges");
    
    latInput = $("#latitude" + mapNr);
    latInput.val(currentAddressPositions[mapNr-1].lat());
    latInput.addClass("unsavedchanges");
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

function openExistingGoogleMaps() {
  
    $(".longitudes").each(function() {
        long = $(this).val();
        if(long != "") {

            mapNr = $(this).attr("data-psinque-index");
            lat = $("#latitude" + mapNr).val();
            
            initializeGoogleMap(mapNr, lat, long);

            $("#googlemap" + mapNr).parent().parent().show();
        }
    });
}

//---------------------------------------------------------

function updateEmail(input) {
  
    var emailAddress = input.val();
    
    if(emailAddress == "")
        return;

    if(!uiValidateEmail(emailAddress))
        return false;
  
    if(input.hasClass("primary")) {
        isPrimary = true;
    } else if(input.hasClass("additional")) {
        isPrimary = false;
    } else {
        return;
    }
    
    var typeOfEmail = input.parent().next().find(".typesofemail").val();
    var emailKey = input.parent().find(".additionalemailkeys");
    if(emailKey.val()) {
        psinqueUpdateEmail(emailKey.val(), emailAddress, typeOfEmail, function() {
            uiUnmarkChangedFields(input.parent());
            uiUnmarkChangedFields(input.parent().next());
        });
    } else {
        psinqueAddEmail(emailAddress, typeOfEmail, isPrimary, function(data) {
            emailKey.val(data["key"]);  // save the key for further queries
            uiUnmarkChangedFields(input.parent());
            uiUnmarkChangedFields(input.parent().next());
        });
    }
}

function updateNickname(input) {
  
    itemValue = input.val();
    
    if(itemValue == "")
        return;
  
    var td = input.parent();
    itemKey = td.find(".nicknamekeys");
    if(itemKey.val()) {
        psinqueUpdateNickname(itemKey.val(), itemValue, function() {
            uiUnmarkChangedFields(td);
            uiUnmarkChangedFields(td.next());
        });
    } else {
        psinqueAddNickname(itemValue, function(data) {
            itemKey.val(data["key"]);  // save the key for further queries
            uiUnmarkChangedFields(td);
            uiUnmarkChangedFields(td.next());
        });
    }
}

function updateCompany(input) {
  
    itemValue = input.val();
    
    if(itemValue == "")
        return;
  
    var td = input.parent();
    itemType = td.next().find("input").val()
    itemKey = td.find(".companykeys");
    if(itemKey.val()) {
        psinqueUpdateCompany(itemKey.val(), itemValue, itemType, function() {
            uiUnmarkChangedFields(td);
            uiUnmarkChangedFields(td.next());
        });
    } else {
        psinqueAddCompany(itemValue, itemType, function(data) {
            itemKey.val(data["key"]);  // save the key for further queries
            uiUnmarkChangedFields(td);
            uiUnmarkChangedFields(td.next());
        });
    }
}

function updateItem(input, prefix, updateFunction, addFunction) {
  
    var itemValue = input.val();
    
    if(itemValue == "")
        return;
    
    itemValue = itemValue.trim();
    
    if(prefix == "www") {
        if(itemValue.indexOf("/") == -1)
            itemValue = itemValue + "/";
        if((itemValue.indexOf("http://") < 0) && (itemValue.indexOf("https://") < 0))
            itemValue = "http://" + itemValue;
    }

    var td = input.parent();
    itemTypes = td.next().find("." + prefix + "types").val()
    itemTypes = itemTypes.split(" ");
    
    itemKey = td.find("." + prefix + "keys");
    if(itemKey.val()) {
        updateFunction(itemKey.val(), itemValue, itemTypes[0], itemTypes[1], function() {
            uiUnmarkChangedFields(td);
            uiUnmarkChangedFields(td.next());
        });
    } else {
        addFunction(itemValue, itemTypes[0], itemTypes[1], function(data) {
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

    var tr = input.parent().parent();
    
    var addressNr = input.attr("data-psinque-index");
    
    city = $("#city" + addressNr).val();
    if(city == "") {
        uiShowErrorMessage("The city field in the address cannot be empty.");
        return;
    }
    
    addressKey = $("#addresskey" + addressNr);
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
                uiUnmarkChangedFields(tr.parent());
            });
    } else {
        psinqueAddAddress(address, city, postalCode, country,
                          privacyType, longitude, latitude, 
            function(data) {
                addressKey.val(data["key"]);
                uiUnmarkChangedFields(tr.parent());
            });
    }
}

function addUpdateHandler(where) {
    
    $(where).click(function() {

        if(!uiValidateTextInputs(".required.general", "You need to fill out the given and family names."))
            return false;
      
        if(!uiValidateTextInputs(".required.emailaddresses", "You need to fill out the primary email address."))
            return false;
        
        birthyear = parseInt($("#birthyears").val());
        birthmonth = parseInt($("#birthmonths").val());
        birthday = parseInt($("#birthdays").val());
        
        if(!uiValidateDate(birthyear, birthmonth, birthday)) {
            uiShowErrorMessage("Are you sure your birthdate is correct? This date is invalid...");
            return false;
        }
        
        psinqueAjaxTransactionStart();
        
        if($(".general.unsavedchanges").length > 0) {
          psinqueUpdateGeneral($("#prefix").val(), 
                               $("#givennames").val(),  $("#givenroman").val(),
                               $("#familynames").val(), $("#familyroman").val(),
                               $("#suffix").val(), 
                               $("#companyname").val(), $("#companyroman").val(),
                               birthday, birthmonth+1, birthyear,
                               $("#gender").val(), 
              function() {
                  uiUnmarkChangedFields(".general.unsavedchanges");
              });
        }
        
        $(".emailaddresses").each(function() {
            if($(this).closest("tr").find(".unsavedchanges").length > 0)
                updateEmail($(this));
        });
        $(".phones").each(function() {
            if($(this).closest("tr").find(".unsavedchanges").length > 0)
                updateItem($(this), "phone", psinqueUpdatePhone, psinqueAddPhone);
        });
        $(".ims").each(function() {
            if($(this).closest("tr").find(".unsavedchanges").length > 0)
                updateItem($(this), "im", psinqueUpdateIM, psinqueAddIM);
        });
        $(".wwws").each(function() {
            if($(this).closest("tr").find(".unsavedchanges").length > 0)
                updateItem($(this), "www", psinqueUpdateWWW, psinqueAddWWW);
        });
        $(".addresses").each(function() {
            tr = $(this).closest("tr");
            if((tr.find(".unsavedchanges").length > 0) 
              || (tr.next().find(".unsavedchanges").length > 0)
              || (tr.next().next().find(".unsavedchanges").length > 0))
                updateAddress($(this));
        });
        $(".nicknames").each(function() {
            if($(this).closest("tr").find(".unsavedchanges").length > 0)
                updateNickname($(this));
        });
        $(".companys").each(function() {
            if($(this).closest("tr").find(".unsavedchanges").length > 0)
                updateCompany($(this));
        });

        psinqueAjaxTransactionStop();
        
        return false;
    });
}

function removePhotoWithEffects(element) {
    element.slideUp('fast', function() {
        element.remove();
        if($(".photoitem").length == 0) {  // no photos left
            $("<img src='/images/nophoto.png' id='nophoto'>").appendTo("#mosaic");
        }
    });
}

function addPhotoRemoverHandler(where) {
  
    $(where).click(function() {
        
        photoDiv = $(this).parent().parent();
        photoKey = photoDiv.find(".photokeys").val();
        if(photoKey) {
            psinqueRemovePhoto(photoKey, function() {
                removePhotoWithEffects(photoDiv);
            });
        } else {
            removePhotoWithEffects(photoDiv);
        }
      
        return false;
    }); 
}

function initializeImageUploading() {
  
    $('#imageupload').fileupload({
        submit: function (e, data) {
            var $this = $(this);
            uiStartLogoAnimation();
            window.ajaxInProgress = true;
            $.getJSON('/profile/getphotouploadurl', function (result) {
                data.url = result;
                $this.fileupload('send', data);
            });
            return false;
        },
        done: function (e, data) {
            $("#nophoto").remove();
            newItem = $(data.result).appendTo("#mosaic");
            addPhotoRemoverHandler(newItem.find(".photoremovers"));
            $('a.colorbox').colorbox.remove()
            $('a.colorbox').colorbox();
            uiStopLogoAnimation();
            window.ajaxInProgress = false;
        } 
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
    uiAddAddHandler("nickname", psinqueRemoveNickname);
    uiAddAddHandler("company", psinqueRemoveCompany);
    
    // Handlers for removing standard fields
    uiAddRemoverHandler(".emailremovers", "additionalemail", psinqueRemoveEmail);
    uiAddRemoverHandler(".imremovers", "im", psinqueRemoveIM);
    uiAddRemoverHandler(".phoneremovers", "phone", psinqueRemovePhone);
    uiAddRemoverHandler(".wwwremovers", "www", psinqueRemoveWWW);

    uiAddRemoverHandler(".companyremovers", "company", psinqueRemoveCompany);
    uiAddRemoverHandler(".nicknameremovers", "nickname", psinqueRemoveNickname);
    
    // Non-standard element removers
    $(".mapremovers").click(function() {
        map = $(this).parent().parent().prev();
        input = map.find("input");
        input.val("");
        uiMarkChangedFields(input);
        map.parent().hide();
    });
    
    // Google map handlers
    geocoder = new google.maps.Geocoder();
    addLocalizerHandler(".localizers");
    openExistingGoogleMaps();

    // A handler to save all profile data
    addUpdateHandler("#savebutton");
    
    // React to pressing the Enter key
    uiAddEnterAction("input[type=text].general", "#savebutton");
    uiAddEnterAction("input[type=text].additional.emailaddresses:first", "#addadditionalemail");
    uiAddEnterAction("input[type=text].nicknames:first", "#addnickname");
    uiAddEnterAction("input[type=text].companys:first", "#addcompany");
    uiAddEnterAction("input[type=text].positions:first", "#addcompany");
    uiAddEnterAction("input[type=text].phones:first", "#addphone");
    uiAddEnterAction("input[type=text].ims:first", "#addim");
    uiAddEnterAction("input[type=text].wwws:first", "#addwww");

    // Profile pictures
    initializeImageUploading();    
    $('a.colorbox').colorbox();   // enable the colorbox
    
    addPhotoRemoverHandler(".photoremovers");

});
