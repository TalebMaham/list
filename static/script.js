var cart = [];
var totalAmount = 0.0;

function addToCart(product, price) {
    price = parseFloat(price); // Assurez-vous que le prix est un nombre
    cart.push({product: product, price: price});
    totalAmount += price;
    updateCart();
}

function updateCart() {
    var cartItems = $('#cart-items');
    cartItems.empty();
    cart.forEach(function(item, index) {
        cartItems.append('<div class="list-group-item">' +
            '<span>' + item.product + ' ' + item.price.toFixed(2) + ' </span>' +
            '<button class="btn btn-danger btn-sm float-right" onclick="removeFromCart(' + index + ')">Retirer</button>' +
        '</div>');
    });
    $('#total-amount').text(totalAmount.toFixed(2));
}

function removeFromCart(index) {
    totalAmount -= cart[index].price;
    cart.splice(index, 1);
    updateCart();
}

function startTransaction() {
    $.ajax({
        url: '/start_transaction',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({total: totalAmount}),
        success: function(response) {
            console.log(response);
            monitorInsertedAmount();
        },
        error: function(error) {
            console.error(error);
        }
    });
}

function monitorInsertedAmount() {
    var insertedAmount = 0.0;
    var intervalId = setInterval(function() {
        $.ajax({
            url: '/get_inserted_amount',
            type: 'GET',
            success: function(response) {
                console.log(response);
                insertedAmount = response.montant_insere;
                $('#inserted-amount').text(insertedAmount.toFixed(2));
                
                if (response.finish) {
                    clearInterval(intervalId);
                    console.log("Monitoring stopped");
                }
            },
            error: function(error) {
                console.error(error);
            }
        });
    }, 1000);
}
