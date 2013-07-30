
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
  
  $(document).tooltip({
      position: {
          my: "left+20 top+5",
          at: "left bottom",
          collision: "flipfit" 
  }});
  
  $("#logomyspace").click(function() {
    
      console.log("Click");
    
      showRow('tr.hiddenelements');
      $("#username").html("MySpace ID")
    
      return false;
  });
  
});
