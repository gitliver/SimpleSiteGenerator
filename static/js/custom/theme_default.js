// console.log('Welcome');

/**
 * Copy link on clicking, and show a quick message
 */
function allowCopy() {

    // Get elts
    let dots = document.getElementById("ssg-threedots");
    let menu = document.getElementById("ssg-dropdown-menu");
    let btn = document.getElementById("ssg-copybutton");
    let tt = document.getElementById("ssg-tt");

    // Toggle menu on click
    dots.onclick = function() {
        // console.log(menu);
        if (menu.classList.contains('ssg-vis-hide')) {
            menu.classList.remove('ssg-vis-hide');
            menu.classList.add('ssg-vis-show');
        } else {
            menu.classList.remove('ssg-vis-show');
            menu.classList.add('ssg-vis-hide');
        }
    }

    // When the user clicks on the button, copy window URL
    // close the menu, and show quick tooltip
    btn.onclick = function() {
        navigator.clipboard.writeText(window.location.href);
        menu.classList.remove('ssg-vis-show');
        menu.classList.add('ssg-vis-hide');
        tt.style.display = "block";
        setTimeout(() => {
            tt.style.display = "none";
        }, "200");
    }
}
