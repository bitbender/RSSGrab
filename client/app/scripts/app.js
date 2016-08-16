'use strict';

/**
 * @ngdoc overview
 * @name yapp
 * @description
 * # yapp
 *
 * Main module of the application.
 */
var app = angular
  .module('yapp', [
    'ui.bootstrap',
    'ui.router',
    'ngAnimate',
    'ngDialog',
    'angularUtils.directives.dirPagination',
    'satellizer'
  ]);

app.constant("moment", moment);

app.config(function ($stateProvider, $urlRouterProvider, $authProvider) {

  $authProvider.baseUrl = 'http://localhost:5000/';

  $urlRouterProvider.when('/dashboard', '/dashboard/overview');
  $urlRouterProvider.otherwise('/login');

  $stateProvider
    .state('base', {
      abstract: true,
      url: '',
      templateUrl: 'views/base.html'
    })
    .state('login', {
      url: '/login',
      parent: 'base',
      templateUrl: 'views/login.html',
      controller: 'LoginCtrl'
    })
    .state('dashboard', {
      url: '/dashboard',
      parent: 'base',
      templateUrl: 'views/dashboard.html',
      controller: 'DashboardCtrl'
    })
    .state('overview', {
      url: '/overview',
      parent: 'dashboard',
      templateUrl: 'views/dashboard/overview.html'
    })
    .state('grabber', {
      url: '/grabber',
      parent: 'dashboard',
      templateUrl: 'views/dashboard/grabbers.html',
      controller: 'GrabberCtrl'
    })
    .state('admin', {
      url: '/admin',
      parent: 'dashboard',
      templateUrl: 'views/dashboard/admin.html',
      controller: 'AdminCtrl'
    })
    .state('stats', {
      url: '/stats/:grabberID',
      parent: 'dashboard',
      templateUrl: 'views/dashboard/stats.html',
      controller: 'StatsCtrl'
    })
    .state('database', {
      url: '/database',
      parent: 'admin',
      templateUrl: "views/partials/database.html",
      controller: 'AdminCtrl'
    })
    .state('task', {
      url: '/task',
      parent: 'admin',
      templateUrl: "views/partials/task.html",
      controller: 'TaskCtrl'
    });
});

app.filter('duration', function() {
  return function(input) {
    var h = Math.floor(input/3600);
    var m = Math.floor((input-(h*3600))/60);
    var s = input-(h*3600+m*60);

    var result = '';

    if(m == 0 && s == 0){
      result = result + h + ' h'
    }
    else if(h == 0 && s == 0){
      result = result + m + ' min'
    }
    else if(h == 0 && m == 0){
      result = result + s + ' sec'
    }else{
      // add hours
      if(h < 10){
        result = result + '0' + h + ':'
      }else{
        result = result + h + ':'
      }

      // add minutes
      if(m < 10){
        result = result + '0' + m + ':'
      }else{
        result = result + m + ':'
      }

      // add seconds
      if(s < 10){
        result = result + '0' + s
      }else{
        result = result + s
      }
    }

    return result
  };
});
