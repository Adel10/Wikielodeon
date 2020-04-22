/*
This function is triggered on hover of any anchor tag element
performs a call to the backend /pagePreview function which will return a page back to be displayed on the UI
getJSON passes three values which help determine what page to grab and if it is a link that we want to have a pagePreview for

If it is successful it will return back data and we append the body's content to the div to be displayed
change the div's coordinates to that of where the anchor tag is on the page and show the element on the UI
 */
$(function() {
          $("a").bind('mouseover', function(e) {
              var tag = e.currentTarget;
            $.getJSON('/pagePreview', {
                    currentTag: tag.pathname,
                    isDeleteBtn : tag.hash,
                    isRikiLink: tag.text
                },

                function(data) {
                    $("#pagePreview").html(data.result);

                    const result = document.getElementById('pagePreview');

                    result.style.left = e.currentTarget.offsetLeft + "px";
                    result.style.top = parseInt(e.currentTarget.offsetTop)*1.15 + "px";
                    result.style.display = "block";
                });
            return false;
          });
        });

/*
Once the user is no longer hovering over the anchor tag, we want to hide the div again
all this function does is binds a mouseout event to every anchor tag which will simply hide the page preview div.
 */
$(function() {
          $("a").bind('mouseout', function(e) {
                var result = document.getElementById('pagePreview');
                result.style.display = "none";
            return false;
          });
        });
