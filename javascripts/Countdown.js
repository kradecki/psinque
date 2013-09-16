
$(function() {
  
    $("div.tableclock").countdown("2013/10/26", function(event) {
        var $this = $(this);
        switch(event.type) {
            case "seconds":
            case "minutes":
            case "hours":
            case "days":
            case "weeks":
            case "daysLeft":
              $this.find('label#'+event.type).html(event.value);
              break;
            case "finished":
              $this.hide();
              break;
        }
    });
    
    $("#content").position({
        my: "center",
        at: "center",
        of: window
    });
  
});
