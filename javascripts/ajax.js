
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

psinqueAPI_settings = "/settings/"
psinqueAPI_generateCardDAVLogin = psinqueAPI_settings + "generatecarddavlogin"
psinqueAPI_deleteCardDAVLogin   = psinqueAPI_settings + "deletecarddav"
psinqueAPI_updateSettings       = psinqueAPI_settings + "updatesettings"

//------------------------------
// My Card

function psinqueRemoveEmail(emailKey, successFunction) {
    psinqueAJAX(psinqueAPI_removeEmail, {
                    key: emailKey,
                }, successFunction);
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
    psinqueAJAX_HTML(psinqueAPI_addPermit, {
                         name: name,
                         index: index,
                     }, successFunction);
}

//------------------------------
// Settings

function psinqueGenerateCardDAVLogin(cardDAVName, successFunction) {
    psinqueAJAX(psinqueAPI_generateCardDAVLogin, {
                   name: cardDAVName,
                }, successFunction);
}

function psinqueDeleteCardDAVLogin(cardDAVKey, successFunction) {
    psinqueAJAX(psinqueAPI_deleteCardDAVLogin, {
                   key: cardDAVKey,
                }, successFunction);
}

function psinqueUpdateSettings(emailNotifications,
                               notifyStops, notifyAsks,
                               notifyAccepts, notifyRejects,
                               notifyRevokes,
                               language, syncCardDAV,
                               newsletter, successFunction) {
    psinqueAJAX(psinqueAPI_updateSettings, {
                    emailnotifications: emailNotifications,
                    notifystops: notifyStops,
                    notifyasks: notifyAsks,
                    notifyaccepts: notifyAccepts,
                    notifyrejects: notifyRejects,
                    notifyrevokes: notifyRevokes,
                    language: language,
                    synccarddav: syncCardDAV,
                    newsletter: newsletter,
                }, successFunction);
}

//------------------------------
// General AJAX

window.ajaxTransaction = false;
window.ajaxCounter = 0;

function psinqueAjaxTransactionStart() {
    window.ajaxTransaction = true;
}

function psinqueAjaxTransactionStop() {
    window.ajaxTransaction = false;
}

function psinqueAJAX(url, parameters, successFunction) {
  
    if((!window.ajaxTransaction) && (window.ajaxCounter != 0))
        return;
    
    psinqueIncreaseAJAXCounter();
    
    $.getJSON(url, parameters, function(data) {
        psinqueDecreaseAJAXCounter();
        if(data["status"] != 0) {
            alert("An error occured while performing operation: " + data["message"]);
        } else if(successFunction != undefined) {
            successFunction(data);
        }
    });
}

function psinqueAJAX_HTML(url, parameters, successFunction) {
    
    if(!psinqueAjaxSafeguard())
        return;
    
    psinqueIncreaseAJAXCounter();
    
    $.get(url, parameters, function(data) {
        psinqueDecreaseAJAXCounter();
        successFunction(data);
    }, "html");
}

function psinqueIncreaseAJAXCounter() {
    window.ajaxCounter++;
    startLogoAnimation();
}

function psinqueDecreaseAJAXCounter() {
    window.ajaxCounter--;
    if(window.ajaxCounter == 0) {
        stopLogoAnimation();
        unmarkChangedFields();
    }
}

$(document).ready(function() {
    
    $(document).ajaxError(function(event, jqXHR, settings, exception) {
        stopLogoAnimation();
        window.ajaxCounter = 0;
        alert("Uknown error occured while performing operation: " + exception);
        console.log(jqXHR.responseText);
    });
    
});

