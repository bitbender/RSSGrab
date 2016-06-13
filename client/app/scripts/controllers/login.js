'use strict';

/**
 * @ngdoc function
 * @name yapp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of yapp
 */
angular.module('yapp')
  .controller('LoginCtrl', function($scope, $auth, $log, $location) {

    // $scope.submit = function() {
    //
    //   $location.path('/dashboard');
    //
    //   return false;
    // }
    $scope.authenticate = function(provider){
      $auth.authenticate(provider);
    };

    $scope.login = function () {
      $auth
        .login({email: $scope.email, password: $scope.password})
        .then(function (response) {
          $auth.setToken(response);
          $scope.loginErr = false;
          $location.path('/dashboard');
        })
        .catch(function (response) {
          $scope.loginErr = true;
          console.log("Email or password incorrect!");
        })
    };


  });
