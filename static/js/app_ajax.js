function like(event, slug, id) {

    event.preventDefault();

    let element = document.getElementById('like');
    let boiler_element = document.getElementById(`like-${id}`);
    let csrftoken = document.getElementById('csrf_token').value;

    $.ajax({
        url: `/product/like/${slug}/${id}`,
        type: 'POST',

        headers: {
            'X-CSRFToken': csrftoken
        },

        success: function (response) {

            if (response.response === 'liked') {

                if (element) {
                    element.src = '/static/images/icons/heart.svg';
                    element.style.marginTop = '-5px';
                }

                if (boiler_element) {
                    boiler_element.src = '/static/images/icons/heart.svg';
                    boiler_element.style.marginTop = '-5px';
                }

                console.log('LIKE');

            } else if (response.response === 'unliked') {

                if (element) {
                    element.src = '/static/images/icons/heart-outline.svg';
                    element.style.marginTop = '0px';
                }

                if (boiler_element) {
                    boiler_element.src = '/static/images/icons/heart-outline.svg';
                    boiler_element.style.marginTop = '0px';
                }

                console.log('UNLIKE');
            }
        },

        error: function (xhr, status, error) {
            console.error("خطا در درخواست:", error);
        }
    });
}

function likes_in_other_sections(event, slug, id, button=null) {

    event.preventDefault();
    event.stopPropagation();

    let element = button.querySelector('.like-icon');
    const csrftoken = document.getElementById('csrf_token').value;

    $.ajax({
        url: `/product/like/${slug}/${id}`,
        type: 'POST',

        headers: {
            'X-CSRFToken': csrftoken
        },

        success: function (response) {

            if (response.response === 'liked') {

                element.src = '/static/images/icons/heart.svg';
                element.style.marginTop = '-5px';
                element.classList.add('liked');

                console.log('LIKE');

            } else if (response.response === 'unliked') {

                element.src = '/static/images/icons/heart-outline.svg';
                element.style.marginTop = '1px';
                element.classList.remove('liked');

                console.log('UNLIKE');
            }
        },

        error: function (xhr, status, error) {
            console.error("خطا در درخواست:", error);
        }
    });
}