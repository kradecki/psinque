
function showRow(tr) {
    $(tr)
        .show()
        .find('td')
        .wrapInner('<div style="display: none;" />')
        .parent()
        .find('td > div')
        .slideDown(700, function(){
            var $set = $(this);
            $set.replaceWith($set.contents());
        });
}

$(function() {
  
  uiInitializeCheckboxes();
  
  $(document).tooltip({
      position: {
          my: "left+20 top+5",
          at: "left bottom",
          collision: "flipfit" 
  }});
  
  $('#password').passStrengthify({
      element: $('#passwordstrength'),
      rawEntropy: true,
      minimum: 5,
  });
  $("#password").keyup(function() {
      $("tr.passwordinfo").show();
  });
  $("#password").blur(function() {
      $("tr.passwordinfo").hide();
  });
  
  $("#logomyspace").click(function() {
    
      console.log("Click");
    
      showRow('tr.username');
      $("#username").html("MySpace ID")
    
      return false;
  });
  
});
