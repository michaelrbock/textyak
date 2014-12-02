var textList = {
    templateFunction: Handlebars.compile($('#text-template').html()),

    render: function(response) {
        var html = '';
        for (var i = 0; i < 3; i++) {
            html += this.templateFunction(response.data[i]);
        }
        $('#text-results-1').html(html);

        html = '';
        for (var i = 3; i < 6; i++) {
            html += this.templateFunction(response.data[i]);
        }
        $('#text-results-2').html(html);
    }
};

$(document).ready(function() {
    $.getJSON('/api/texts', function(response) {
        textList.render(response);
    });
});
