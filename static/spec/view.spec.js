describe('View Page JS', function() {
    describe('titleHelper', function() {
        describe('render', function() {
            it('should set a title with the correct format', function() {
                titleHelper.render('area_code', '310');
                expect($('#title-results h2').text()).toBe('Texts from (310)');
            });
        });
    });

    describe('textList', function() {
        describe('render', function() {
            it('should set a list of texts with the correct format', function() {
                textList.render({"data": [{"body": "Hi", "city": "La Grange Park", "country": "US", "area_code": "630", "state": "IL", "time_since": "0h:47m:8s", "zip_code": "60561"}]});
                expect($('#text-results h4').text()).toBe('(630) Hi');
            });
        });
    });

    describe('filterHelper', function() {
        describe('render', function() {
            it('should set the correct options for the filter selects', function() {
                filterHelper.render({"states": ["CA", "WI", "WA", "NV", "IL"], "countries": ["US"], "cities": ["Los Altos", "Los Angeles", "Sherman Oaks", "Chicago", "San Diego", "Burbank", "Gardena", "Las Vegas", "Vancouver", "Sunnyvale", "Milwaukee", "La Grange Park", "Van Nuys", "Seattle"], "area_codes": ["630", "818", "626", "206", "310", "858", "702", "414", "650", "847", "360", "408"], "zip_codes": ["53202", "90507", "90015", "60561", "90249", "98101", "94024", "94087", "91504", "91505", "91401", "89101", "92128", "90049", "91335", "98675", "60042"]});
                expect($('#filter-results option')[1].innerHTML).toBe('630');
            });
        });
    });
});