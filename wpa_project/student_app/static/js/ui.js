// Scripts to deal with UI functionality

const mobileWidth = 770;  // Size at which we will use mobile settings for UI

$(document).ready(function() {
    var menuItems = $(".navbar-nav");   // Navigation bar's contents

    // Change UI when window is resized
    window.onresize = function() {
        /*// Show navigation links if we're over a certain width
        if (window.innerWidth > mobileWidth) {
            menuItems.show();
            //$(".navbar-custom").css("{ float: left, clear: '' }");
        }
        else {
            menuItems.hide();
        }*/
    }

    // Hide and show menu items when button is clicked on smaller screens
    $("#menu-button").on("click", function() {
        if (menuItems.css("display") == "none")
            menuItems.show();
        else
            menuItems.hide();
    })
});