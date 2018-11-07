const express = require('express');
const app = express();
const cors = require('cors');
const mongoose = require('mongoose');
const bodyParser = require('body-parser')
app.use(cors());
app.use(bodyParser.json())

// mongoose
mongoose.connect('mongodb://localhost/lootdog');
const connection = mongoose.connection;

connection.on('error', console.error.bind(console, 'connection error:'));
connection.once('open', function () {

    connection.db.collection('settings_parser', function(err, collection){
        app.get('/settings', function (req, res) {
            collection.findOne({}, function(err, data){
                res.send(data);
            })
        });


        app.post('/save_settings', function (req, res) {
            collection.findOne({key: 'secret'}, function (err, data) {
                if (err) return console.log(err);
                data.period_parsing = req.body.period_parsing;
                data.low_percents_to_notification = req.body.low_percents_to_notification;
                data.high_percents_to_notification = req.body.high_percents_to_notification;
                data.days_to_notification = req.body.days_to_notification;
                data.note_appear_good = req.body.note_appear_good;

                collection.save(data, function (err, data) {
                    res.send(data);
                });
            });
        });

        app.post('/black_list', function (req, res) {
            collection.findOne({key: 'secret'}, function (err, data) {
                if (err) return console.log(err);

                if(req.body.status){
                    data.black_list.push(req.body.item_name);
                } else {
                    data.black_list.splice(data.black_list.indexOf(req.body.item_name), 1);
                }

                collection.save(data, function (err, data) {
                    res.send(data);
                });

            });
        });







    });


    connection.db.collection("price_statistics", function(err, collection){

        //  тута писать запросы



        app.get('/', function (req, res) {
            collection.find({}).toArray(function(err, data){
                res.send(data);
            })
        });


        app.get('/init', function (req, res) {
            collection.distinct('item_name',function(err, data){
                res.send(data);
            })
        });

        app.post('/good_statistics', function (req, res) {
            let startDate = new Date();
            startDate.setDate(startDate.getDate() - req.body.minusDays);
            collection.find({
                item_name: req.body.item_name,
                date: {"$gte": startDate, "$lt": new Date()}
            })
                .toArray(function(err, data){

                    let tempLabels = []
                    let labels = [];
                    let datasets = [
                        {
                            data: [],
                            label: "Цена 1",
                            borderColor: "#3e95cd",
                            fill: false
                        },
                        {
                            data: [],
                            label: "Цена 2",
                            borderColor: "#8e5ea2",
                            fill: false
                        },
                        {
                            data: [],
                            label: "Цена 3",
                            borderColor: "#3cba9f",
                            fill: false
                        },
                        {
                            data: [],
                            label: "Цена 4",
                            borderColor: "#e8c3b9",
                            fill: false
                        },
                        {
                            data: [],
                            label: "Цена 5",
                            borderColor: "#c45850",
                            fill: false
                        }
                    ];
                    let in_sale_sold = [
                        {
                            data: [],
                            label: "В продаже",
                            borderColor: "#1971ff",
                            fill: false
                        },
                        {
                            data: [],
                            label: "Продано за день",
                            borderColor: "#ef2c09",
                            fill: false
                        }
                    ];

                    data.forEach(function (good) {
                       // labels
                        if(req.body.minusDays === 1){
                            tempLabels.push(good.date.getHours().toString()+':'+good.date.getMinutes().toString());
                        } else {
                            tempLabels.push(good.date.getDate().toString()+'.'+good.date.getMonth().toString()+' '+good.date.getHours().toString()+':'+good.date.getMinutes().toString());
                        }

                        // в продаже/продано
                        in_sale_sold[0].data.push(good.count_on_sale_now);
                        in_sale_sold[1].data.push(good.sold_today);

                       //  datasets
                        datasets[0].data.push(good.prices[0]);
                        datasets[1].data.push(good.prices[1]);
                        datasets[2].data.push(good.prices[2]);
                        datasets[3].data.push(good.prices[3]);
                        datasets[4].data.push(good.prices[4]);
                    });



                    for(let i = 0; i < tempLabels.length; i += req.body.minusDays){
                        labels.push(tempLabels[i])
                    }
                    res.send({
                        labels,
                        datasets,
                        in_sale_sold
                    });
            })
        });


    });
});






app.listen(3000, function () {
    console.log('app listening on port 3000!');
});