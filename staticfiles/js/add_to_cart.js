// Add to cart

$(document).on("click", ".add-to-cart", function () {
  var _vm = $(this);
  var _index = _vm.attr("data-index");
  var _qty = $(".product-qty-" + _index).val();
  var _productId = $(".product-id-" + _index).val();
  var _productImage = $(".product-image-" + _index).val();
  var _productName = $(".product-name-" + _index).val();
  var _productPrice = $(".product-price-" + _index).text();
  var url = "/<slug>/<table_id>/add-to-cart"; // Replace <slug> and <table_id> with actual values
  url = url.replace("<slug>", "store.slug").replace("<table_id>", "table"); // Replace placeholders with template variables
  // Ajax
  $.ajax({
    url: "/add-to-cart",
    data: {
      id: _productId,
      image: _productImage,
      qty: _qty,
      name: _productName,
      price: _productPrice,
    },
    dataType: "json",
    beforeSend: function () {
      _vm.attr("disabled", true);
    },
    success: function (res) {
      $(".cart-count").text(res.totalitems);
      _vm.attr("disabled", false);
    },
  });
  // End
});
// End



