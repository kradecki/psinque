
//*******************************************************************
// Psinque AJAX API
// 
//*******************************************************************

psinqueAPI_mycard = "/mycard/"
psinqueAPI_removeEmail   = psinqueAPI_mycard + "removeemail"
psinqueAPI_updateGeneral = psinqueAPI_mycard + "updategeneral"
psinqueAPI_updateEmail   = psinqueAPI_mycard + "updateemail"
psinqueAPI_addEmail      = psinqueAPI_mycard + "addemail"

psinqueAPI_permits = "/permits/"
psinqueAPI_removePermit     = psinqueAPI_permits + "removepermit"
psinqueAPI_setGeneralPermit = psinqueAPI_permits + "setgeneralpermit"
psinqueAPI_setEmailPermit   = psinqueAPI_permits + "setemailpermit"
psinqueAPI_addPermit        = psinqueAPI_permits + "addpermit"

//------------------------------
// My Card

function psinqueRemovePermit(emailKey, successFunction) {
    $.get(psinqueAPI_removeEmail, {
            key: emailKey,
        }, successFunction);
}

function psinqueUpdateGeneral(firstName, lastName,
                              successFunction) {
    $.get(psinqueAPI_updateGeneral, {
              firstname: firstName,
              lastname: lastName,
          }, successFunction);
}

function psinqueUpdateEmail(emailKey, emailAddress, typeOfEmail,
                            successFunction) {
    $.get(psinqueAPI_updateEmail, {
              key: emailKey,
              email: emailAddress,
              type: typeOfEmail,
          }, successFunction);
}

function psinqueAddEmail(emailAddress, typeOfEmail,
                         successFunction) {
    $.get(psinqueAPI_addEmail, {
              email: emailAddress,
              type: typeOfEmail,
          }, successFunction);
}

//------------------------------
// Permits

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
