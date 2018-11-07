const app = new Vue({
    el: '#app',
    data: {
        listGoods: [],
        period_parsing: null,
        low_percents_to_notification: null,
        high_percents_to_notification: null,
        days_to_notification: null,
        note_appear_good: null,
        search_string: '',
        minusDays: 1,
        goods: null,
        chart: null,
        chart_sales: null,
        black_list: [],
        show_now: 1
    },
    methods: {
        drawChat(item_name){
            const ctx = document.getElementById("Chart");
            const ctx_sales = document.getElementById("chart_sales");
            axios
                .post('http://localhost:3000/good_statistics',
                    {
                        item_name: item_name,
                        minusDays: this.minusDays
                    })
                .then(res => {
                    this.goods = res.data;
                    // цены
                    if(this.chart === null){
                        this.chart = new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: this.goods.labels,
                                datasets: this.goods.datasets
                            },
                            options: {
                                title: {
                                    display: true,
                                    text: "Динамика цен"
                                }
                            }
                        });
                    } else {
                        this.chart.data.labels = this.goods.labels;
                        this.chart.data.datasets = this.goods.datasets;
                        this.chart.update();
                    }
                    // продажи
                    if(this.chart_sales === null) {
                        this.chart_sales = new Chart(ctx_sales, {
                            type: 'line',
                            data: {
                                labels: this.goods.labels,
                                datasets: this.goods.in_sale_sold
                            },
                            options: {
                                title: {
                                    display: true,
                                    text: "Кол-во в продаже/продано"
                                }
                            }
                        });
                    } else {
                        this.chart_sales.data.labels = this.goods.labels;
                        this.chart_sales.data.datasets = this.goods.in_sale_sold;
                        this.chart_sales.update();
                    }
                });
        },
        save_settings() {
            let dat = {
                note_appear_good: this.note_appear_good,
                period_parsing: this.period_parsing,
                high_percents_to_notification: this.high_percents_to_notification,
                low_percents_to_notification: this.low_percents_to_notification,
                days_to_notification: this.days_to_notification
            };

            axios
                .post('http://localhost:3000/save_settings', dat)
                .then(res => {
                    console.log(res);
                });

        },
        set_minus_days(num_days){
            this.minusDays = num_days;
        },
        add_to_black_list(item_name){
            if(this.black_list.includes(item_name)){
                axios
                    .post('http://localhost:3000/black_list',
                        {
                            item_name: item_name,
                            status: 0
                        })
                    .then(res => {
                        this.black_list.splice(this.black_list.indexOf(item_name),1);
                    });
            } else {
                axios
                    .post('http://localhost:3000/black_list',
                        {
                            item_name: item_name,
                            status: 1
                        })
                    .then(res => {
                        this.black_list.push(item_name);
                    });
            }



        }
    },
    mounted(){
        // названия предметов
        axios({
            method: 'GET',
            url: 'http://localhost:3000/init',
            crossDomain: true
        })
            .then(res => {
                this.listGoods = res.data;
            });

        // настройки
        axios({
            method: 'GET',
            url: 'http://localhost:3000/settings',
            crossDomain: true
        })
            .then(res => {
                this.settings_parser = res.data;
                this.period_parsing = res.data.period_parsing;
                this.low_percents_to_notification = res.data.low_percents_to_notification;
                this.high_percents_to_notification = res.data.high_percents_to_notification;
                this.days_to_notification = res.data.days_to_notification;
                this.note_appear_good = res.data.note_appear_good;
                this.black_list = res.data.black_list;
            });


    }

});



