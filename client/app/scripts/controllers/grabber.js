'use strict';

/**
 * @ngdoc function
 * @name yapp.controller:GrabberCtrl
 * @description
 * # GrabberCtrl
 */
angular.module('yapp')
  .controller('GrabberCtrl', function ($scope, $state, ngDialog, $http) {

    /**
    * Convert the interval value to the correct unit (seconds,minutes,hours)
    * @param value the inverval value in seconds
    * @param unit the unit it should be converted to (sec, min, h)
    * @returns number converted interval value
    */
    var convert = function(value,unit){
      if(unit == 'min'){
        return value * 60;
      }else if(unit == 'h'){
        return value * 60 * 60;
      }else{
        return value;
      }
    };

    $scope.getAll = function () {

      var req = {
        method: 'GET',
        url: 'http://localhost:5000/grabber',
        headers: {
          'Content-Type': "application/json"
        }
      };

      $http(req).then(function successCallback(response) {
        $scope.grabbers = response.data;
      }, function errorCallback(response) {
        console.log('Ups for some reason I couldn\'t create the grabber')
      });

    };
    // get all data when page reloads
    $scope.getAll();

    $scope.clickToOpen = function () {
      ngDialog.open({
        template: '../../views/partials/create_grabber.html',
        controller: 'GrabberCtrl'
      });
    };

    $scope.create = function () {
      $scope.grabber.interval = convert($scope.grabber.interval, $scope.unit);

      var req = {
        method: 'POST',
        url: 'http://localhost:5000/grabber',
        headers: {
          'Content-Type': "application/json"
        },
        data: $scope.grabber
      };

      $http(req).then(function successCallback(response) {
        console.log(response.data)
      }, function errorCallback(response) {
        console.log('Ups for some reason I couldn\'t create the grabber')
      });
    };

    $scope.start = function(position){
      var req = {
        method: 'POST',
        url: 'http://localhost:5000/grabber/'+$scope.grabbers[position].id+'/start',
        headers: {
          'Content-Type': "application/json"
        }
      };

      $http(req).then(function successCallback(response) {
        console.log(response.data);
        $scope.startgrab='glyphicon glyphicon-play text-success';
      }, function errorCallback(response) {
        console.log('Ups for some reason I couldn\'t start the grabber')
      });
    };

    $scope.stop = function(position){
      var req = {
        method: 'POST',
        url: 'http://localhost:5000/grabber/'+$scope.grabbers[position].id+'/stop',
        headers: {
          'Content-Type': "application/json"
        }
      };

      $http(req).then(function successCallback(response) {
        console.log(response.data);
        $scope.stopgrab='glyphicon glyphicon-play text-danger';
      }, function errorCallback(response) {
        console.log('Ups for some reason I couldn\'t stop the grabber')
      });
    };

    $scope.delete = function(position){
      console.log("Deleting Grabber at position: "+position);
      console.log($scope.grabbers[position].id);

      var req = {
        method: 'DELETE',
        url: 'http://localhost:5000/grabber/'+$scope.grabbers[position].id,
        headers: {
          'Content-Type': "application/json"
        }
      };

      $http(req).then(function successCallback(response) {
        console.log(response);
        $scope.getAll();
      }, function errorCallback(response) {
        console.log('Ups for some reason I couldn\'t delete the grabber')
      });

    }
  });
