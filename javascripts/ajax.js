
//*******************************************************************
// Psinque AJAX API
// 
//*******************************************************************

psinqueAPI_profile = "/profile/"

psinqueAPI_addEmail       = psinqueAPI_profile + "addemail"
psinqueAPI_addPhone       = psinqueAPI_profile + "addphone"
psinqueAPI_addIM          = psinqueAPI_profile + "addim"
psinqueAPI_addWWW         = psinqueAPI_profile + "addwww"
psinqueAPI_addAddress     = psinqueAPI_profile + "addaddress"
psinqueAPI_addNickname    = psinqueAPI_profile + "addnickname"
psinqueAPI_addCompany     = psinqueAPI_profile + "addcompany"

psinqueAPI_removeEmail    = psinqueAPI_profile + "removeemail"
psinqueAPI_removePhone    = psinqueAPI_profile + "removephone"
psinqueAPI_removeIM       = psinqueAPI_profile + "removeim"
psinqueAPI_removeWWW      = psinqueAPI_profile + "removewww"
psinqueAPI_removeAddress  = psinqueAPI_profile + "removeaddress"
psinqueAPI_removePhoto    = psinqueAPI_profile + "removephoto"
psinqueAPI_removeNickname = psinqueAPI_profile + "removenickname"
psinqueAPI_removeCompany  = psinqueAPI_profile + "removecompany"

psinqueAPI_updateEmail    = psinqueAPI_profile + "updateemail"
psinqueAPI_updatePhone    = psinqueAPI_profile + "updatephone"
psinqueAPI_updateIM       = psinqueAPI_profile + "updateim"
psinqueAPI_updateWWW      = psinqueAPI_profile + "updatewww"
psinqueAPI_updateAddress  = psinqueAPI_profile + "updateaddress"
psinqueAPI_updateNickname = psinqueAPI_profile + "updatenickname"
psinqueAPI_updateCompany  = psinqueAPI_profile + "updatecompany"

psinqueAPI_updateGeneral  = psinqueAPI_profile + "updategeneral"

//------------------------------

psinqueAPI_personas = "/personas/"

psinqueAPI_addPersona          = psinqueAPI_personas + "addpersona"
psinqueAPI_removePersona       = psinqueAPI_personas + "removepersona"
psinqueAPI_setGeneralPersona   = psinqueAPI_personas + "setgeneral"
psinqueAPI_setIndividualPermit = psinqueAPI_personas + "setindividualpermit"
psinqueAPI_enablePublic        = psinqueAPI_personas + "enablepublic"

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
psinqueAPI_addGroup          = psinqueAPI_psinques + "addgroup"
psinqueAPI_changeGroup       = psinqueAPI_psinques + "changegroup"
psinqueAPI_changePersona     = psinqueAPI_psinques + "changepersona"
psinqueAPI_addIncoming       = psinqueAPI_psinques + "addincoming"

//------------------------------
// Profile

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

function psinqueAddNickname(nickname, successFunction) {
    psinqueAJAX(psinqueAPI_addNickname, {
                    nickname: nickname,
                }, successFunction);
}


function psinqueAddCompany(company, position, successFunction) {
    psinqueAJAX(psinqueAPI_addCompany, {
                    company: company,
                    position: position,
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

function psinqueRemovePhoto(key, successFunction) {
    psinqueRemove(psinqueAPI_removePhoto, key, successFunction);
}

function psinqueRemoveNickname(key, successFunction) {
    psinqueRemove(psinqueAPI_removeNickname, key, successFunction);
}

function psinqueRemoveCompany(key, successFunction) {
    psinqueRemove(psinqueAPI_removeCompany, key, successFunction);
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

function psinqueUpdateNickname(key, nickname, successFunction) {
    psinqueAJAX(psinqueAPI_updateNickname, {
                    key: key,
                    nickname: nickname,
                }, successFunction);
}


function psinqueUpdateCompany(key, company, position, successFunction) {
    psinqueAJAX(psinqueAPI_updateCompany, {
                    key: key,
                    company: company,
                    position: position,
                }, successFunction);
}

function psinqueUpdateGeneral(prefix, givenNames, givenNamesRomanization,
                              familyNames, familyNamesRomanization, suffix,
                              companyName, companyNameRomanization,
                              birthday, birthmonth, birthyear, gender,
                              successFunction) {
    psinqueAJAX(psinqueAPI_updateGeneral, {
                    prefix: prefix,
                    givennames: givenNames,
                    givenroman: givenNamesRomanization,
                    familynames: familyNames,
                    familyroman: familyNamesRomanization,
                    suffix: suffix,
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

function psinqueSetGeneralPersona(personaKey, personaName,
                                  canViewPrefix,
                                  canViewGivenNames, canViewGivenNamesRoman,
                                  canViewFamilyNames, canViewFamilyNamesRoman,
                                  canViewSuffix,
                                  canViewBirthday,
                                  canViewGender, company, nickname,
                                  photoKey,
                                  successFunction) {
    psinqueAJAX(psinqueAPI_setGeneralPersona, {
                    key: personaKey,
                    name: personaName,
                    prefix: canViewPrefix,
                    givennames: canViewGivenNames,
                    givennamesroman: canViewGivenNamesRoman,
                    familynames: canViewFamilyNames,
                    familynamesroman: canViewFamilyNamesRoman,
                    suffix: canViewSuffix,
                    birthday: canViewBirthday,
                    gender: canViewGender,
                    company: company,
                    nickname: nickname,
                    photo: photoKey,
                }, successFunction);
}

function psinqueSetIndividualPermit(permitKey, canView, successFunction) {
    psinqueAJAX(psinqueAPI_setIndividualPermit, {
                    key: permitKey,
                    canview: canView,
                }, successFunction);
}

function psinqueEnablePublic(enable, successFunction) {
    psinqueAJAX(psinqueAPI_enablePublic, {
                    enable: enable,
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
// Psinques

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
    psinqueAJAX_HTML(psinqueAPI_acceptRequest, {
                    key : psinqueKey,
                }, successFunction);
}

function psinqueRejectRequest(psinqueKey, successFunction) {
    psinqueAJAX(psinqueAPI_rejectRequest, {
                    key : psinqueKey,
                }, successFunction);
}

function psinqueAddGroup(groupName, successFunction) {
    psinqueAJAX(psinqueAPI_addGroup, {
                    name : groupName,
                }, successFunction);
}

function psinqueChangeGroup(contactKey, groupKey, successFunction) {
    psinqueAJAX(psinqueAPI_changeGroup, {
                    contact: contactKey,
                    group: personaKey,
                }, successFunction);
}

function psinqueChangePersona(contactKey, personaKey, successFunction) {
    psinqueAJAX(psinqueAPI_changePersona, {
                    contact: contactKey,
                    persona: personaKey,
                }, successFunction);
}

function psinqueAddIncoming(contactKey, successFunction) {
    psinqueAJAX_HTML(psinqueAPI_addIncoming, {
                    key: contactKey,
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
            uiShowErrorMessage("An error occured while performing operation: " + data["message"]);
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
    uiStartLogoAnimation();
}

function psinqueDecreaseAJAXCounter() {
    window.ajaxCounter--;
    if(window.ajaxCounter == 0) {
        uiStopLogoAnimation();
        uiUnmarkChangedFields();
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
        uiStopLogoAnimation();
        window.ajaxCounter--;
        uiShowErrorMessage("Uknown error occured while performing operation: " + exception);
    });
    
});

