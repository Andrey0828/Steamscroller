function openTab(evt, tabName) {
    var i, tabcontent, tablinks, wantToClose;
    wantToClose = evt.currentTarget.className.includes("active");

    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    if (!wantToClose) {
        document.getElementById(tabName).style.display = "block";
        evt.currentTarget.className += " active";

        window.moveBy(0, -document.getElementById(tabName).offsetHeight);
        console.log(document.getElementById(tabName).offsetHeight);
    }
}