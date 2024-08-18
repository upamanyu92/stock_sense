document.getElementById('stock-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const symbol = document.getElementById('symbol').value;
    fetch('/get_stock_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ 'symbol': symbol })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('result').innerText = JSON.stringify(data, null, 2);
    });
});

document.getElementById('predict-button').addEventListener('click', function (e) {
    e.preventDefault();

    const symbol = document.getElementById('symbol').value;
    fetch('/get_prediction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ 'symbol': symbol })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('result').innerText = JSON.stringify(data, null, 2);
    });
});
