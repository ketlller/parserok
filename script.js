const app = new Vue({
    el: '#app',
    data: {
        listGoods: null,
        period_parsing: null,
        percents_to_notification: null,
        days_to_notification: null,
        minusDays: 1,
        goods: null,
        chart: null
    },
    methods: {
        drawChat(item_name){
            const ctx = document.getElementById("Chart");
            axios
                .post('http://localhost:3000/good_statistics',
                    {
                        item_name: item_name,
                        minusDays: this.minusDays
                    })
                .then(res => {
                    this.goods = res.data;
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
                                    text: "Статистика цен за последние "+this.minusDays.toString()+" дней"
                                }
                            }
                        });
                    } else {
                        this.chart.data.labels = this.goods.labels;
                        this.chart.data.datasets = this.goods.datasets;
                        this.chart.update();
                    }

                });
        },
        save_settings(){
            let dat = {
                period_parsing: this.period_parsing,
                percents_to_notification: this.percents_to_notification,
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
                console.log(res.data);
                this.settings_parser = res.data;
                this.period_parsing = res.data.period_parsing;
                this.percents_to_notification = res.data.percents_to_notification;
                this.days_to_notification = res.data.days_to_notification;
            });


    }

});



