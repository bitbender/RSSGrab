'use strict';

/**
 * @ngdoc function
 * @name yapp.controller:GrabberCtrl
 * @description
 * # GrabberCtrl
 */
angular.module('yapp')
  .controller('GrabberCtrl', function ($scope, $state, $log, ngDialog, $http) {

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
        controller: 'CreateGrabberCtrl'
      }).closePromise.then(function (data) {
        console.log(data.id + ' has been dismissed.');
        $scope.getAll();
      });
    };

    $scope.openEditDialog = function (position) {
      $scope.grabber = $scope.grabbers[position];
      ngDialog.open({
        template: '../../views/partials/edit_grabber.html',
        controller: 'EditGrabberCtrl',
        scope: $scope
      }).closePromise.then(function (data) {
        console.log('Edit grabber dialog has been dismissed.');
      });
    };

    $scope.start = function(position){

      var req = {
        method: 'POST',
        url: 'http://localhost:5000/grabber/'+$scope.grabbers[position]._id['$oid']+'/start',
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

    $scope.startAll = function(){
      var req = {
        method: 'POST',
        url: 'http://localhost:5000/grabber/start',
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
        url: 'http://localhost:5000/grabber/'+$scope.grabbers[position]._id['$oid']+'/stop',
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

    $scope.stopAll = function(){
      var req = {
        method: 'POST',
        url: 'http://localhost:5000/grabber/stop',
        headers: {
          'Content-Type': "application/json"
        }
      };

      $http(req).then(function successCallback(response) {
        console.log(response.data);
        $scope.stopgrab='glyphicon glyphicon-play text-danger';
      }, function errorCallback(response) {
        console.log('Ups for some reason I couldn\'t start the grabber')
      });
    };

    $scope.delete = function(position){
      console.log("Deleting Grabber at position: "+position);
      console.log($scope.grabbers[position]);

      var req = {
        method: 'DELETE',
        url: 'http://localhost:5000/grabber',
        headers: {
          'Content-Type': "application/json"
        },
        data: $scope.grabbers[position]
      };

      $http(req).then(function successCallback(response) {
        console.log(response);
        $scope.getAll();
      }, function errorCallback(response) {
        console.log('Ups for some reason I couldn\'t delete the grabber')
      });

    }
  });
