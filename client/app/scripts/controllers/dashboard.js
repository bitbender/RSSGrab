'use strict';

/**
 * @ngdoc function
 * @name yapp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of yapp
 */
angular.module('yapp')
  .controller('DashboardCtrl', function($scope, $state, $auth, $log, $location) {
    $scope.$state = $state;

    if (!$auth.isAuthenticated()) { return; }

    $scope.logout = function () {
      $auth.logout()
        .then(function() {
          $log.info('You have been logged out');
          $location.path('/login');
        })
        .catch(function (response) {
          $log.error("An error occurred during logout!");
        })
    };
  });
