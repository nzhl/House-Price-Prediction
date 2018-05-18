chrome.tabs.query(
    { currentWindow: true, active: true },
    function (tabs) {
        let url = tabs[0].url;
        let house_id = url.match('details/([0-9]*)');
        if (house_id.length == 2) {
            house_id = house_id[1];
            prediction_request(house_id);
        }
    }
);

function prediction_request(house_id) {
    if (house_id) {
        $.ajax({
            url: "http://localhost:3000/get_prediction?id=" + house_id,
            type: "GET", dataType: "json",
        }).done(function (result) {
            var content = "Zoopla On Sale Price: £" + result['price'] +
                "  <br/>My Estimation: £" + result['prediction'];
            predict_result.innerHTML = content;

            var myChart = echarts.init(document.getElementById('radar_div'));
            option = {
                title: {
                    text: 'House Data Analysis'
                },
                tooltip: {},
                legend: {
                    data: ['Average Level', 'Current House']
                },
                radar: {
                    // shape: 'circle',
                    name: {
                        textStyle: {
                            color: '#fff',
                            backgroundColor: '#999',
                            borderRadius: 3,
                            padding: [3, 5]
                        }
                    },
                    indicator: [
                        { name: 'Area Average Sell', max: result['price_max'], min: result['price_min'] },
                        { name: 'Area Average Ask ', max: result['price_max'], min: result['price_min'] },
                        { name: 'Robbery (Crime)', max: 5 },
                        { name: 'Burglary (Crime)', max: 10 },
                        { name: 'Overall User Rating (Area)', max: 100, min: 60 },
                        { name: 'Transport and Travel (Area)', max: 100, min: 60 },
                        { name: 'Level 4+ English and Math (Education)', max: 100, min: 70 },
                        { name: '2+ A-Level passes (Education)', max: 100, min: 70 },
                    ]
                },
                series: [{
                    name: 'House Data Analysis',
                    type: 'radar',
                    data: [
                        {
                            value: [result['avg_sell'], result['avg_ask'], 0.97, 7.01, 78.98, 84.74, 78.02, 92.56],
                            name: 'Average Level'
                        },
                        {
                            value: [result['price'], result['price'], result['crime'][5], result['crime'][1],
                            result['overall_rating'], result['tt_rating'],
                            result['education'][0], result['education'][4]],
                            name: 'Current House'
                        }
                    ]
                }]
            };
            myChart.setOption(option);


        }).fail(function (xhr, status, errorThrown) {
            $("h3").html(
                "Sorry, Unable to finish prediction. Please check your url..."
            )
        })
        document.getElementById("info_div").style.display = 'block';
        predict_result.innerHTML = "Please wait ...";
    }
}