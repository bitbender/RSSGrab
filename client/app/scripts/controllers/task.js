'use strict';

/**
 * @ngdoc function
 * @name yapp.controller:AdminCtrl
 * @description
 * # AdminCtrl
 * Controller of admin
 */
angular.module('yapp')
  .controller('TaskCtrl', function ($scope, $state, $http) {

    $scope.$state = $state;

    $scope.createTask = function(){

      var req = {
        method: 'POST',
        url: 'http://localhost:5000/task',
        headers: {
          'Content-Type': 'application/json'
        },
        data: angular.toJson($scope.user)
      };

      $http(req).then(function successCallback(response) {
        console.log("Successfully created a new Task!")
      }, function errorCallback(response) {
        // called asynchronously if an error occurs
        // or server returns response with an error status.
        console.log('Ups an error occurred while creating a new task!')
      });
    };

    $scope.foo = function(){
      $http({
        method: 'GET',
        url: 'http://localhost:5000/database'
      }).then(function successCallback(response) {
        $scope.databases = angular.fromJson(response.data.databases);
        console.log(response)
      }, function errorCallback(response) {
        // called asynchronously if an error occurs
        // or server returns response with an error status.
        console.log('Ups an error occurred while calling the backend!')
      });
    }

  });
