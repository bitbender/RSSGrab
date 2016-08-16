'use strict';

/**
 * @ngdoc function
 * @name yapp.controller:GrabberCtrl
 * @description
 * # GrabberCtrl
 */
angular.module('yapp')
  .controller('GrabberCtrl', function ($scope, $state, $log, ngDialog, $http) {

    // This controls the sorting of the table
    $scope.sortType     = 'name'; // set the default sort type
    $scope.sortReverse  = false;  // set the default sort order
    $scope.searchTerm   = '';     // set the default search/filter term

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

    var replace_grabber = function(arr,grabber){
      for(var i = 0; i < arr.length; i++) {
        if(grabber._id['$oid'] === arr[i]._id['$oid']){
          arr[i] = grabber;
          break;
        }
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

    // Open the create dialog
    $scope.clickToOpen = function () {
      ngDialog.open({
        template: '../../views/partials/create_grabber.html',
        controller: 'CreateGrabberCtrl'
      }).closePromise.then(function (data) {
        console.log(data.id + ' has been dismissed.');
        $scope.getAll();
      });
    };

    $scope.openEditDialog = function (grabber) {
      $scope.grabber = grabber;
      ngDialog.open({
        template: '../../views/partials/edit_grabber.html',
        controller: 'EditGrabberCtrl',
        scope: $scope
      }).closePromise.then(function (data) {
        console.log('Edit grabber dialog has been dismissed.');
      });
    };

    $scope.start = function(grabber){

      var req = {
        method: 'POST',
        url: 'http://localhost:5000/grabber/'+grabber._id['$oid']+'/start',
        headers: {
          'Content-Type': "application/json"
        }
      };

      $http(req).then(function successCallback(response) {
        console.log(response.data);
        replace_grabber($scope.grabbers, response.data);
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
        $scope.grabbers = response.data;
      }, function errorCallback(response) {
        console.log('Ups for some reason I couldn\'t start the grabber')
      });
    };

    $scope.stop = function(grabber){
      var req = {
        method: 'POST',
        url: 'http://localhost:5000/grabber/'+grabber._id['$oid']+'/stop',
        headers: {
          'Content-Type': "application/json"
        }
      };

      $http(req).then(function successCallback(response) {
        console.log(response.data);
        replace_grabber($scope.grabbers, response.data);
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
        $scope.grabbers = response.data;
      }, function errorCallback(response) {
        console.log('Ups for some reason I couldn\'t start the grabber')
      });
    };

    $scope.delete = function(grabber){
      console.log("Deleting Grabber: "+grabber.name);
      console.log(grabber);

      var req = {
        method: 'DELETE',
        url: 'http://localhost:5000/grabber',
        headers: {
          'Content-Type': "application/json"
        },
        data: grabber
      };

      $http(req).then(function successCallback(response) {
        console.log(response);
        $scope.getAll();
      }, function errorCallback(response) {
        console.log('Ups for some reason I couldn\'t delete the grabber')
      });

    };


    $scope.showGrb = function(){
       console.log($scope.grabbers);
    };


  });
