
/**
* Theme: Ubold Admin Template
* Author: Coderthemes
* eCommerce Dashboard
*/

!function($) {
    "use strict";

    var eCommerceDashboard = function() {
    	this.$realData = []
    };

    //creates area chart with dotted
    eCommerceDashboard.prototype.createAreaChartDotted = function(element, pointSize, lineWidth, data, xkey, ykeys, labels, Pfillcolor, Pstockcolor, lineColors) {
        Morris.Area({
            element: element,
            pointSize: 0,
            lineWidth: 0,
            data: data,
            xkey: xkey,
            ykeys: ykeys,
            labels: labels,
            hideHover: 'auto',
            pointFillColors: Pfillcolor,
            pointStrokeColors: Pstockcolor,
            resize: true,
            gridLineColor: '#eef0f2',
            lineColors: lineColors
        });

   },
    eCommerceDashboard.prototype.init = function() {

        //creating area chart
        var $areaDotData = [
                { y: '2009', a: 10, b: 20, c:30 },
                { y: '2010', a: 75,  b: 65, c:30 },
                { y: '2011', a: 50,  b: 40, c:30 },
                { y: '2012', a: 75,  b: 65, c:30 },
                { y: '2013', a: 50,  b: 40, c:30 },
                { y: '2014', a: 75,  b: 65, c:30 },
                { y: '2015', a: 90, b: 60, c:30 }
            ];
        this.createAreaChartDotted('morris-area-with-dotted', 0, 0, $areaDotData, 'y', ['a', 'b', 'c'], ['Desktops ', 'Tablets ', 'Mobiles '],['#ffffff'],['#999999'], ['#7e57c2', '#b39ddb', '#ede7f6']);

    },
    //init
    $.eCommerceDashboard = new eCommerceDashboard, $.eCommerceDashboard.Constructor = eCommerceDashboard
}(window.jQuery),

//initializing
function($) {
    "use strict";
    $.eCommerceDashboard.init();
}(window.jQuery);