'use strict';

/**
 * @ngdoc overview
 * @name yapp
 * @description
 * # yapp
 *
 * Main module of the application.
 */
angular
  .module('yapp', [
    'ui.router',
    'ngAnimate',
    'ngDialog'
  ])
  .config(function ($stateProvider, $urlRouterProvider) {

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
