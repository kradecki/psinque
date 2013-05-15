acceptPsinque = function(parentRow) {

    psinqueKey = parentRow.find(".keys").val();

    groupCounter = 0;
    parentRow.find(".groupSelectors :selected").each(function(i, selected) {
        groupCounter++;
    });
    console.log(groupCounter);

    parentRow.find(".groupSelectors :selected").each(function(i, selected) {
        executeAJAX("/decisions/addtogroup?key=" + psinqueKey +
                                         "&group=" + $(selected).text(),
                    function() {
                        groupCounter--;
                        if(groupCounter == 0) {
                            executeAJAX("/decisions/accept?key=" + psinqueKey,
                                function() {
                                    parentRow.slideUp(function() {
                                        $(this).remove();
                                    });
                                });
                        }
                    });
    });
}

rejectPsinque = function(parentRow) {
    executeAJAX("/decisions/reject?key=" + parentRow.find(".keys").val(),
        function() {
            parentRow.slideUp(function() {
                $(this).remove();
            });
        });
}

$(document).ready(function() {
    
//   $(".groupSelectors").dropdownchecklist( { icon: {}, width: 150 } );
//   $(".groupSelectors").select2();
  
  $(".rejectButtons").click(function() {
      rejectPsinque($(this).parent().parent());
  });
  
  $(".acceptButtons").click(function() {
      acceptPsinque($(this).parent().parent());
  });
  
});