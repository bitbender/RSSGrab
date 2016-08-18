'use strict';

/**
 * @ngdoc function
 * @name yapp.controller:GrabberCtrl
 * @description
 * # GrabberCtrl
 */
angular.module('yapp')
  .controller('CreateGrabberCtrl', function ($scope, $state, $log, ngDialog, $http, __env) {

    $scope.grabber = {};

    var d =  new Date();
    d.setHours(0);
    d.setMinutes(0);
    d.setSeconds(0);
    $scope.Date = d;

    var trigger = 0;

    $scope.changed = function () {
      var hours = $scope.grabber.interval.getHours() * 3600;
      var minutes = $scope.grabber.interval.getMinutes() * 60;
      var seconds = $scope.grabber.interval.getSeconds();

      trigger = hours+minutes+seconds;
    };

    $scope.create = function () {
      $scope.grabber.interval = trigger ;

      $log.info($scope.grabber);

      var req = {
        method: 'POST',
        url: __env.apiUrl+'grabber',
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

    $scope.openPreviewDialog = function () {
      $log.info('Open preview dialog');
      ngDialog.open({
        template: '../../views/partials/preview_feed.html',
        controller: 'PreviewFeedCtrl',
        scope: $scope
      }).closePromise.then(function (data) {
        console.log(data);
      });
    };

  });
