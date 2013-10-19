
$(function() {
  
    $("input[type=text]").unbind('change');
    $("input[type=text]").unbind('keyup');

    $(".myspacesignin").click(function() {

          myspaceuser = $("#myspaceuser").val();
          
          if(myspaceuser == "")
              return;
          
          loginurl = "http://www.psinque.com/_ah/login_redir?claimid=http://www.myspace.com/" + myspaceuser + "&continue=http://www.psinque.com/profile/view";
          
          // Go!
          window.location.replace(loginurl);
    });
  
    $(".openidsignin").click(function() {

          openidlink = $("#openidlink").val();
          
          if(openidlink == "")
              return;
          
          loginurl = "http://www.psinque.com/_ah/login_redir?claimid="
          + openidlink + "&continue=http://www.psinque.com/profile/view";
          
          // Go!
          window.location.replace(loginurl);
    });
  
});
