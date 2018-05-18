let map, heatmap, heatlayer, points = [];
let predict_btn;
let predict_url;
let info_div;
let predict_result;
let house_frame;
let jubilee = { lat: 52.95434, lng: -1.18888 }

function initMap() {
  axios.get('assets/result/result.json')
    .then(function (response) {
      let houses = response.data;
      map = new google.maps.Map(document.getElementById('map'), {
        zoom: 15,
        center: jubilee
      });

      for (let i = 0; i < houses.length; i++) {
        points.push(
          {
            location:
              new google.maps.LatLng(houses[i]['latitude'], houses[i]['longitude']),
            weight: (houses[i]['price'] - 218066) / 10000
          }
        )
        let link =
          "https://www.zoopla.co.uk/for-sale/details/" + houses[i].house_id

        let contentString =
          " <h3> Zoopla Sale Price: " + houses[i].price + "</h3>" +
          " <br/>" +
          " <h3> Meta Predicted Price: " + houses[i].meta_result + "</h3>" +
          " <br/>" +
          " <h3> Desc Predicted Price: " + houses[i].desc_result + "</h3>" +
          " <br/>" +
          " <h3> Comb Predicted Price: " + houses[i].comb_result + "</h3>" +
          " <br/>" +
          " <a href='" + link + "'> House Original Data </a>"

        let position = {
          lat: houses[i].latitude,
          lng: houses[i].longitude
        }

        let infowindow = new google.maps.InfoWindow({
          position: position,
          content: contentString
        });


        let marker = new google.maps.Marker({
          position: position,
          map: map,
        });

        marker.addListener('click', function () {
          infowindow.open(map, marker);
        });
      }
      // initHeatMap();
    }).catch(function (error) {
      console.log(error);
    }
    );
}


function initHeatMap() {
  heatmap = new google.maps.Map(document.getElementById('heatmap'), {
    zoom: 12,
    center: jubilee,
  });

  heatlayer = new google.maps.visualization.HeatmapLayer({
    data: points,
    map: heatmap,
    gradient: [
      'rgba(0, 255, 255, 0)',
      'rgba(0, 255, 255, 1)',
      'rgba(0, 160, 255, 1)',
      'rgba(0, 63, 255, 1)',
      'rgba(0, 0, 223, 1)',
      'rgba(0, 0, 159, 1)',
      'rgba(0, 0, 127, 1)',
      'rgba(63, 0, 91, 1)',
      'rgba(127, 0, 63, 1)',
      'rgba(191, 0, 31, 1)',
      'rgba(255, 0, 0, 1)'
    ],
    radius: 20
  });
}


function get_prediction(house_id) {
  predict_result.innerHTML = "Background model is predicting price now. <br/> Please wait ...";
  info_div.style.visibility = 'visible';
  var result;
  axios.get('get_prediction?id=' + house_id)
    .then(function (response) {
      result = response.data;
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
    }).catch(function (error) {
      predict_result.innerHTML = "Sorry, Unable to finish prediction. Please check your house id...";
    });
  document.getElementById("info_div").style.display = 'block';
  predict_result.innerHTML = "Please wait ...";
}




onload = function () {
  predict_btn = this.document.getElementById("predict_btn");
  predict_url = this.document.getElementById("predict_url");
  info_div = this.document.getElementById("info_div");
  predict_result = this.document.getElementById("predict_result");
  house_frame = this.document.getElementById("house_frame");
  predict_btn.onclick = function () {
    var result = get_prediction(predict_url.value);
  };
};