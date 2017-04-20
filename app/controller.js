var speakercastApp = angular.module('speakercastApp', []);

var first_presidency_names = ["Thomas S. Monson", "Henry B. Eyring", "Dieter F. Uchtdorf"];
var twelve_apostles_names = ["Russell M. Nelson", "Dallin H. Oaks", "M. Russell Ballard", "Robert D. Hales", "Jeffrey R. Holland", "David A. Bednar", "Quentin L. Cook", "D. Todd Christofferson", "Neil L. Andersen", "Ronald A. Rasband", "Gary E. Stevenson", "Dale G. Renlund"];

// var server_url = "http://127.0.0.1:5000";
var server_url = "http://speakercast.app.lundrigan.org";

speakercastApp.controller('SpeakerController', function($scope, $http) {
    $scope.speakers = speakers;
    $scope.first_presidency = [];
    $scope.twelve_apostles = [];

    angular.forEach($scope.speakers, function(speaker) {
      var first_presidency_index = first_presidency_names.indexOf(speaker.name);
      var twelve_apostles_index = twelve_apostles_names.indexOf(speaker.name);

      if (first_presidency_index >= 0) {
        speaker.index = first_presidency_index;
        $scope.first_presidency.push(speaker);
      }
      else if (twelve_apostles_index>= 0) {
        speaker.index = twelve_apostles_index;
        $scope.twelve_apostles.push(speaker);
      }
    });

    // $http.get(server_url + '/speakers').then(function(response) {
    //   $scope.speakers = response.data;
    //   $scope.first_presidency = [];
    //   $scope.twelve_apostles = [];

    //   angular.forEach($scope.speakers, function(speaker) {
    //     var first_presidency_index = first_presidency_names.indexOf(speaker.name);
    //     var twelve_apostles_index = twelve_apostles_names.indexOf(speaker.name);

    //     if (first_presidency_index >= 0) {
    //       speaker.index = first_presidency_index;
    //       $scope.first_presidency.push(speaker);
    //     }
    //     else if (twelve_apostles_index>= 0) {
    //       speaker.index = twelve_apostles_index;
    //       $scope.twelve_apostles.push(speaker);
    //     }
    //   });
    // });

    $scope.anySelected = false;

    $scope.smallScreen = false;

    $scope.$on('windowResize', function(event, currentBreakpoint, previousBreakpoint) {
      $scope.smallScreen = currentBreakpoint == "extra small";
      $scope.$apply();
    });
});

speakercastApp.directive('bsBreakpoint', function($window, $rootScope, $timeout) {
    return {
        controller: function() {
            var getBreakpoint = function() {
                var windowWidth = $window.innerWidth;

                if(windowWidth < 768) {
                    return 'extra small';
                } else if (windowWidth >= 768 && windowWidth < 992) {
                    return 'small';
                } else if (windowWidth >= 992 && windowWidth < 1200) {
                    return 'medium';
                } else if (windowWidth >= 1200) {
                    return 'large';
                }
            };

            var currentBreakpoint = getBreakpoint();
            var previousBreakpoint = null;

            // Broadcast inital value, so other directives can get themselves setup
            $timeout(function() {
                $rootScope.$broadcast('windowResize', currentBreakpoint, previousBreakpoint);
            });

            angular.element($window).bind('resize', function() {
                var newBreakpoint = getBreakpoint();

                if (newBreakpoint != currentBreakpoint) {
                    previousBreakpoint = currentBreakpoint;
                    currentBreakpoint = newBreakpoint;
                }

                $rootScope.$broadcast('windowResize', currentBreakpoint, previousBreakpoint);
            });
        }
    };
});

speakercastApp.directive('myRepeatDirective', function() {
  return function(scope, element, attrs) {
    if (scope.$last) {
      // console.log("before: " + $(document).height());
      // setTimeout(set_affix, 0);
    }
  };
});
