
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

function removeEmailEntry(tr) {
//     if(tr.hasClass("additionalemails")) {
//         if(window.additionalEmailCounter > 1) {
//             window.additionalEmailCounter--;
            tr.slideUp('fast', function() {
                uiChangeLabelHeight("#additionalemaillabel", -1);
                tr.remove();
            });
//         }
//     } else {
//         $("#primaryemailaddressinput").val("");
//     }
}

function addRemoveEmailHandler(where) {

    $(where).click(function() {
        
        tr = $(this).parent().parent();
        emailKey = tr.find(".emailkeys").val();
        if(emailKey) {
            psinqueRemoveEmail(emailKey, function() {
                removeEmailEntry(tr);
            });
        } else {
            removeEmailEntry(tr);
        }
      
        return false;
    });
}

//---------------------------------------------------------

function addUpdateHandler(where) {
    
    $(where).click(function() {
      
        psinqueAjaxTransactionStart();
        
        psinqueUpdateGeneral($("#givennames").val(),
                             $("#givenroman").val(),
                             $("#familynames").val(),
                             $("#familyroman").val(),
                             $("#companyname").val(),
                             $("#companyroman").val(),
            function() {
                unmarkChangedFields("#generalinfo");
            });
        
        $(".emailaddresses").each(function() {  // then run the AJAX queries
          
            emailinput = $(this);
            emailAddress = emailinput.val();
            if(emailAddress == "")
                return;
            
            td = emailinput.parent();
            typeOfEmail = td.next().find(".typesofemail").val();
            emailKey = td.find(".emailkeys").val();
            if(emailKey) {
                psinqueUpdateEmail(emailKey, emailAddress, typeOfEmail, function() {
                    unmarkChangedFields(td);
                    unmarkChangedFields(td.next());
                });
            } else {
                psinqueAddEmail(emailAddress, typeOfEmail, function(data) {
                    td.find(".emailkeys").val(data["key"]);  // save the key for further queries
                    unmarkChangedFields(td);
                    unmarkChangedFields(td.next());
                });
            }
        });

        psinqueAjaxTransactionStop();
        
        return false;
    });
}

//---------------------------------------------------------

function addAddEmailHandler(where) {
    
    $(where).click(function() {
        
        tr = cloneElement($("#primaryemailaddress > tbody > tr"));
        tr.addClass("additionalemails");
        tr.find('.formlabels').remove();

        // Resize the table label
        uiChangeLabelHeight("#additionalemaillabel", +1)
        
        // Add a remove button
        tr.append("<td class='forminputs formbuttons'><span class='emailremovers buttons clickable'><img src='/images/button_remove.png' /></span></td>");
        addRemoveEmailHandler(tr.find('.emailremovers'));

        // Show the new row
        tr.appendTo("#additionalemailaddresses > tbody");
        tr.slideDown();

        // Re-create the dropdown
        tr.find('.dropdown').remove();
        tr.find('select').dropdown();

        window.additionalEmailCounter++;
        
        return false;   // stop page refresh
    });
}

//---------------------------------------------------------

$(document).ready(function() {

    addAddEmailHandler("#addemail");
    addRemoveEmailHandler(".emailremovers");
    addUpdateHandler("#savebutton");
      
    // Turn the form validation on
//   $("#submitForm").validate();

    // Add map handlers
    geocoder = new google.maps.Geocoder();
    addLocalizerHandler(".localizers");
    
});
