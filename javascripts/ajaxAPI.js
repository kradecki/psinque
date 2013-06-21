
//*******************************************************************
// Psinque AJAX API
// 
//*******************************************************************

psinqueAPI_permits = "/permits/"
psinqueAPI_removePermit     = psinqueAPI_permits + "removepermit"
psinqueAPI_setGeneralPermit = psinqueAPI_permits + "setgeneralpermit"
psinqueAPI_setEmailPermit   = psinqueAPI_permits + "setemailpermit"
psinqueAPI_addPermit        = psinqueAPI_permits + "addpermit"

function psinqueRemovePermit(permitKey, successFunction) {
    $.get(psinqueAPI_removePermit, {
            key: permitKey,
        }, successFunction);
}

function psinqueSetGeneralPermit(permitKey, canViewFirstNames,
                                 canViewLastNames, canViewBirthday,
                                 canViewGender, successFunction) {
    $.get(psinqueAPI_setGeneralPermit, {
              key: permitKey,
              firstnames: canViewFirstNames,
              lastnames: canViewLastNames,
              birthday: canViewBirthday,
              gender: canViewGender,
          }, successFunction);
}

function psinqueSetEmailPermit(permitKey, canView, successFunction) {
    $.get(psinqueAPI_setEmailPermit, {
              key: permitKey,
              canview: canView,
          }, successFunction);
}

function psinqueAddPermit(name, index, successFunction) {
    $.get(psinqueAPI_addPermit, {
                  name: name,
                  index: index,
              }, successFunction);
}

function executeAJAX(query, done) {
    $.ajax(query)
        .done(function(data) {
            parsedJSON = $.parseJSON(data);
            if(parsedJSON["status"] != 0) {
                alert("Error while performing operation: " + parsedJSON["message"]);
            } else {
                done(parsedJSON);
            }
        })
}
