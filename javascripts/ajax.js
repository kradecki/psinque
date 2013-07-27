
//*******************************************************************
// Psinque AJAX API
// 
//*******************************************************************

psinqueAPI_mycard = "/mycard/"

psinqueAPI_addEmail      = psinqueAPI_mycard + "addemail"
psinqueAPI_addPhone      = psinqueAPI_mycard + "addphone"
psinqueAPI_addIM         = psinqueAPI_mycard + "addim"
psinqueAPI_addWWW        = psinqueAPI_mycard + "addwww"
psinqueAPI_addAddress    = psinqueAPI_mycard + "addaddress"

psinqueAPI_removeEmail   = psinqueAPI_mycard + "removeemail"
psinqueAPI_removePhone   = psinqueAPI_mycard + "removephone"
psinqueAPI_removeIM      = psinqueAPI_mycard + "removeim"
psinqueAPI_removeWWW     = psinqueAPI_mycard + "removewww"
psinqueAPI_removeAddress = psinqueAPI_mycard + "removeaddress"

psinqueAPI_updateEmail   = psinqueAPI_mycard + "updateemail"
psinqueAPI_updatePhone   = psinqueAPI_mycard + "updatephone"
psinqueAPI_updateIM      = psinqueAPI_mycard + "updateim"
psinqueAPI_updateWWW     = psinqueAPI_mycard + "updatewww"
psinqueAPI_updateAddress = psinqueAPI_mycard + "updateaddress"

psinqueAPI_updateGeneral = psinqueAPI_mycard + "updategeneral"

//------------------------------

psinqueAPI_permits = "/permits/"

psinqueAPI_addPermit           = psinqueAPI_permits + "addpermit"
psinqueAPI_removePermit        = psinqueAPI_permits + "removepermit"
psinqueAPI_setGeneralPermit    = psinqueAPI_permits + "setgeneralpermit"
psinqueAPI_setIndividualPermit = psinqueAPI_permits + "setindividualpermit"

//------------------------------

psinqueAPI_settings = "/settings/"

psinqueAPI_generateCardDAVLogin = psinqueAPI_settings + "generatecarddavlogin"
psinqueAPI_deleteCardDAVLogin   = psinqueAPI_settings + "deletecarddav"
psinqueAPI_updateSettings       = psinqueAPI_settings + "updatesettings"

//------------------------------
// My Card

function psinqueAddEmail(emailAddress, privacyType, isPrimary, successFunction) {
    psinqueAJAX(psinqueAPI_addEmail, {
                    email: emailAddress,
                    privacy: privacyType,
                    primary: isPrimary,
                }, successFunction);
}

function psinqueAddPhone(phoneNumber, privacyType, phoneType, successFunction) {
    psinqueAJAX(psinqueAPI_addPhone, {
                    phone: phoneNumber,
                    privacy: privacyType,
                    type: phoneType,
                }, successFunction);
}

function psinqueAddIM(imLogin, privacyType, imType, successFunction) {
    psinqueAJAX(psinqueAPI_addIM, {
                    im: imLogin,
                    privacy: privacyType,
                    type: imType,
                }, successFunction);
}

function psinqueAddWWW(wwwAddress, privacyType, wwwType, successFunction) {
    psinqueAJAX(psinqueAPI_addIM, {
                    www: wwwAddress,
                    privacy: privacyType,
                    type: wwwType,
                }, successFunction);
}

function psinqueAddAddress(address, city, postalCode,
                           privacyType, longitude, latitude,
                           successFunction) {
    psinqueAJAX(psinqueAPI_addIM, {
                    address: address,
                    city: city,
                    postal: postalCode,
                    privacy: privacyType,
                    lon: longitude,
                    lat: latitude,
                }, successFunction);
}

function psinqueRemoveEmail(key, successFunction) {
    psinqueRemove(psinqueAPI_removeEmail, key, successFunction);
}

