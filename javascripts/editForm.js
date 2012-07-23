
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
  console.log("hide map");
  mapIdNr = parseInt($(this).parent()[0].id.match("[0-9]+"));
  console.log(mapIdNr)
  $("#map_canvas" + mapIdNr).slideUp();
  $(this).hide();
  $(this).next().show();
  return false;
}

function showTheMap() {
  console.log("show map")
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

    addressCounter++;

    // Create and insert a new address field
    newElement = document.createElement("p");
    newElement.id = "address" + addressCounter;
    newElement.innerHTML = '<label>Address ' + addressCounter + ':</label> <input type="text" name="address' + addressCounter + '" class="required" /><a href="" id="remover' + addressCounter + '">Remove</a>';
    this.parentNode.insertBefore(newElement, this);

    // Add a handle to remove this address
    addRemoverHandle(addressCounter);

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
