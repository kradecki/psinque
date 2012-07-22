
// Global Google Map variables
var geocoder;
var map;
var addressMarker;
var currentAddressPositon;

function initializeGoogleMap() {
  currentAddressPositon = new google.maps.LatLng(-34.397, 150.644)
  geocoder = new google.maps.Geocoder();
  var mapOptions = {
    center: currentAddressPositon,
    zoom: 12,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
}

function codeAddress(address) {
  geocoder.geocode( { 'address': address }, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      currentAddressPositon = results[0].geometry.location;
      map.setCenter(currentAddressPositon);
      addressMarker = new google.maps.Marker({
        map: map,
        position: currentAddressPositon,
        draggable: true
      });

      updateAddressCoordinates()

      addressMarker.position_changed = function() {
        currentAddressPositon = addressMarker.getPosition();
        updateAddressCoordinates();
      };
      
    } else {
      alert("Geocode was not successful for the following reason: " + status);
    }
  });
}

function updateAddressCoordinates() {
  // Copy the coordinates into appropriate input fields
  $("#coord1").val(currentAddressPositon.$a);
  $("#coord2").val(currentAddressPositon.Za);
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
$(document).ready(function(){
  
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

  $('.findOnAMap').click(function() {
    $(this).parent().append('<br /><div id="map_canvas"></div><br /><label>Longitude:</label><input type="text" name="coord1" id="coord1" disabled="disabled" /><br /><label>Latitude:</label><input type="text" name="coord2" id="coord2" disabled="disabled" />');
    $(this).text("");  // hide the label, because removing the map doesn't work for now
    initializeGoogleMap();
    fullAddress = $("#address1 > input").map(function() { return $(this).val(); }).get().join(", ")  // join all fields for the query
    codeAddress(fullAddress);
    return false;
  });
  
});
