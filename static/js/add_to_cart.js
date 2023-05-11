$('.addToCartBtn').click(function (event) {
    event.preventDefault();
    
    const form_data = {
        item_id: $(this).closest(".item_data").find('.item_id').val(),
        csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
    }
    $.ajax({
        type: 'POST',
        url: '/add',
        data: form_data,
        datatype: "datatype",
        success: function () {
            alert("Product added to cart")
        }
    })
});