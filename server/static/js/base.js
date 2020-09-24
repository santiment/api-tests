document.addEventListener("DOMContentLoaded", function(e) {
  var collapsibleElements = document.getElementsByClassName("collapsible");

  for (var i = 0; i < collapsibleElements.length; i++) {
    collapsibleElements[i].addEventListener("click", function() {
      this.classList.toggle("active");
      var content = this.nextElementSibling;

      if (content.style.display === "block") {
        content.style.display = "none";
      } else {
        content.style.display = "block";
      }
    });
  }
});