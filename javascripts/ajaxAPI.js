
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
    psinqueAJAX(psinqueAPI_removeEmail, {
                    key: emailKey,
                }, function() {
                    psinqueDecreaseAJAXCounter();
                    successFunction();
                });
}

function psinqueUpdateGeneral(firstName, lastName,
                              successFunction) {
    psinqueAJAX(psinqueAPI_updateGeneral, {
                    firstname: firstName,
                    lastname: lastName,
                }, successFunction);
}

function psinqueUpdateEmail(emailKey, emailAddress, typeOfEmail,
                            successFunction) {
    psinqueAJAX(psinqueAPI_updateEmail, {
                    key: emailKey,
                    email: emailAddress,
                    type: typeOfEmail,
                }, successFunction);
}

function psinqueAddEmail(emailAddress, typeOfEmail,
                         successFunction) {
    psinqueAJAX(psinqueAPI_addEmail, {
                    email: emailAddress,
                    type: typeOfEmail,
                }, successFunction);
}

//------------------------------
// Permits

function psinqueRemovePermit(permitKey, successFunction) {
    psinqueAJAX(psinqueAPI_removePermit, {
                    key: permitKey,
                }, successFunction);
}

function psinqueSetGeneralPermit(permitKey, canViewFirstNames,
                                 canViewLastNames, canViewBirthday,
                                 canViewGender, successFunction) {
    psinqueAJAX(psinqueAPI_setGeneralPermit, {
                    key: permitKey,
                    firstnames: canViewFirstNames,
                    lastnames: canViewLastNames,
                    birthday: canViewBirthday,
                    gender: canViewGender,
                }, successFunction);
}

function psinqueSetEmailPermit(permitKey, canView, successFunction) {
    psinqueAJAX(psinqueAPI_setEmailPermit, {
                    key: permitKey,
                    canview: canView,
                }, successFunction);
}

function psinqueAddPermit(name, index, successFunction) {
    psinqueAJAX(psinqueAPI_addPermit, {
                    name: name,
                    index: index,
                }, successFunction);
}

//------------------------------
// General AJAX

window.ajaxCounter = 0;

function psinqueAJAX(url, parameters, successFunction) {
    psinqueIncreaseAJAXCounter();
    $.get(url, parameters, function(data) {
        psinqueDecreaseAJAXCounter();
        if(successFunction != undefined)
            successFunction(data);
    });
}

function psinqueAjaxSafeguard() {
    if(window.ajaxCounter == 0) {
        startLogoAnimation();
        return true;
    } else
        return false;
}

function psinqueIncreaseAJAXCounter() {
    window.ajaxCounter++;
}

function psinqueDecreaseAJAXCounter() {
    window.ajaxCounter--;
    if(window.ajaxCounter == 0) {
        stopLogoAnimation();
        unmarkChangedFields();
    }
}

$(document).ready(function() {
    
    $(document).ajaxError(function() {
        stopLogoAnimation();
        window.ajaxCounter = 0;
        alert("Uknown error occured while performing operation.");
    });
    
});

