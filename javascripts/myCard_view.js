
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

function removeParent(whose) {
  addressParent = whose.parent();
  addressParent.slideUp('fast', function() {
    addressParent.remove(); // remove the parent
  });
}

function decreaseElementCount() {
    window.elementCount--;
    if(window.elementCount == 0) {  // all fields are updated
//         document.location.reload(true);   // refresh the list of groups
//         window.location = "/mycard/view"
        $(".spinner").hide();
    }
}

function updateGeneralInfo(parent) {
    firstName = $("#firstname").val();
    lastName = $("#lastname").val();
    $.ajax("/mycard/updategeneral?firstname=" + firstName +
                                "&lastname=" + lastName)
        .done(function(data) {
            parsedJSON = $.parseJSON(data);
            if(parsedJSON["status"] == 0) {
                decreaseElementCount();
                parent.find("input,select").css("color", "#000");
            } else {
                alert("Error while updating general information: " + parsedJSON["message"]);
            }
        })
        .error(function(data) {
            alert("Error while updating general information.");
        })
}

function updateEmail(parent) {
    emailAddress = parent.parent().find("#emailAddress").val();
    typeofEmail = parent.parent().find("#typeofEmail").val();
    emailKey = parent.parent().find("#emailKey").val();
    if(emailKey) {
        ajaxMethod = "updateemail?emailKey=" + emailKey + "&";
    } else {
        ajaxMethod = "addemail?";
    }
    $.ajax("/mycard/" + ajaxMethod + "email=" + emailAddress + "&emailType=" + typeofEmail)
        .done(function(data) {
            parsedJSON = $.parseJSON(data);
            if(parsedJSON["status"] == 0) {
                decreaseElementCount();
                if(!emailKey) {
                    parent.find("#emailKey").val(parsedJSON["key"]);
                }
                parent.find("input,select").css("color", "#000");
            } else {
                alert("Error while updating email: " + parsedJSON["message"]);
            }
        })
        .error(function(data) {
            alert("Error while updating email.");
        })
}

function removeEmail(whose) {
    emailKey = whose.parent().parent().find("#emailKey").val();
    if(emailKey) {
        $.ajax("/mycard/removeemail?emailKey=" + emailKey)
            .done(function(data) {
                parsedJSON = $.parseJSON(data);
                if(parsedJSON["status"] == 0) {
                    removeParent(whose.parent());
                } else {
                    alert("Error while removing email: " + parsedJSON["message"]);
                }
            })
            .error(function(data) {
                alert("Error while removing email.");
            })
    } else {
        removeParent(whose.parent());
    }
}

// Set all event handlers when the page is ready
$(document).ready(function() {
    
  $('#addEmail').click(function() {
    newEmail = cloneElement($("#emails > table:first"));
    newEmail.find('.mycardlabels').html("Additional email");
    newEmail.find('.mycardbuttons').remove();
    newEmail.find('tr').append("<td class='mycardbuttons'><a href='' class='emailRemovers'><img src='/images/squareicons/remove.png' /></a></td>");
    newEmail.find('.emailRemovers').click(function() {
        removeEmail($(this));
        return false;
    });
    newEmail.find('input,select').change(function() {
        $(this).css("color", "#de5d35");
    });
    newEmail.insertAfter("#emails > table:last"); // insert hidden
    newEmail.slideDown();  // show
    return false;   // stop page refresh
  });
  
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
//       removeParent($(this));
//       return false;
//     });
// 
//     // Show the new address fields
//     newAddress.slideDown();
// 
//     return false;   // stop page refresh
//   });

  // Add removers to already existing fields
  $('.removers').each(function() {
    $(this).click(function() {
      removeParent($(this));
      return false;          // represss page refresh
    });
  });
  
  $('.emailRemovers').each(function() {
    $(this).click(function() {
      removeEmail($(this));
      return false;          // represss page refresh
    });
  });

  $("#submitButton").click(function() {
      $(this).parent().find(".spinner").show();
      window.elementCount = 1;
      updateGeneralInfo($("#generalInfo"));
      $(".emailAddress").each(function() {  // first count the objects
          window.elementCount++;
      });
      $(".emailAddress").each(function() {  // then run the AJAX querries
          if($(this).attr("class") == "emailAddress") {
              updateEmail($(this));
          }
      });
      return false;
  });
  
  // Turn the form validation on
  $("#submitForm").validate();

//   // Add map handlers
//   $('.addMap').click(addNewMap);
//   $('.hideMap').click(hideTheMap);
//   $('.showMap').click(showTheMap);
});
