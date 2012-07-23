
// Global Google Map variables
var geocoder;
var maps = [];
var addressMarkers;
var currentAddressPositons = [];

function initializeGoogleMap(mapIdNr) {
  currentAddressPositon = new google.maps.LatLng(-34.397, 150.644);
  geocoder = new google.maps.Geocoder();
  var mapOptions = {
    center: currentAddressPositon,
    zoom: 12,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  maps[mapIdNr-1] = new google.maps.Map(document.getElementById("map_canvas" + mapIdNr), mapOptions);
}

function codeAddress(address, mapIdNr) {
  geocoder.geocode( { 'address': address }, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      currentAddressPositons[mapIdNr-1] = results[0].geometry.location;
      maps[mapIdNr-1].setCenter(currentAddressPositons[mapIdNr-1]);
      addressMarker = new google.maps.Marker({
        map: maps[mapIdNr-1],
        position: currentAddressPositons[mapIdNr-1],
        draggable: true
      });

      updateAddressCoordinates(mapIdNr);

      addressMarker.position_changed = function() {
        currentAddressPositons[mapIdNr-1] = addressMarker.getPosition();
        updateAddressCoordinates(mapIdNr);
      };
    } else {
      alert("Geocode was not successful for the following reason: " + status);
    }
  });
}

function updateAddressCoordinates(mapIdNr) {
  // Copy the coordinates into appropriate input fields
  $("#long" + mapIdNr).val(currentAddressPositons[mapIdNr-1].$a);
  $("#lat" + mapIdNr).val(currentAddressPositons[mapIdNr-1].Za);
}

function addNewMap() {
  mapIdNr = parseInt($(this).parent()[0].id.match("[0-9]+"));
  $(this).parent().append('<br /><div class="mapCanvas" id="map_canvas' + mapIdNr + '"></div>');

  initializeGoogleMap(mapIdNr);
  fullAddress = $(this).siblings("input").map(function() { return $(this).val(); }).get().join(", ")  // join all fields for the query
  console.log(fullAddress);  //TODO: The above also joins the empty longitude and latitude fields...
  codeAddress(fullAddress, mapIdNr);

  $(this).hide();
  $(this).next().show();

  return false;
}

function hideTheMap() {
  mapIdNr = parseInt($(this).parent()[0].id.match("[0-9]+"));
  $("#map_canvas" + mapIdNr).slideUp();
  $(this).hide();
  $(this).next().show();
  return false;
}

function showTheMap() {
  mapIdNr = parseInt($(this).parent()[0].id.match("[0-9]+"));
  $("#map_canvas" + mapIdNr).slideDown();
  $(this).hide();
  $(this).prev().show();
  return false;
}

function addRemoverHandle(addressNr) {
  $('#remover' + addressNr).click(function() {
    addressCounter--;
    addressParent = $(this).parent()
    addressParent.slideUp('fast', function() {
      addressParent.remove(); // remove the parent <p></p>
    });
    return false;          // represss page refresh
  });
}

// Set all event handlers when the page is ready
$(document).ready(function() {
  
  $('#addAddress').click(function() {
    if(addressCounter >= 10)   // a hard limit on the number of addresses
      return false;  //TODO: Hide the "Add address" anchor not to confuse the user

    // Clone an existing address field group
    newAddress = $("#address" + (addressCounter++)).clone()
    newAddress.attr("id", "address" + addressCounter);  // change its id
    allInputFields = newAddress.find("input");
    allInputFields.each(function() { $(this).attr("value", "") }); // clear the input values
    allInputFields.each(function() { $(this).attr("name", $(this).attr("name").match("[^0-9]+") + addressCounter) }); // change the ids' prefix numbers
    allInputFields.each(function() {
      currentId = $(this).attr("id");
      if(typeof(currentId) != 'undefined')
        $(this).attr("id", currentId.match("[^0-9]+") + addressCounter);
    });
    
    // Insert it to the page, but hidden for now
    newAddress.hide();
    newAddress.insertBefore("#addAddress"); // insert hidden

    // Handle the google map
    newAddress.find("div").remove();        // remove the google map too
    newAddress.find(".showMap").hide();
    newAddress.find(".hideMap").hide();
    newAddress.find(".addMap").show();
    newAddress.find(".addMap").click(addNewMap);
    newAddress.find(".hideMap").click(hideTheMap);
    newAddress.find(".showMap").click(showTheMap);

    // Add a handle to remove this address
    if(addressCounter == 2)  // we cloned the first address, so we need to add a 'remove' link
      newAddress.append(' | <a href="" id="remover' + addressCounter + '" class="removers">Remove</a>')
    addRemoverHandle(addressCounter);

    // Show the new address fields
    newAddress.slideDown();

    return false;   // stop page refresh
  });

  // Add removers to already existing secondary address
  $('.removers').each(function(ii) {
    addRemoverHandle(ii+2);
  });

  // Turn the form validation on
  $("#submitForm").validate();

  // Add map handlers
  $('.addMap').click(addNewMap);
  $('.hideMap').click(hideTheMap);
  $('.showMap').click(showTheMap);
});
