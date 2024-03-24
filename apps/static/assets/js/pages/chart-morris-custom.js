'use strict';
$(document).ready(function() {
    setTimeout(function() {
    // [ bar-simple ] chart start

    // [ line-angle-chart ] end
    // [ line-smooth-chart ] start
    Morris.Line({
        element: 'morris-line-smooth-chart',
        data: [{
                y: '2006',
                a: 100,
                b: 90
            },
            {
                y: '2007',
                a: 75,
                b: 65
            },
            {
                y: '2008',
                a: 50,
                b: 40
            },
            {
                y: '2009',
                a: 75,
                b: 65
            },
            {
                y: '2010',
                a: 50,
                b: 40
            },
            {
                y: '2011',
                a: 75,
                b: 65
            },
            {
                y: '2012',
                a: 100,
                b: 90
            }
        ],
        xkey: 'y',
        redraw: true,
        resize: true,
        ykeys: ['a', 'b'],
        hideHover: 'auto',
        responsive:true,
        labels: ['Series A', 'Series B'],
        lineColors: ['#1de9b6', '#A389D4']
    });
    // [ line-smooth-chart ] end

    // [ Donut-chart ] Start
    var graph = Morris.Donut({
        element: 'morris-donut-chart',
        data: [{
                value: 60,
                label: 'Data 1'
            },
            {
                value: 20,
                label: 'Data 1'
            },
            {
                value: 10,
                label: 'Data 1'
            },
            {
                value: 5,
                label: 'Data 1'
            }
        ],
        colors: [
            '#1de9b6',
            '#A389D4',
            '#04a9f5',
            '#1dc4e9',
        ],
        resize: true,
        formatter: function(x) {
            return "val : " + x
        }
    });    
    // [ Donut-chart ] end
        }, 700);
});
