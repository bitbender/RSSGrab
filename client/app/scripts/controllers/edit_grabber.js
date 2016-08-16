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

    var replace_grabber = function(arr,grabber){
      for(var i = 0; i < arr.length; i++) {
        if(grabber._id['$oid'] === arr[i]._id['$oid']){
          arr[i] = grabber;
          break;
        }
      }
    };

    $scope.changed = function () {
      var hours = $scope.interval.getHours() * 3600;
      var minutes = $scope.interval.getMinutes() * 60;
      var seconds = $scope.interval.getSeconds();

      trigger = hours+minutes+seconds;
      $log.info(trigger)
    };

    // Open Preview Feed Dialog
    $scope.clickToOpen = function () {
      ngDialog.open({
        template: '../../views/partials/preview_feed.html',
        controller: 'PreviewFeedCtrl',
        scope: $scope
      }).closePromise.then(function (data) {
        console.log(data);
        //$scope.getAll();edit_grabber.js
      });
    };

    $scope.save = function (grabber) {
      if (trigger != 0){
        grabber.interval = trigger ;
      }

      var req = {
        method: 'PUT',
        url: 'http://localhost:5000/grabber',
        headers: {
          'Content-Type': "application/json"
        },
        data: grabber
      };

      $http(req).then(function successCallback(response) {
        $log.debug(response.data);
        replace_grabber($scope.grabbers, response.data);
        $scope.closeThisDialog('Close the edit dialog');
      }, function errorCallback(response) {
        $log.error('Ups for some reason I could not create the grabber')
      });
    };

  });
