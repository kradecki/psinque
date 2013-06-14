
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

function decreaseElementCount() {
    window.elementCount--;
    if(window.elementCount == 0) {  // all fields are updated
        stopLogoAnimation();
    }
}

function removeEmailEntry(parent) {
    if(tableformlabel = parent.find(".tableformlabels")) {
        if(tableformlabel.html() == "Additional emails") {
            additionalEmailCounter--;
            if(additionalEmailCounter > 0){
                tableformlabel.attr("rowspan", additionalEmailCounter);
                tableformlabel.insertBefore(parent.parent().find("tr:first > td:first"));
            }
        }
    }
    removeElementWithEffects(parent);
}

//---------------------------------------------------------
// AJAX executing functions

function updateGeneralInfo(parent) {
    firstName = $("#firstname").val();
    lastName = $("#lastname").val();
    executeAJAX("/mycard/updategeneral?firstname=" + firstName +
                                     "&lastname=" + lastName,
                function() {
                    decreaseElementCount();
                    unmarkChangedFields(parent);
                });
}

function updateEmail(emailinput) {
    emailAddress = emailinput.val();
    parent = emailinput.parent()
    typeofEmail = parent.next().find(".typesofemail").val();
    emailKey = parent.find(".emailkeys").val();
    if(emailKey) {
        ajaxMethod = "updateemail?key=" + emailKey + "&";
    } else {
        ajaxMethod = "addemail?";
    }
    executeAJAX("/mycard/" + ajaxMethod + "email=" + emailAddress + "&type=" + typeofEmail,
                function() {
                    decreaseElementCount();
                    if(!emailKey) {
                        parent.find(".emailkeys").val(parsedJSON["key"]);
                    }
                    parent.find("input").css("color", "#000");
                    parent.next().find("select").css("color", "#000");
                });
}

function removeEmail(removeButton) {
    parent = removeButton.parent().parent();
    emailKey = parent.find(".tableforminputs > .emailkeys").val();
    if(emailKey) {
        executeAJAX("/mycard/removeemail?key=" + emailKey,
                    function() {
                        removeEmailEntry(parent);
                    });
    } else {
        removeEmailEntry(parent);
    }
}

//---------------------------------------------------------
// Initial JS handlers

$(document).ready(function() {
    
  $('#addemail').click(function() {
      
      newEmail = cloneElement($("#primaryemailaddress > tbody > tr"));

      newEmail.find('.tableformlabels').remove();
      newEmail.find('.tableformbuttons').html("<a href='' class='emailremovers'><img src='/images/squareicons/remove.png' /></a>");
      newEmail.find('input,select').change(function() {
          markChangedFields($(this));
      });
      newEmail.find('input,select').val('');

      if(additionalEmailCounter == 0) {
          $("<td rowspan=" + additionalEmailCounter + " class='tableformlabels'>Additional emails</td>").insertBefore(newEmail.find("td:first"));
      } else {
          $("#additionalemailaddresses > tbody > tr > .tableformlabels").attr('rowspan', additionalEmailCounter + 1);
      }
      additionalEmailCounter++;
      
      newEmail.find('.emailremovers').click(function() {
          removeEmail($(this));
          return false;
      });

      newEmail.appendTo("#additionalemailaddresses");
      newEmail.slideDown();
      
      return false;   // stop page refresh
  });
  
  // Add removers to already existing fields
  $('.removers').each(function() {
    $(this).click(function() {
      removeElementWithEffects($(this).parent());
      return false;          // represss page refresh
    });
  });
  
  $('.emailremovers').each(function() {
    $(this).click(function() {
      removeEmail($(this));
      return false;          // represss page refresh
    });
  });

  $("#submitbutton").click(function() {
      startLogoAnimation();
      window.elementCount = 1; // the general info is always there
      updateGeneralInfo($("#generalinfo"));
      $(".emailaddresses").each(function() {  // first count the objects
          window.elementCount++;
      });
      $(".emailaddresses").each(function() {  // then run the AJAX queries
          updateEmail($(this));
      });
      return false;
  });
  
  // Turn the form validation on
//   $("#submitForm").validate();

//   // Add map handlers
//   $('.addMap').click(addNewMap);
//   $('.hideMap').click(hideTheMap);
//   $('.showMap').click(showTheMap);
});
