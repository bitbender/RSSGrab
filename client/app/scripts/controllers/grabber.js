'use strict';

/**
 * @ngdoc function
 * @name yapp.controller:GrabberCtrl
 * @description
 * # GrabberCtrl
 */
angular.module('yapp')
  .controller('GrabberCtrl', function ($scope, $state, ngDialog, $http) {

    $scope.clickToOpen = function () {
      ngDialog.open({
        template: '../../views/partials/create_grabber.html',
        controller: 'GrabberCtrl'
      });
    };

    $scope.greet = function () {
      console.log($scope.grabber);
    };

    $scope.create = function () {
      var req = {
        method: 'POST',
        url: 'http://localhost:5000/grabber',
        headers: {
          'Content-Type': "application/json"
        },
        data: $scope.grabber
      };

      $http(req).then(function successCallback(response) {
        console.log(response)
      }, function errorCallback(response) {
        console.log('Ups for some reason I couldn\'t create the grabber')
      });

    }
  });
