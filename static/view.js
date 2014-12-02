var textList = {
    templateFunction: Handlebars.compile($('#text-template').html()),

    setLoading: function() {
        $('#text-results').html('Loading...');
    },

    render: function(response) {
        var html = '';

        for (var i = 0; i < response.data.length; i++) {
          html += this.templateFunction(response.data[i]);
        }

        $('#text-results').html(html);
    }
};

var titleHelper = {
    templateFunction: Handlebars.compile($('#title-template').html()),

    render: function(type, value) {
        if (type == 'area_code') {
            value = '(' + value + ')';
        }
        $('#title-results').html(this.templateFunction({type: type, value: value}));
    }
};

var textApi = {
    call: function(filterBy, value) {
        textList.setLoading();

        if (!filterBy || !value) {
            url = '/api/texts';
        } else {
            url = 'api/texts?' + filterBy + '=' + value;
        }

        $.getJSON(url, function(response) {
            titleHelper.render(filterBy, value);
            textList.render(response);
        });
    }
};

var filterHelper = {
    templateFunction: Handlebars.compile($('#filter-template').html()),

    render: function(response) {
        var html = '';

        html += this.templateFunction({type: 'Area-Code', values: response.area_codes});
        html += this.templateFunction({type: 'City', values: response.cities});
        html += this.templateFunction({type: 'State', values: response.states});
        html += this.templateFunction({type: 'Zip-Code', values: response.zip_codes});

        $('#filter-results').html(html);
    }
};

var categoriesApi = {
    call: function() {
        return $.getJSON('/api/categories', function(response) {
            filterHelper.render(response);
        });
    }
};

// initial page setup
$(document).ready(function() {
    categoriesPromise = categoriesApi.call();

    var filter = window.location.hash.substr(1).split('=');

    if (filter[0] == 'area_code') {
        textApi.call('area_code', filter[1]);
    } else if (filter[0] == 'city') {
        textApi.call('city', filter[1]);
    } else if (filter[0] == 'state') {
        textApi.call('state', filter[1]);
    } else if (filter[0] == 'zip_code') {
        textApi.call('zip_code', filter[1]);
    } else {
        textApi.call(null, null);
    }

    // Form binding must be done after options are populated
    categoriesPromise.done(function() {
        $('.filter').on('submit', function(e) {
            e.preventDefault();
            e.returnValue = false;

            currentId = this.id;

            // clear all other filters
            $('.filter').each(function(index) {
                if (this.id != currentId) {
                    $('#' + this.id + ' select').val('0');
                }
            });

            filterBy = this.id.replace('-', '_').toLowerCase();
            value = $('#' + this.id + ' select').val();

            if (filterBy && value) {
                textApi.call(filterBy, value);

                // change url hash
                window.location.hash = filterBy + '=' + value;
            }
        });
    });

});