function psinqueRemovePhone(key, successFunction) {
    psinqueRemove(psinqueAPI_removePhone, key, successFunction);
}

function psinqueRemoveIM(key, successFunction) {
    psinqueRemove(psinqueAPI_removeIM, key, successFunction);
}

function psinqueRemoveWWW(key, successFunction) {
    psinqueRemove(psinqueAPI_removeWWW, key, successFunction);
}

function psinqueRemoveAddress(key, successFunction) {
    psinqueRemove(psinqueAPI_removeAddress, key, successFunction);
}

function psinqueUpdateEmail(key, emailAddress, privacyType,
                            successFunction) {
    psinqueAJAX(psinqueAPI_updateEmail, {
                    key: key,
                    email: emailAddress,
                    privacy: privacyType,
                }, successFunction);
}

function psinqueUpdatePhone(key, phoneNumber, privacyType,
                            phoneType, successFunction) {
    psinqueAJAX(psinqueAPI_updatePhone, {
                    key: key,
                    phone: phoneNumber,
                    privacy: privacyType,
                    type: phoneType,
                }, successFunction);
}

function psinqueUpdateIM(key, imLogin, privacyType,
                         imType, successFunction) {
    psinqueAJAX(psinqueAPI_updateIM, {
                    key: key,
                    im: imLogin,
                    privacy: privacyType,
                    type: imType,
                }, successFunction);
}

function psinqueUpdateWWW(key, wwwAddress, privacyType,
                          wwwType, successFunction) {
    psinqueAJAX(psinqueAPI_updateIM, {
                    key: key,
                    www: wwwAddress,
                    privacy: privacyType,
                    type: wwwType,
                }, successFunction);
}

function psinqueUpdateAddress(key, address, city, postalCode, country,
                              privacyType, longitude, latitude, successFunction) {
    psinqueAJAX(psinqueAPI_updateIM, {
                    key: key,
                    address: address,
                    city: city,
                    postal: postalCode,
                    country: country,
                    privacy: privacyType,
                    lon: longitude,
                    lat: latitude,
                }, successFunction);
}

function psinqueUpdateGeneral(givenNames, givenNamesRomanization,
                              familyNames, familyNamesRomanization,
                              companyName, companyNameRomanization,
                              birthday, birthmonth, birthyear, gender,
                              successFunction) {
    psinqueAJAX(psinqueAPI_updateGeneral, {
                    givennames: givenNames,
                    givenroman: givenNamesRomanization,
                    familynames: familyNames,
                    familyroman: familyNamesRomanization,
                    company: companyName,
                    companyroman: companyNameRomanization,
                    day: birthday,
                    month: birthmonth,
                    year: birthyear,
                    gender: gender,
                }, successFunction);
}

//------------------------------
// Permits

function psinqueAddPermit(name, index, successFunction) {
    psinqueAJAX_HTML(psinqueAPI_addPermit, {
                         name: name,
                         index: index,
                     }, successFunction);
}

function psinqueRemovePermit(permitKey, successFunction) {
    psinqueRemove(psinqueAPI_removePermit, permitKey, successFunction);
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

function psinqueSetIndividualPermit(permitKey, canView, successFunction) {
    psinqueAJAX(psinqueAPI_setIndividualPermit, {
                    key: permitKey,
                    canview: canView,
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
    psinqueRemove(psinqueAPI_deleteCardDAVLogin, cardDAVKey, successFunction);
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

function psinqueRemove(url, key, successFunction) {
    psinqueAJAX(url, {
                    key: key,
                }, successFunction);
}

//------------------------------

window.ajaxTransaction = false;
window.ajaxCounter = 0;

$(document).ready(function() {
    
    $(document).ajaxError(function(event, jqXHR, settings, exception) {
        stopLogoAnimation();
//         window.ajaxCounter = 0;
        alert("Uknown error occured while performing operation: " + exception);
        console.log(settings);
    });
    
});

