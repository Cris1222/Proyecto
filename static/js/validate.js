// The submit button
const SUBMIT = $( "#submit" );
const PASSWORD = $( "#password" );
const PASSWORD_MSG = $( "#password-msg" );
const CONFIRM = $( "#confirm" );
const CONFIRM_MSG = $( "#confirm-msg" );
const EMAIL = $( "#email" );
const EMAIL_MSG = $( "#email-msg" );
function reset_form ( ) {
    PASSWORD_MSG.html( "" );
    PASSWORD_MSG.hide();
    CONFIRM_MSG.html( "" );
    CONFIRM_MSG.hide();
    EMAIL_MSG.html( "" );
    EMAIL_MSG.hide();
    SUBMIT.show();
}
function validate ( ){
    let valid = true;
    reset_form ( );
    SUBMIT.hide();
    if ( !CONFIRM.val() || PASSWORD.val() != CONFIRM.val() ){
        CONFIRM_MSG.html("Contraseñas diferentes");
        CONFIRM_MSG.show();
        valid = false;
    }
    var x = EMAIL.val().trim();
    var atpos = x.indexOf("@");
    var dotpos = x.lastIndexOf(".");
    if ( atpos < 1 || dotpos < atpos + 2 || dotpos + 2 >= x.length ) {
        EMAIL_MSG.html("Correo no valido");
        EMAIL_MSG.show();
        valid = false;
    }
    if ( valid ){reset_form ( );}
$(document).ready ( validate );
PASSWORD.change ( validate );
CONFIRM.change ( validate );
EMAIL.change ( validate );
}