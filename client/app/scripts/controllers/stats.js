'use strict';

/**
 * @ngdoc function
 * @name yapp.controller:AdminCtrl
 * @description
 * # AdminCtrl
 * Controller of admin
 */
angular.module('yapp')
  .controller('StatsCtrl', function ($scope, $state, $stateParams, ngDialog, $http, __env) {

    // This controls the sorting of the table
    $scope.sortType     = 'start'; // set the default sort type
    $scope.sortReverse  = false;  // set the default sort order
    $scope.grabber = {};

    $scope.retrieveGrabber = function(id){

      var req = {
        method: 'GET',
        url: __env.apiUrl+'grabber/'+id,
        headers: {
          'Content-Type': "application/json"
        }
      };

      $http(req).then(function successCallback(response) {
        console.log(response.data);
        $scope.grabber = response.data;
        $scope.retrieveStatistics()
      }, function errorCallback(response) {
        console.log('Ups for some reason I couldn\'t start the grabber')
      });
    };

    $scope.retrieveStatistics = function(){

      var req = {
        method: 'POST',
        url: __env.apiUrl+'grabber/stats/50',
        headers: {
          'Content-Type': "application/json"
        },
        data: $scope.grabber
      };

      $http(req).then(function successCallback(response) {
        console.log(response.data);
        $scope.stats = response.data;
      }, function errorCallback(response) {
        console.log('Ups for some reason I couldn\'t start the grabber')
      });
    };

    $scope.showNewUrls = function (stat) {
      ngDialog.open({
        plain:true,
        template: '<h1>New URLs</h1><ol><li ng-repeat="url in stat.new"><a href="{{ url }}">{{ url }}</a></li></ol><a class="btn btn-primary btn-sm btn-outline btn-rounded" ng-click="closeThisDialog()">Close</a>',
        //template: '../../views/partials/show_urls.html',
        controller: function ($scope) { $scope.stat = $scope.ngDialogData;},
        data: stat
      }).closePromise.then(function (data) {
        console.log(data.id + ' has been dismissed.');
      });
    };

    $scope.showPayedUrls = function (stat) {
      ngDialog.open({
        plain:true,
        template: '<h1>Payed URLs</h1><ol><li ng-repeat="url in stat.payed"><a href="{{ url }}">{{ url }}</a></li></ol><a class="btn btn-primary btn-sm btn-outline btn-rounded" ng-click="closeThisDialog()">Close</a>',
        //template: '../../views/partials/show_urls.html',
        controller: function ($scope) { $scope.stat = $scope.ngDialogData;},
        data: stat
      }).closePromise.then(function (data) {
        console.log(data.id + ' has been dismissed.');
      });
    };

    $scope.showUpdatedUrls = function (stat) {
      ngDialog.open({
        plain:true,
        template: '<h1>Updated URLs</h1><ol><li ng-repeat="url in stat.updated"><a href="{{ url }}">{{ url }}</a></li></ol><a class="btn btn-primary btn-sm btn-outline btn-rounded" ng-click="closeThisDialog()">Close</a>',
        //template: '../../views/partials/show_urls.html',
        controller: function ($scope) { $scope.stat = $scope.ngDialogData;},
        data: stat
      }).closePromise.then(function (data) {
        console.log(data.id + ' has been dismissed.');
      });
    };

    $scope.retrieveGrabber($stateParams.grabberID);

    $scope.printGrabber = function(){
      console.log($scope.grabber)
    };
  });
