'use strict';

/**
 * @ngdoc function
 * @name yapp.controller:GrabberCtrl
 * @description
 * # GrabberCtrl
 */
angular.module('yapp')
  .controller('PreviewFeedCtrl', function ($scope, $state, $log, $http, __env) {

    $scope.preview = function () {

      $log.info('Grabbing: '+$scope.grabber.feed);

      var req = {
        method: 'POST',
        url: __env.apiUrl+'feed',
        headers: {
          'Content-Type': "application/json"
        },
        data: {
          'url': $scope.grabber.feed
        }
      };

      $http(req).then(function successCallback(response) {
        $scope.feed = response.data;
      }, function errorCallback(response) {
        $log.info('Ups for some reason I could not preview the contents of this feed')
      });
    };

    $scope.preview();

  });
