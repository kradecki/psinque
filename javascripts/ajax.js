
//*******************************************************************
// Psinque AJAX API
// 
//*******************************************************************

psinqueAPI_profile = "/profile/"

psinqueAPI_addEmail      = psinqueAPI_profile + "addemail"
psinqueAPI_addPhone      = psinqueAPI_profile + "addphone"
psinqueAPI_addIM         = psinqueAPI_profile + "addim"
psinqueAPI_addWWW        = psinqueAPI_profile + "addwww"
psinqueAPI_addAddress    = psinqueAPI_profile + "addaddress"

psinqueAPI_removeEmail   = psinqueAPI_profile + "removeemail"
psinqueAPI_removePhone   = psinqueAPI_profile + "removephone"
psinqueAPI_removeIM      = psinqueAPI_profile + "removeim"
psinqueAPI_removeWWW     = psinqueAPI_profile + "removewww"
psinqueAPI_removeAddress = psinqueAPI_profile + "removeaddress"

psinqueAPI_updateEmail   = psinqueAPI_profile + "updateemail"
psinqueAPI_updatePhone   = psinqueAPI_profile + "updatephone"
psinqueAPI_updateIM      = psinqueAPI_profile + "updateim"
psinqueAPI_updateWWW     = psinqueAPI_profile + "updatewww"
psinqueAPI_updateAddress = psinqueAPI_profile + "updateaddress"

psinqueAPI_updateGeneral = psinqueAPI_profile + "updategeneral"

//------------------------------

psinqueAPI_personas = "/personas/"

psinqueAPI_addPersona          = psinqueAPI_personas + "addpersona"
psinqueAPI_removePersona       = psinqueAPI_personas + "removepersona"
psinqueAPI_setGeneralPersona   = psinqueAPI_personas + "setgeneral"
psinqueAPI_setIndividualPermit = psinqueAPI_personas + "setindividualpermit"

//------------------------------

psinqueAPI_settings = "/settings/"

psinqueAPI_generateCardDAVLogin = psinqueAPI_settings + "generatecarddavlogin"
psinqueAPI_deleteCardDAVLogin   = psinqueAPI_settings + "deletecarddav"
psinqueAPI_updateSettings       = psinqueAPI_settings + "updatesettings"

//------------------------------

psinqueAPI_psinques = "/psinques/"

psinqueAPI_searchEmail       = psinqueAPI_psinques + "searchemail"
psinqueAPI_addPublicPsinque  = psinqueAPI_psinques + "addpublic"
psinqueAPI_removeContact     = psinqueAPI_psinques + "removecontact"
psinqueAPI_requestPrivate    = psinqueAPI_psinques + "requestprivate"
psinqueAPI_acceptRequest     = psinqueAPI_psinques + "acceptrequest"
psinqueAPI_rejectRequest     = psinqueAPI_psinques + "rejectrequest"

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
    psinqueAJAX(psinqueAPI_addWWW, {
                    www: wwwAddress,
                    privacy: privacyType,
                    type: wwwType,
                }, successFunction);
}

function psinqueAddAddress(address, city, postalCode, country,
                           privacyType, longitude, latitude,
                           successFunction) {
    psinqueAJAX(psinqueAPI_addAddress, {
                    address: address,
                    city: city,
                    postal: postalCode,
                    country: country,
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
    psinqueAJAX(psinqueAPI_updateWWW, {
                    key: key,
                    www: wwwAddress,
                    privacy: privacyType,
                    type: wwwType,
                }, successFunction);
}

function psinqueUpdateAddress(key, address, city, postalCode, country,
                              privacyType, longitude, latitude, successFunction) {
    psinqueAJAX(psinqueAPI_updateAddress, {
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
// Personas

function psinqueAddPersona(name, index, successFunction) {
    psinqueAJAX_HTML(psinqueAPI_addPersona, {
                         name: name,
                         index: index,
                     }, successFunction);
}

function psinqueRemovePersona(personaKey, successFunction) {
    psinqueRemove(psinqueAPI_removePersona, personaKey, successFunction);
}

function psinqueSetGeneralPersona(personaKey, canViewGivenNames,
                                 canViewFamilyNames, canViewBirthday,
                                 canViewGender, successFunction) {
    psinqueAJAX(psinqueAPI_setGeneralPersona, {
                    key: personaKey,
                    givennames: canViewGivenNames,
                    familynames: canViewFamilyNames,
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

function psinqueSearchEmail(email, successFunction) {
    psinqueAJAX(psinqueAPI_searchEmail, {
                    email: email,
                }, successFunction);
}

function psinqueAddPublicPsinque(friendsProfile, successFunction) {
    psinqueAJAX_HTML(psinqueAPI_addPublicPsinque, {
                    key: friendsProfile,
                }, successFunction);
}

function psinqueRemoveContact(contactKey, successFunction) {
    psinqueAJAX(psinqueAPI_removeContact, {
                    key: contactKey,
                }, successFunction);
}

function psinqueRequestPrivate(contactKey, successFunction) {
    psinqueAJAX(psinqueAPI_requestPrivate, {
                    key: contactKey,
                }, successFunction);
}

function psinqueAcceptRequest(psinqueKey, successFunction) {
    psinqueAJAX(psinqueAPI_acceptRequest, {
                    key : psinqueKey,
                }, successFunction);
}

function psinqueRejectRequest(psinqueKey, successFunction) {
    psinqueAJAX(psinqueAPI_rejectRequest, {
                    key : psinqueKey,
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
    
    if((!window.ajaxTransaction) && (window.ajaxCounter != 0))
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

