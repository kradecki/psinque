
// Global Google Map variables
var geocoder;
var map;

function initializeGoogleMap() {
  geocoder = new google.maps.Geocoder();
  var mapOptions = {
    center: new google.maps.LatLng(-34.397, 150.644),
    zoom: 12,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
}

function codeAddress(address) {
  geocoder.geocode( { 'address': address }, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      map.setCenter(results[0].geometry.location);
      position = results[0].geometry.location;
      var marker = new google.maps.Marker({
        map: map,
        position: position
      });
      $("#coord1").val(position.$a);
      $("#coord2").val(position.Za);
    } else {
      alert("Geocode was not successful for the following reason: " + status);
    }
  });
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

$(document).ready(function(){
  $('#addAddress').click(function() {

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

  // Activate a Google Map
  $('.findOnAMap').click(function() {
    $(this).parent().append('<br /><div id="map_canvas"></div><br /><label>Primary coordinates:</label><input type="text" name="coord1" id="coord1" /><input type="text" name="coord2" id="coord2" />');
    $(this).text("Hide the map (not working yet)");
    initializeGoogleMap();
    codeAddress($("#address1 > input").val());
    return false;
  });
});