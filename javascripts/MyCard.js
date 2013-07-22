
// // Global Google Map variables
// var geocoder;
// var maps = [];
// var addressMarkers;
// var currentAddressPositions = [];
// 
// function initializeGoogleMap(mapIdNr) {
//   currentAddressPositon = new google.maps.LatLng(-34.397, 150.644);
//   geocoder = new google.maps.Geocoder();
//   var mapOptions = {
//     center: currentAddressPositon,
//     zoom: 12,
//     mapTypeId: google.maps.MapTypeId.ROADMAP
//   };
//   maps[mapIdNr-1] = new google.maps.Map(document.getElementById("map_canvas" + mapIdNr), mapOptions);
// }
// 
// function codeAddress(address, mapIdNr) {
//   geocoder.geocode( { 'address': address }, function(results, status) {
//     if (status == google.maps.GeocoderStatus.OK) {
//       currentAddressPositions[mapIdNr-1] = results[0].geometry.location;
//       maps[mapIdNr-1].setCenter(currentAddressPositions[mapIdNr-1]);
//       addressMarker = new google.maps.Marker({
//         map: maps[mapIdNr-1],
//         position: currentAddressPositions[mapIdNr-1],
//         draggable: true
//       });
// 
//       updateAddressCoordinates(mapIdNr);
// 
//       addressMarker.position_changed = function() {
//         currentAddressPositions[mapIdNr-1] = addressMarker.getPosition();
//         updateAddressCoordinates(mapIdNr);
//       };
//     } else {
//       alert("Geocode was not successful for the following reason: " + status);
//     }
//   });
// }

// function updateAddressCoordinates(mapIdNr) {
//   // Copy the coordinates into appropriate input fields
//   $("#long" + mapIdNr).val(currentAddressPositions[mapIdNr-1].Xa);
//   $("#lat" + mapIdNr).val(currentAddressPositions[mapIdNr-1].Ya);
// }
// 
// function addNewMap() {
//   mapIdNr = parseInt($(this).parent()[0].id.match("[0-9]+"));
//   $(this).parent().append('<br /><div class="mapCanvas" id="map_canvas' + mapIdNr + '"></div>');
// 
//   initializeGoogleMap(mapIdNr);
//   fullAddress = $(this).siblings("input").map(function() { return $(this).val(); }).get().join(", ")  // join all fields for the query
//   console.log(fullAddress);  //TODO: The above also joins the empty longitude and latitude fields...
//   codeAddress(fullAddress, mapIdNr);
// 
//   $(this).hide();
//   $(this).next().show();
// 
//   return false;
// }

// function hideTheMap() {
//   mapIdNr = parseInt($(this).parent()[0].id.match("[0-9]+"));
//   $("#map_canvas" + mapIdNr).slideUp();
//   $(this).hide();
//   $(this).next().show();
//   return false;
// }
// 
// function showTheMap() {
//   mapIdNr = parseInt($(this).parent()[0].id.match("[0-9]+"));
//   $("#map_canvas" + mapIdNr).slideDown();
//   $(this).hide();
//   $(this).prev().show();
//   return false;
// }

//   $('#addAddress').click(function() {
//     newAddress = cloneElement("address", addressCounter++, addressCounter+1);
//     newAddress.insertBefore("#addAddress"); // insert hidden
// 
//     // Handle the google map
//     newAddress.find("div").remove();        // remove the google map too
//     newAddress.find(".showMap").hide();
//     newAddress.find(".hideMap").hide();
//     newAddress.find(".addMap").show();
//     newAddress.find(".addMap").click(addNewMap);
//     newAddress.find(".hideMap").click(hideTheMap);
//     newAddress.find(".showMap").click(showTheMap);
// 
//     // Add a handle to remove this address
//     if(addressCounter == 2)  // we cloned the first address, so we need to add a 'remove' link
//       newAddress.append(' | <a href="" id="remover' + addressCounter + '" class="removers">Remove</a>')
//     newAddress.find('#remover' + addressCounter).click(function() {
//       removeElementWithEffects($(this).parent());
//       return false;
//     });
// 
//     // Show the new address fields
//     newAddress.slideDown();
// 
//     return false;   // stop page refresh
//   });

//---------------------------------------------------------

function removeEmailEntry(tr) {
    if(tr.hasClass("additionalemails")) {
        window.additionalEmailCounter--;
        if(window.additionalEmailCounter > 0) {
            formlabel = $("#additionalemaillabel");
            if(formlabel.parent().is(tr))
                formlabel.prependTo(tr.next());
            formlabel.attr("rowspan", window.additionalEmailCounter);
        }
        removeElementWithEffects(tr);
    } else {
        $("#primaryemailaddressinput").val("");
    }
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
        
        psinqueUpdateGeneral($("#firstname").val(), $("#lastname").val(),
            function() {
                unmarkChangedFields("#generalinfo");
            });
        
        $(".emailaddresses").each(function() {  // then run the AJAX queries
            emailinput = $(this);
            emailAddress = emailinput.val();
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
        
        return false;
    });
}

//---------------------------------------------------------

function addAddEmailHandler(where) {
    
    $(where).click(function() {
        
        tr = cloneElement($("#primaryemailaddress > tbody > tr"));
        window.additionalEmailCounter++;

        tr.addClass("additionalemails");
        tr.find('.formlabels').remove();
        tr.find('.formbuttons:first').remove();
        tr.find('.formbuttons').html("<span class='emailremovers buttons clickable'><img src='/images/squareicons/remove.png' /></span>");

        if(window.additionalEmailCounter == 1) {
            tr.prepend($("<td rowspan='1' class='formlabels' id='additionalemaillabel'><label>Additional emails</label></td>"));
        } else {
            $("#additionalemaillabel").attr('rowspan', window.additionalEmailCounter);
        }
        
        addRemoveEmailHandler(tr.find('.emailremovers'));

        tr.appendTo("#additionalemailaddresses > tbody");
        tr.slideDown();
        
        return false;   // stop page refresh
    });
}

//---------------------------------------------------------

$(document).ready(function() {

    addAddEmailHandler("#addemail");
    addRemoveEmailHandler(".emailremovers");
    addUpdateHandler("#savebutton");
      
//     $("input[type=text]").submit(function() {
//         
//     });

    // Turn the form validation on
//   $("#submitForm").validate();

//   // Add map handlers
//   $('.addMap').click(addNewMap);
//   $('.hideMap').click(hideTheMap);
//   $('.showMap').click(showTheMap);
    
});
