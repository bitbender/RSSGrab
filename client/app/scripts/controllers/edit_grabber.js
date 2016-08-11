'use strict';

/**
 * @ngdoc function
 * @name yapp.controller:GrabberCtrl
 * @description
 * # GrabberCtrl
 */
angular.module('yapp')
  .controller('EditGrabberCtrl', function ($scope, $state, $log, $http, ngDialog, moment) {

    var dur =  $scope.grabber.interval;
    var h = Math.floor(dur/3600);
    var m = Math.floor((dur-(h*3600))/60);
    var s = dur-(h*3600+m*60);
    $log.log(h);
    $log.log(m);
    $log.log(s);
    $scope.Date = new moment().hours(h).minutes(m).seconds(s);

    var trigger = 0;

    $scope.changed = function () {
      var hours = $scope.interval.getHours() * 3600;
      var minutes = $scope.interval.getMinutes() * 60;
      var seconds = $scope.interval.getSeconds();

      trigger = hours+minutes+seconds;
      $log.info(trigger)
    };

    $scope.clickToOpen = function () {
      ngDialog.open({
        template: '../../views/partials/preview_feed.html',
        controller: 'PreviewFeedCtrl',
        scope: $scope
      }).closePromise.then(function (data) {
        console.log(data);
        //$scope.getAll();
      });
    };

    $scope.save = function () {
      if (trigger != 0){
        $scope.grabber.interval = trigger ;
      }
      $log.info($scope.grabber);

      var req = {
        method: 'PUT',
        url: 'http://localhost:5000/grabber',
        headers: {
          'Content-Type': "application/json"
        },
        data: $scope.grabber
      };

      $http(req).then(function successCallback(response) {
        $log.info(response);
        $scope.closeThisDialog('Close the create dialog');
      }, function errorCallback(response) {
        $log.info('Ups for some reason I could not create the grabber')
      });
    };

  });
